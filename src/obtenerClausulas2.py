import fitz
import json
import re
import chromadb
from transformers import pipeline
from sentence_transformers import SentenceTransformer

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

with open('data/clausulas_finales.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

client = chromadb.PersistentClient(path="./clausulas_db")
collection = client.get_or_create_collection(name="vivienda_clausulas")

documentos = []
metadatos = []
ids = []

contador = 0
for categoria, subdict in data.items():
    for nombre_regla, contenido in subdict.items():
        documentos.append(contenido['ejemplo'])
        metadatos.append({
            "categoria": categoria,
            "regla": nombre_regla,
            "es_legal": str(contenido['valor'])
        })
        ids.append(f"id_{contador}")
        contador += 1

collection.add(documents=documentos, metadatas=metadatos, ids=ids)

print(f"Base de datos cargada con {contador} cláusulas")


def extraer_texto_pdf(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text("text") + "\n"
    return texto


def limpiar_texto(texto):
    if "CLAUSULAS" in texto:
        texto = texto.split("CLAUSULAS", 1)[1]

    texto = re.sub(r'\n+', '\n', texto)
    texto = re.sub(r'\n\d+\s*\n', '\n', texto)
    texto = re.sub(r'\d{1,2}\s+', '', texto)
    texto = re.sub(r'\s+', ' ', texto)

    return texto


def segmentar_clausulas(texto):
    texto = texto.replace("\r", "\n")

    # 1. Por numeración (1., 2., etc.)
    partes = re.split(r'\n\s*(\d{1,2}\.\s+)', texto)

    clausulas = []
    buffer = ""

    for parte in partes:
        if re.match(r'\d{1,2}\.\s+', parte):
            if buffer:
                clausulas.append(buffer.strip())
            buffer = parte
        else:
            buffer += " " + parte

    if buffer:
        clausulas.append(buffer.strip())

    # 2. Por palabras tipo PRIMERA, SEGUNDA...
    if len(clausulas) <= 2:
        partes = re.split(
            r'(PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|SÉPTIMA|OCTAVA|NOVENA|DÉCIMA)',
            texto,
            flags=re.IGNORECASE
        )

        clausulas = []
        buffer = ""

        for parte in partes:
            if re.match(r'(PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|SÉPTIMA|OCTAVA|NOVENA|DÉCIMA)', parte, re.IGNORECASE):
                if buffer:
                    clausulas.append(buffer.strip())
                buffer = parte
            else:
                buffer += " " + parte

        if buffer:
            clausulas.append(buffer.strip())

    # 3. Fallback (bloques grandes)
    if len(clausulas) <= 2:
        clausulas = re.split(r'\n{2,}', texto)

    clausulas = [c.strip() for c in clausulas if len(c.strip()) > 200]

    return clausulas


def detectar_abusividad(texto, collection, top_k=5, threshold=0.6):
    embedding = embedding_model.encode(texto).tolist()

    resultados = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    docs = resultados['documents'][0]
    metas = resultados['metadatas'][0]

    votos_abusiva = 0
    evidencia = []

    for doc, meta in zip(docs, metas):
        if meta['es_legal'] == "False":
            votos_abusiva += 1
            evidencia.append(doc)

    score = votos_abusiva / len(metas)

    texto_lower = texto.lower()

    patrones_abusivos = [
        "sin derecho a indemnización",
        "a discreción del arrendador",
        "en cualquier momento",
        "sin necesidad de justificar",
        "no estará sujeto a prórrogas legales",
        "el arrendatario no podrá desistir"
    ]

    patron_detectado = any(p in texto_lower for p in patrones_abusivos)


    es_abusiva = (
        score >= threshold
        or (patron_detectado and score >= (threshold - 0.2))
    )

    return {
        "es_abusiva": es_abusiva,
        "score_abusividad": round(score, 2),
        "ejemplos_similares": evidencia[:2] if es_abusiva else []
    }


def analizar_contrato(ruta_pdf):
    texto = extraer_texto_pdf(ruta_pdf)
    texto = limpiar_texto(texto)

    clausulas = segmentar_clausulas(texto)

    print(f"Cláusulas detectadas: {len(clausulas)}")

    resultado = {
        "archivo": ruta_pdf,
        "total_clausulas": len(clausulas),
        "clausulas": []
    }

    for clausula in clausulas:

        # evitar bloques demasiado grandes (ruido)
        if len(clausula) > 2000:
            continue

        clasificacion = classifier(
            clausula,
            candidate_labels=["cláusula contractual", "información general"],
            hypothesis_template="Este texto es una {}"
        )

        categoria = clasificacion['labels'][0]
        confianza = clasificacion['scores'][0]

        analisis = detectar_abusividad(clausula, collection)

        resultado["clausulas"].append({
            "id": len(resultado["clausulas"]) + 1,
            "texto": clausula,
            "categoria": categoria,
            "confianza_ia": round(confianza, 2),
            "es_abusiva": analisis["es_abusiva"],
            "score_abusividad": analisis["score_abusividad"],
            "ejemplos": analisis["ejemplos_similares"] if analisis["es_abusiva"] else []
        })

    return resultado


ruta_pdf = "data/contratoPrueba.pdf"

resultado_final = analizar_contrato(ruta_pdf)

with open("resultado_final.json", "w", encoding="utf-8") as f:
    json.dump(resultado_final, f, indent=4, ensure_ascii=False)

print("\nAnálisis completo terminado")

for c in resultado_final["clausulas"]:
    print("\n==============================")
    print(f"CLÁUSULA {c['id']}")
    print(f"Tipo: {c['categoria']} ({c['confianza_ia']})")
    print(f"Abusiva: {c['es_abusiva']} | Score: {c['score_abusividad']}")
    print("\nTEXTO:")
    print(c["texto"])

    if c["es_abusiva"]:
        print("\nEjemplos similares:")
        for e in c["ejemplos"]:
            print("-", e)