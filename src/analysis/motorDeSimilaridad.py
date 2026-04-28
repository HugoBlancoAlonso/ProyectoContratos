import json
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ======================================================
# CONFIGURACIÓN MODELO EMBEDDINGS
# ======================================================

model_name = "paraphrase-multilingual-MiniLM-L12-v2"

huggingface_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=model_name
)

# ======================================================
# INICIALIZAR CHROMADB
# ======================================================

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="clausulas_referencia",
    embedding_function=huggingface_ef,
    metadata={"hnsw:space": "cosine"}
)

# ======================================================
# INDEXAR DICCIONARIO LEGAL
# ======================================================

def indexar_diccionario(ruta_json):

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
                    "justificacion": info.get(
                        "explicacion",
                        "Sin justificación disponible"
                    )
                })

                idx += 1

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatos
        )

        print(f"✅ {idx} ejemplos indexados correctamente.")

    else:

        print(
            f"💾 Base persistente detectada "
            f"({collection.count()} registros)."
        )

# ======================================================
# ANALIZAR TEXTO CONTRA BASE VECTORIAL
# ======================================================

def analizar_con_chroma(texto_usuario):

    results = collection.query(
        query_texts=[texto_usuario],
        n_results=1,
        include=["metadatas", "distances", "documents"]
    )

    distancia = results["distances"][0][0]
    confianza = 1 - distancia

    metadata = results["metadatas"][0][0]
    texto_ref = results["documents"][0][0]

    justificacion = metadata.get(
        "justificacion",
        "Sin información adicional"
    )

    return (
        confianza,
        metadata["es_legal"],
        texto_ref,
        justificacion
    )

# ======================================================
# EJECUCIÓN PRINCIPAL
# ======================================================

indexar_diccionario("data/clausulas.json")

df_contrato = pd.read_csv(
    "data/contratosParaAnalizar/clausulas_contrato.csv"
)

UMBRAL_LEGAL = 0.50
UMBRAL_ABUSIVO = 0.80

resultados = []

print("\n🚀 Analizando contrato...")

for _, row in df_contrato.iterrows():

    score, es_legal_ref, ref_txt, motivo = analizar_con_chroma(
        row["contenido"]
    )

    # --------------------------------------------------
    # DECISIÓN FINAL
    # --------------------------------------------------

    if es_legal_ref:

        if score >= UMBRAL_LEGAL:
            dictamen = "✅ LEGAL"
            razon = (
                "La cláusula coincide con patrones legales válidos."
            )
        else:
            dictamen = "🔍 REVISIÓN (Coincidencia moderada)"
            razon = (
                "Se recomienda revisión manual por similitud parcial."
            )

    else:

        if score >= UMBRAL_ABUSIVO:
            dictamen = "⚠️ POSIBLE ABUSIVA"
            razon = motivo

        elif score >= UMBRAL_LEGAL:
            dictamen = "🔍 REVISIÓN (Sospecha leve)"
            razon = f"Posible conflicto: {motivo}"

        else:
            dictamen = "✅ LEGAL (Probable)"
            razon = (
                "No se detectaron patrones claros de abusividad."
            )

    resultados.append({
        "Cláusula": row["titulo"],
        "Dictamen": dictamen,
        "Confianza": f"{score:.2%}",
        "Referencia": ref_txt[:40] + "...",
        "Justificación": razon
    })

# ======================================================
# EXPORTAR RESULTADOS
# ======================================================

df_final = pd.DataFrame(resultados)

print("\n" + "=" * 80)
print(df_final[["Cláusula", "Dictamen", "Justificación"]])
print("=" * 80)

df_final.to_csv(
    "data/prediccionAbusividad.csv",
    index=False,
    encoding="utf-8"
)

print(
    "\n✅ Análisis completo guardado en "
    "'data/prediccionAbusividad.csv'"
)