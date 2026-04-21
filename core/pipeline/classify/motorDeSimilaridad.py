import json
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import os

# 1. Configuración del Modelo de Embeddings
model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
huggingface_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)

# 2. Inicializar ChromaDB
client = chromadb.PersistentClient(path="./data/processed/chroma_db")

collection = client.get_or_create_collection(
    name="clausulas_referencia",
    embedding_function=huggingface_ef,
    metadata={"hnsw:space": "cosine"}
)

# 3. Función de Indexación (MODIFICADA para incluir justificación)
def indexar_diccionario(ruta_json):
    if collection.count() == 0:
        print("📥 Indexando diccionario en ChromaDB por primera vez...")
        with open(ruta_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        ids, documents, metadatos = [], [], []
        
        idx = 0
        for cat, subs in data.items():
            for sub, info in subs.items():
                ids.append(f"id_{idx}")
                documents.append(info['ejemplo'])
                # Añadimos 'justificacion' a los metadatos
                metadatos.append({
                    "categoria": cat,
                    "subcategoria": sub,
                    "es_legal": info['valor'],
                    "justificacion": info.get('explicacion', "Sin justificación disponible")
                })
                idx += 1
        
        collection.add(ids=ids, documents=documents, metadatas=metadatos)
        print(f"✅ {idx} ejemplos indexados con sus justificaciones.")
    else:
        # NOTA: Si ya habías indexado antes sin justificación, 
        # deberás borrar la carpeta chroma_db para que se vuelva a indexar con los nuevos metadatos.
        print(f"💾 Usando base de datos persistente ({collection.count()} registros).")

# 4. Lógica de Análisis (MODIFICADA para recuperar justificación)
def analizar_con_chroma(texto_usuario):
    results = collection.query(
        query_texts=[texto_usuario],
        n_results=1,
        include=['metadatas', 'distances', 'documents']
    )
    
    distancia = results['distances'][0][0]
    confianza = 1 - distancia
    metadata = results['metadatas'][0][0]
    texto_ref = results['documents'][0][0]
    justificacion = metadata.get('justificacion', "N/A")
    
    return confianza, metadata['es_legal'], texto_ref, justificacion

# --- EJECUCIÓN ---

indexar_diccionario('data/dictionaries/clausulas.json')

df_contrato = pd.read_csv("data/outputs/clausulas_contrato.csv")

UMBRAL_LEGAL = 0.50
UMBRAL_ABUSIVO = 0.80

resultados = []
print("\n🚀 Analizando contrato con ChromaDB y generando justificaciones...")

for _, row in df_contrato.iterrows():
    score, es_legal_ref, ref_txt, por_que = analizar_con_chroma(row['contenido'])
    
    if es_legal_ref:
        dictamen = "✅ LEGAL" if score >= UMBRAL_LEGAL else "🔍 REVISIÓN (Baja confianza)"
        # Si es legal, la justificación suele ser informativa
        razon = "La cláusula se ajusta a los estándares legales de referencia."
    else:
        if score >= UMBRAL_ABUSIVO:
            dictamen = "⚠️ POSIBLE ABUSIVA"
            razon = por_que
        elif score >= UMBRAL_LEGAL:
            dictamen = "🔍 REVISIÓN (Sospecha leve)"
            razon = f"Posible conflicto: {por_que}"
        else:
            dictamen = "✅ LEGAL (Probable)"
            razon = "No se detectaron patrones de abusividad claros."

    resultados.append({
        "Cláusula": row['titulo'],
        "Dictamen": dictamen,
        "Confianza": f"{score:.2%}",
        "Referencia": ref_txt[:40] + "...",
        "Justificación": razon
    })

# Guardar y mostrar
df_final = pd.DataFrame(resultados)
print("\n" + "="*80)
# Mostramos la columna Justificación en el print para verificar
print(df_final[['Cláusula', 'Dictamen', 'Justificación']])
print("="*80)

df_final.to_csv("data/outputs/prediccionAbusividad.csv", index=False, encoding="utf-8")
print("\n✅ Análisis completo guardado en 'data/outputs/prediccionAbusividad.csv'")