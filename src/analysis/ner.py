import spacy
from spacy.matcher import Matcher
from collections import Counter
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ======================================================
# CARGA MODELO SPACY
# ======================================================

try:
    nlp = spacy.load("es_core_news_sm")

except Exception:
    print(
        "Error: instala el modelo ejecutando:\n"
        "python -m spacy download es_core_news_sm"
    )
    nlp = spacy.blank("es")

matcher = Matcher(nlp.vocab)

# ======================================================
# PATRONES NLP JURÍDICOS
# ======================================================

# ------------------------------------------------------
# 1. AMOUNT (Cuantías)
# Ej:
# 950 euros
# 1.000 €
# 1200 eur
# ------------------------------------------------------

patron_monto = [
    {"LIKE_NUM": True},
    {"LOWER": {"IN": ["euros", "€", "eur"]}}
]

# ------------------------------------------------------
# 2. DURATION (Duración)
# Ej:
# un año
# cinco años
# 6 meses
# treinta días
# ------------------------------------------------------

patron_duracion = [
    {"LIKE_NUM": True, "OP": "?"},
    {
        "LOWER": {
            "IN": [
                "un", "una", "dos", "tres",
                "cinco", "seis", "doce",
                "treinta"
            ]
        },
        "OP": "?"
    },
    {
        "LOWER": {
            "IN": [
                "mes", "meses",
                "año", "años",
                "día", "días",
                "anual", "anuales"
            ]
        }
    }
]

# ------------------------------------------------------
# 3. JURISDICTION
# Ej:
# jurisdicción ordinaria
# juzgados de Madrid
# tribunales de Valencia
# ------------------------------------------------------

patron_juris_1 = [
    {"LOWER": "jurisdicción"},
    {"LOWER": "ordinaria"}
]

patron_juris_2 = [
    {"LOWER": {"IN": ["juzgados", "tribunales"]}},
    {"LOWER": "de"},
    {"IS_TITLE": True}
]

# ------------------------------------------------------
# 4. PARTY (Partes)
# Ej:
# arrendador
# arrendatario
# arrendataria
# propietario
# inquilino
# ------------------------------------------------------

patron_partes = [
    {
        "LOWER": {
            "IN": [
                "arrendador",
                "arrendatario",
                "arrendataria",
                "propietario",
                "inquilino"
            ]
        }
    }
]

# ======================================================
# REGISTRO DE PATRONES
# ======================================================

matcher.add("AMOUNT", [patron_monto])
matcher.add("DURATION", [patron_duracion])
matcher.add("JURISDICTION", [patron_juris_1, patron_juris_2])
matcher.add("PARTY", [patron_partes])

# ======================================================
# FUNCIÓN PRINCIPAL
# ======================================================

def pre_anotar(texto):

    doc = nlp(texto)
    matches = matcher(doc)

    anotaciones = []

    for match_id, start, end in matches:

        span = doc[start:end]

        anotaciones.append({
            "start": span.start_char,
            "end": span.end_char,
            "label": nlp.vocab.strings[match_id],
            "text": span.text.strip()
        })

    return {"label": anotaciones}

# ======================================================
# EJECUCIÓN
# ======================================================

ruta_archivo = "data/contratosParaAnalizar/contrato_limpio.txt"

try:

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    resultado = pre_anotar(contenido)

    resumen = Counter(
        [item["label"] for item in resultado["label"]]
    )

    print("📌 Resumen de entidades detectadas:")
    print(dict(resumen))

    print("\n📄 Resultado detallado:\n")

    print(
        json.dumps(
            resultado,
            indent=4,
            ensure_ascii=False
        )
    )

except Exception as e:

    print(f"❌ Error en NER: {e}")