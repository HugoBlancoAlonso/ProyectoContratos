import chromadb
import json

# 1. Cargar tu JSON
with open('data/clausulas_finales.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

client = chromadb.PersistentClient(path="./clausulas_db")
collection = client.get_or_create_collection(name="vivienda_clausulas")

# 2. Recorrer el JSON anidado
documentos = []
metadatos = []
ids = []

contador = 0
for categoria, subdict in data.items():
    for nombre_regla, contenido in subdict.items():
        # Extraemos la info
        texto_ejemplo = contenido['ejemplo']
        es_legal = contenido['valor'] # True = Legal, False = Abusiva

        documentos.append(texto_ejemplo)
        metadatos.append({
            "categoria": categoria,
            "regla": nombre_regla,
            "es_legal": str(es_legal)
        })
        ids.append(f"id_{contador}")
        contador += 1

# 3. Guardar en ChromaDB
collection.add(
    documents=documentos,
    metadatas=metadatos,
    ids=ids
)

print(f"¡Base de datos lista con {contador} ejemplos de vivienda!")