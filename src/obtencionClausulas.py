import requests
import json
import fitz


def procesar_bloque_llama3(texto_bloque, inicio_id):
    url = "http://localhost:11434/api/generate"
    
    prompt = f"""
    SISTEMA: Eres un extractor de datos especializado en documentos legales. Tu salida debe ser exclusivamente un JSON válido.
    
    INSTRUCCIÓN CLAVE: 
    Cada cláusula debe empezar con su identificador original (ejemplo: "Primera. Regulación", "Segunda.", "1.", etc.). 
    NO elimines el nombre de la cláusula.

    TAREA:
    Extrae el texto ÍNTEGRO de cada cláusula, empezando por su título o número.
    Mantén la numeración de los IDs de la lista empezando en {inicio_id}.
    
    FORMATO OBLIGATORIO DE SALIDA:
    {{
      "clausulas": [
        {{ "id": {inicio_id}, "texto": "Primera. [Título]. [Resto del texto...]" }},
        {{ "id": {inicio_id + 1}, "texto": "Segunda. [Título]. [Resto del texto...]" }}
      ]
    }}

    REGLAS CRÍTICAS:
    1. Incluye el NOMBRE de la cláusula (Primera, Segunda, etc.) dentro del campo "texto".
    2. Ignora el encabezado del contrato (REUNIDOS, EXPONEN) y las notas al pie.
    3. NO incluyas introducciones ni comentarios. Solo el JSON.

    CONTRATO A PROCESAR:
    {texto_bloque}
    """

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1}
    }

    response = requests.post(url, json=payload, timeout=300)
    # Extraemos la lista de la respuesta
    return json.loads(response.json()['response'])['clausulas']

def extraer_todo_el_contrato(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    texto_completo = ""
    for pagina in doc:
        texto_completo += pagina.get_text("text") + "\n"
    
    # Dividir el texto en dos partes
    mitad = len(texto_completo) // 2
    parte1 = texto_completo[:mitad]
    parte2 = texto_completo[mitad:]

    print("🦙 Procesando Parte 1 del contrato...")
    clausulas_p1 = procesar_bloque_llama3(parte1, 1)
    
    # CORRECCIÓN DE ID: Calculamos el siguiente ID real
    siguiente_id = clausulas_p1[-1]['id'] + 1 if clausulas_p1 else 1
    
    print(f"🦙 Procesando Parte 2 (desde ID {siguiente_id})...")
    clausulas_p2 = procesar_bloque_llama3(parte2, siguiente_id)

    resultado_final = {
        "archivo": ruta_pdf.split('/')[-1],
        "total": len(clausulas_p1) + len(clausulas_p2),
        "clausulas": clausulas_p1 + clausulas_p2
    }
    return resultado_final

# --- EJECUCIÓN ---
ruta = "data\contratoPrueba.pdf"
try:
    final = extraer_todo_el_contrato(ruta)
    print("\n✅ CONTRATO COMPLETO EXTRAÍDO:")
    print(json.dumps(final, indent=4, ensure_ascii=False))
except Exception as e:
    print(f"❌ Error: {e}")