import spacy
from spacy.matcher import Matcher
import json
import sys
sys.stdout.reconfigure(encoding="utf-8")
# Forzamos la carga del modelo en español para que entienda la gramática
try:
    nlp = spacy.load("es_core_news_sm")
except:
    print("Error: Ejecuta 'python -m spacy download es_core_news_sm' en tu terminal")
    nlp = spacy.blank("es")

matcher = Matcher(nlp.vocab)

# 1. PATRÓN PARA AMOUNT (Cuantías)
# Detecta: "950,00 euros", "950 euros", "1.000 €", "950,00 €"
patron_monto = [
    {"IS_DIGIT": False, "LIKE_NUM": True}, # Captura el número (incluso con comas)
    {"LOWER": {"IN": ["euros", "€", "eur"]}} # Captura la moneda
]

# 2. PATRÓN PARA DURATION (Duración)
# Detecta: "un año", "5 años", "treinta días", "seis meses"
patron_duracion = [
    {"LIKE_NUM": True, "OP": "?"}, 
    {"LOWER": {"IN": ["un", "una", "un", "seis", "doce", "treinta", "cinco"]}, "OP": "?"},
    {"LOWER": {"IN": ["mes", "meses", "año", "años", "día", "días", "anuales"]}}
]

# 3. PATRÓN PARA JURISDICTION
# Detecta: "jurisdicción ordinaria", "juzgados de Madrid"
patron_juris_1 = [{"LOWER": "jurisdicción"}, {"LOWER": "ordinaria"}]
patron_juris_2 = [{"LOWER": "juzgados"}, {"LOWER": "de"}, {"IS_TITLE": True}]

# 4. PATRÓN PARA PARTY (Partes) - Nuevo
# Detecta: "Arrendador", "Arrendatario" cuando aparecen como títulos o roles
patron_partes = [{"LOWER": {"IN": ["arrendador", "arrendataria", "arrendatario"]}}]

matcher.add("AMOUNT", [patron_monto])
matcher.add("DURATION", [patron_duracion])
matcher.add("JURISDICTION", [patron_juris_1, patron_juris_2])
matcher.add("PARTY", [patron_partes])

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

# --- EJECUCIÓN ---
ruta_archivo = "data/contratosParaAnalizar/contrato_limpio.txt"

try:
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()
    
    resultado = pre_anotar(contenido)
    # Mostramos cuántas hemos encontrado de cada una para verificar
    from collections import Counter
    resumen = Counter([a['label'] for a in resultado['label']])
    print(f"Resumen de hallazgos: {dict(resumen)}")
    
    print(json.dumps(resultado, indent=4, ensure_ascii=False))

except Exception as e:
    print(f"Error: {e}")