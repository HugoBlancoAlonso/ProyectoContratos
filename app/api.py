from fastapi import FastAPI, UploadFile, File, HTTPException
from contextlib import asynccontextmanager
import shutil
import pandas as pd
import os
import json
import re
import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
import sys
from datetime import datetime

# ======================================================
# CONFIGURACIÓN DE SALIDA UTF-8
# ======================================================
sys.stdout.reconfigure(encoding="utf-8")

# ======================================================
# ESTADO GLOBAL DE LA APLICACIÓN
# ======================================================
app_state = {
    "chroma_client": None,
    "collection": None,
    "embedding_function": None,
    "modelo_cargado": False,
    "tiempo_inicio": None
}


# ======================================================
# FUNCIONES DE PROCESAMIENTO
# ======================================================

def unir_titulo_con_subclausula(texto_pagina):
    """Une títulos partidos con subcláusulas"""
    lineas = texto_pagina.splitlines()
    lineas = [l.strip() for l in lineas if l.strip()]

    resultado = []
    i = 0

    while i < len(lineas):
        actual = lineas[i]
        siguiente = lineas[i + 1] if i + 1 < len(lineas) else ""

        es_titulo = re.match(r"(?i)^cl[áa]usula\s+.+$", actual)
        es_subtitulo = re.match(r"^\d+(\.\d+)*\b", siguiente)

        if es_titulo and es_subtitulo:
            resultado.append(f"{actual} {siguiente}")
            i += 2
            continue

        resultado.append(actual)
        i += 1

    return "\n".join(resultado)


def extraer_texto_legal_pro(ruta_pdf):
    """Extrae texto limpio de un PDF"""
    try:
        doc = fitz.open(ruta_pdf)
        texto_final = []

        for pagina in doc:
            dict_pag = pagina.get_text("dict")

            # Detectar tamaño fuente dominante
            tamanos = []
            for bloque in dict_pag["blocks"]:
                if "lines" in bloque:
                    for linea in bloque["lines"]:
                        for span in linea["spans"]:
                            if span["text"].strip():
                                tamanos.append(round(span["size"], 1))

            if not tamanos:
                continue

            fuente_principal = max(set(tamanos), key=tamanos.count)
            texto_pagina = ""

            # Filtrar superíndices / notas pie
            for bloque in dict_pag["blocks"]:
                if "lines" in bloque:
                    for linea in bloque["lines"]:
                        linea_texto = ""
                        for span in linea["spans"]:
                            if span["size"] >= (fuente_principal * 0.95):
                                linea_texto += span["text"]
                        texto_pagina += linea_texto + " "
                    texto_pagina += "\n"

            # Limpieza regex
            texto_pagina = re.sub(r"(?i)p[áa]gina\s+\d+\s+de\s+\d+", "", texto_pagina)
            texto_pagina = re.sub(r"[ ]{2,}", " ", texto_pagina)
            texto_pagina = re.sub(r"\n{2,}", "\n", texto_pagina)
            texto_pagina = unir_titulo_con_subclausula(texto_pagina)
            texto_final.append(texto_pagina)

        resultado = "\n".join(texto_final)
        resultado = re.sub(r"\n{3,}", "\n\n", resultado).strip()

        return resultado

    except Exception as e:
        raise Exception(f"Error en extracción: {e}")


def segmentar_clausulas(texto, nombre_archivo="contrato_01"):
    """Segmenta el texto en cláusulas individuales"""
    patron = r"(Primera|Segunda|Tercera|Cuarta|Quinta|Sexta|Séptima|Octava|Novena|Décima|Undécima|Duodécima|Décimo\s+primera|Décimo\s+segunda|Décimo\s+tercera|Décimo\s+cuarta|Décimo\s+quinta|Décimo\s+sexta|Décimo\s+séptima|Décimo\s+octava|Décimo\s+novena|Vigésima|Vigésimo\s+primera|Vigésimo\s+segunda|Vigésimo\s+tercera|Vigésimo\s+cuarta|Vigésimo\s+quinta)\."

    matches = list(re.finditer(patron, texto, re.IGNORECASE | re.VERBOSE))

    clausulas = []

    if len(matches) == 0:
        clausulas.append({
            "contrato_id": nombre_archivo,
            "titulo": "CONTRATO_COMPLETO",
            "contenido": texto,
            "longitud": len(texto)
        })
        return clausulas

    for i in range(len(matches)):
        inicio = matches[i].start()
        titulo = matches[i].group().strip()
        fin = matches[i + 1].start() if i + 1 < len(matches) else len(texto)
        contenido = texto[inicio:fin].strip()
        contenido = re.sub(r"\s+", " ", contenido)

        clausulas.append({
            "contrato_id": nombre_archivo,
            "titulo": titulo,
            "contenido": contenido,
            "longitud": len(contenido)
        })

    return clausulas


def analizar_con_chroma(texto_usuario, collection):
    """Analiza un texto contra la base vectorial de ChromaDB"""
    results = collection.query(
        query_texts=[texto_usuario],
        n_results=1,
        include=["metadatas", "distances", "documents"]
    )

    distancia = results["distances"][0][0]
    confianza = 1 - distancia
    metadata = results["metadatas"][0][0]
    texto_ref = results["documents"][0][0]
    justificacion = metadata.get("justificacion", "Sin información adicional")

    return confianza, metadata["es_legal"], texto_ref, justificacion


def indexar_diccionario(ruta_json, collection):
    """Indexa el diccionario legal en ChromaDB (solo si no está indexado)"""
    if collection.count() == 0:
        print("📥 Indexando diccionario en ChromaDB por primera vez...")

        with open(ruta_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        ids = []
        documents = []
        metadatos = []
        idx = 0

        for categoria, subcategorias in data.items():
            for subcategoria, info in subcategorias.items():
                ids.append(f"id_{idx}")
                documents.append(info["ejemplo"])
                metadatos.append({
                    "categoria": categoria,
                    "subcategoria": subcategoria,
                    "es_legal": info["valor"],
                    "justificacion": info.get("explicacion", "Sin justificación disponible")
                })
                idx += 1

        collection.add(ids=ids, documents=documents, metadatas=metadatos)
        print(f"✅ {idx} ejemplos indexados correctamente.")
    else:
        print(f"💾 Base persistente detectada ({collection.count()} registros).")


# ======================================================
# CICLO DE VIDA DE LA APLICACIÓN
# ======================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicia los modelos al arrancar y libera recursos al terminar"""
    
    print("\n🚀 Inicializando API...")
    
    # STARTUP
    try:
        # Cargar modelo de embeddings
        model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        
        # Inicializar ChromaDB
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_or_create_collection(
            name="clausulas_referencia",
            embedding_function=embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Indexar diccionario
        indexar_diccionario("data/clausulas.json", collection)
        
        # Guardar en estado global
        app_state["chroma_client"] = chroma_client
        app_state["collection"] = collection
        app_state["embedding_function"] = embedding_function
        app_state["modelo_cargado"] = True
        app_state["tiempo_inicio"] = datetime.now()
        
        print("✅ API lista para recibir peticiones\n")
        
    except Exception as e:
        print(f"❌ Error al inicializar: {e}")
        app_state["modelo_cargado"] = False
    
    yield  # La aplicación corre aquí
    
    # SHUTDOWN
    print("\n🛑 Cerrando API...")
    app_state["modelo_cargado"] = False
    print("✅ API cerrada correctamente")


# ======================================================
# CREAR APLICACIÓN FASTAPI
# ======================================================

app = FastAPI(
    title="API Analizador de Contratos",
    description="Sistema NLP para análisis automático de contratos - Modelos en memoria",
    version="2.0",
    lifespan=lifespan
)


# ======================================================
# ENDPOINTS
# ======================================================

@app.get("/")
def home():
    """Endpoint raíz"""
    return {
        "nombre": "API Analizador de Contratos",
        "version": "2.0",
        "estado": "modelos cargados" if app_state["modelo_cargado"] else "modelos no cargados",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "status": "/status",
            "analizar": "/analizar (POST)"
        }
    }


@app.get("/health")
def health_check():
    """Verifica que la API esté operativa"""
    return {
        "status": "ok",
        "modelos_cargados": app_state["modelo_cargado"],
        "tiempo_uptime": (datetime.now() - app_state["tiempo_inicio"]).total_seconds() if app_state["tiempo_inicio"] else 0
    }


@app.get("/status")
def status():
    """Información detallada del estado del sistema"""
    return {
        "api_status": "healthy" if app_state["modelo_cargado"] else "unhealthy",
        "modelos_cargados": app_state["modelo_cargado"],
        "chroma_db_conectado": app_state["collection"] is not None,
        "clausulas_indexadas": app_state["collection"].count() if app_state["collection"] else 0,
        "tiempo_uptime_segundos": (datetime.now() - app_state["tiempo_inicio"]).total_seconds() if app_state["tiempo_inicio"] else 0,
        "hora_inicio": app_state["tiempo_inicio"].isoformat() if app_state["tiempo_inicio"] else None
    }


@app.post("/analizar")
async def analizar_contrato(file: UploadFile = File(...)):
    """Analiza un contrato PDF subido"""
    
    if not app_state["modelo_cargado"]:
        raise HTTPException(
            status_code=503,
            detail="Modelos no están cargados. Por favor, reinicia la API."
        )
    
    try:
        # Crear carpeta si no existe
        os.makedirs("data/contratosParaAnalizar", exist_ok=True)
        
        # Guardar PDF
        ruta_pdf = "data/contratosParaAnalizar/contrato.pdf"
        with open(ruta_pdf, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"\n📄 Analizando archivo: {file.filename}")
        
        # PASO 1: Extracción de texto
        print("   1️⃣  Extrayendo texto...")
        texto_limpio = extraer_texto_legal_pro(ruta_pdf)
        
        # Guardar texto limpio
        ruta_limpio = "data/contratosParaAnalizar/contrato_limpio.txt"
        with open(ruta_limpio, "w", encoding="utf-8") as f:
            f.write(texto_limpio)
        
        # PASO 2: Segmentación de cláusulas
        print("   2️⃣  Segmentando cláusulas...")
        clausulas = segmentar_clausulas(texto_limpio)
        
        # PASO 3: Análisis con ChromaDB
        print("   3️⃣  Analizando con ChromaDB...")
        
        UMBRAL_LEGAL = 0.50
        UMBRAL_ABUSIVO = 0.80
        resultados = []
        
        for clausula in clausulas:
            score, es_legal_ref, ref_txt, motivo = analizar_con_chroma(
                clausula["contenido"],
                app_state["collection"]
            )
            
            # Decisión final
            if es_legal_ref:
                if score >= UMBRAL_LEGAL:
                    dictamen = "✅ LEGAL"
                    razon = "La cláusula coincide con patrones legales válidos."
                else:
                    dictamen = "🔍 REVISIÓN (Coincidencia moderada)"
                    razon = "Se recomienda revisión manual por similitud parcial."
            else:
                if score >= UMBRAL_ABUSIVO:
                    dictamen = "⚠️ POSIBLE ABUSIVA"
                    razon = motivo
                elif score >= UMBRAL_LEGAL:
                    dictamen = "🔍 REVISIÓN (Sospecha leve)"
                    razon = f"Posible conflicto: {motivo}"
                else:
                    dictamen = "✅ LEGAL (Probable)"
                    razon = "No se detectaron patrones claros de abusividad."
            
            resultados.append({
                "clausula": clausula["titulo"],
                "contenido": clausula["contenido"][:100] + "..." if len(clausula["contenido"]) > 100 else clausula["contenido"],
                "dictamen": dictamen,
                "confianza": f"{score:.2%}",
                "referencia": ref_txt[:50] + "..." if len(ref_txt) > 50 else ref_txt,
                "justificacion": razon,
                "longitud_original": clausula["longitud"]
            })
        
        # Guardar resultados en CSV
        df_resultados = pd.DataFrame(resultados)
        ruta_csv = "data/prediccionAbusividad.csv"
        df_resultados.to_csv(ruta_csv, index=False, encoding="utf-8")
        
        print(f"   ✅ Análisis completado: {len(resultados)} cláusulas procesadas")
        
        return {
            "estado": "exito",
            "archivo": file.filename,
            "clausulas_procesadas": len(resultados),
            "timestamp": datetime.now().isoformat(),
            "resultados": resultados
        }
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando contrato: {str(e)}"
        )


# ======================================================
# EJECUCIÓN
# ======================================================
# uvicorn app.api:app --reload --host 0.0.0.0 --port 8000