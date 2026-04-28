import fitz  # PyMuPDF
import re
import sys
sys.stdout.reconfigure(encoding="utf-8")


def _unir_titulo_con_subclausula(texto_pagina):
    """
    Une títulos de cláusula con la primera subcláusula numerada siguiente.
    Ejemplo: "Clausula 2\n2.1 ..." -> "Clausula 2 2.1 ..."
    """
    lineas = [linea.strip() for linea in texto_pagina.splitlines()]
    lineas = [linea for linea in lineas if linea]
    resultado = []
    i = 0

    while i < len(lineas):
        linea_actual = lineas[i]
        linea_siguiente = lineas[i + 1] if i + 1 < len(lineas) else ""

        if re.match(r'(?i)^cl[áa]usula\s+.+$', linea_actual) and re.match(r'^\d+(?:\.\d+)*\b', linea_siguiente):
            resultado.append(f"{linea_actual} {linea_siguiente}")
            i += 2
            continue

        resultado.append(linea_actual)
        i += 1

    return "\n".join(resultado)


def extraer_texto_legal_pro(ruta_pdf):
    """
    Extrae texto eliminando superíndices y ruidos mediante
    análisis de metadatos de fuente y regex.
    """
    try:
        doc = fitz.open(ruta_pdf)
        texto_final = []

        for num_pag, pagina in enumerate(doc):
            # 1. Obtener estructura detallada de la página
            dict_pag = pagina.get_text("dict")
           
            # 2. Identificar el tamaño de fuente predominante (cuerpo del texto)
            tamanos = []

            for bloque in dict_pag["blocks"]:
                if "lines" in bloque:
                    for linea in bloque["lines"]:
                        for span in linea["spans"]:
                            # Limpiamos espacios vacíos para no falsear la estadística
                            if span["text"].strip():
                                tamanos.append(round(span["size"], 1))
           
            if not tamanos:
                continue
               
            # La moda (valor más frecuente) será nuestro tamaño de referencia
            fuente_principal = max(set(tamanos), key=tamanos.count)
            texto_pagina = ""

            for bloque in dict_pag["blocks"]:
                if "lines" in bloque:
                    for linea in bloque["lines"]:
                        linea_texto = ""
                        for span in linea["spans"]:
                            # FILTRO CRÍTICO:
                            # Solo aceptamos texto cuyo tamaño sea >= al 95% de la fuente principal.
                            # Esto descarta superíndices y notas al pie minúsculas.
                            if span["size"] >= (fuente_principal * 0.95):
                                linea_texto += span["text"]
                        texto_pagina += linea_texto + " "
                    texto_pagina += "\n"
            # 3. Limpieza final con Regex (para ruidos estructurales)
            # Eliminar números de página: "Página X de Y"
            texto_pagina = re.sub(r'(?i)p[áa]gina\s+\d+\s+de\s+\d+', '', texto_pagina)
            # Normalizar saltos de línea y espacios
            texto_pagina = re.sub(r' {2,}', ' ', texto_pagina)
            texto_pagina = _unir_titulo_con_subclausula(texto_pagina)
            texto_final.append(texto_pagina)

        # Unir y limpiar espacios en blanco excesivos
        resultado = "\n".join(texto_final)
        return re.sub(r'\n{3,}', '\n\n', resultado).strip()

    except Exception as e:
        return f"Error en el pipeline: {e}"


# --- Ejemplo de ejecución ---

ruta = "data/contratosParaAnalizar/contrato.pdf"
texto_puro = extraer_texto_legal_pro(ruta)

with open("data/contratosParaAnalizar/contrato_limpio.txt", "w", encoding="utf-8") as f:
    f.write(texto_puro)

print("¡Listo! Texto extraído sin superíndices.")