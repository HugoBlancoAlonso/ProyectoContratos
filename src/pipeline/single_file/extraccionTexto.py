import fitz  # PyMuPDF
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ======================================================
# FUNCIÓN AUXILIAR
# Une títulos partidos con subcláusulas
# Ej:
# Clausula 2
# 2.1 Objeto
# =>
# Clausula 2 2.1 Objeto
# ======================================================

def unir_titulo_con_subclausula(texto_pagina):

    lineas = texto_pagina.splitlines()
    lineas = [l.strip() for l in lineas if l.strip()]

    resultado = []
    i = 0

    while i < len(lineas):

        actual = lineas[i]
        siguiente = lineas[i + 1] if i + 1 < len(lineas) else ""

        es_titulo = re.match(
            r"(?i)^cl[áa]usula\s+.+$",
            actual
        )

        es_subtitulo = re.match(
            r"^\d+(\.\d+)*\b",
            siguiente
        )

        if es_titulo and es_subtitulo:

            resultado.append(
                f"{actual} {siguiente}"
            )

            i += 2
            continue

        resultado.append(actual)
        i += 1

    return "\n".join(resultado)

# ======================================================
# EXTRACCIÓN PROFESIONAL TEXTO PDF
# ======================================================

def extraer_texto_legal_pro(ruta_pdf):

    try:

        doc = fitz.open(ruta_pdf)

        texto_final = []

        for pagina in doc:

            dict_pag = pagina.get_text("dict")

            # ------------------------------------------
            # Detectar tamaño fuente dominante
            # ------------------------------------------

            tamanos = []

            for bloque in dict_pag["blocks"]:

                if "lines" in bloque:

                    for linea in bloque["lines"]:

                        for span in linea["spans"]:

                            if span["text"].strip():

                                tamanos.append(
                                    round(span["size"], 1)
                                )

            if not tamanos:
                continue

            fuente_principal = max(
                set(tamanos),
                key=tamanos.count
            )

            texto_pagina = ""

            # ------------------------------------------
            # Filtrar superíndices / notas pie
            # ------------------------------------------

            for bloque in dict_pag["blocks"]:

                if "lines" in bloque:

                    for linea in bloque["lines"]:

                        linea_texto = ""

                        for span in linea["spans"]:

                            if span["size"] >= (
                                fuente_principal * 0.95
                            ):

                                linea_texto += span["text"]

                        texto_pagina += linea_texto + " "

                    texto_pagina += "\n"

            # ------------------------------------------
            # Limpieza regex
            # ------------------------------------------

            texto_pagina = re.sub(
                r"(?i)p[áa]gina\s+\d+\s+de\s+\d+",
                "",
                texto_pagina
            )

            texto_pagina = re.sub(
                r"[ ]{2,}",
                " ",
                texto_pagina
            )

            texto_pagina = re.sub(
                r"\n{2,}",
                "\n",
                texto_pagina
            )

            # ------------------------------------------
            # Unión de títulos partidos
            # ------------------------------------------

            texto_pagina = unir_titulo_con_subclausula(
                texto_pagina
            )

            texto_final.append(texto_pagina)

        # ----------------------------------------------
        # Unir documento final
        # ----------------------------------------------

        resultado = "\n".join(texto_final)

        resultado = re.sub(
            r"\n{3,}",
            "\n\n",
            resultado
        ).strip()

        return resultado

    except Exception as e:

        return f"Error en extracción: {e}"

# ======================================================
# EJECUCIÓN
# ======================================================

ruta = "data/contratosParaAnalizar/contrato.pdf"

texto = extraer_texto_legal_pro(ruta)

salida = "data/contratosParaAnalizar/contrato_limpio.txt"

with open(
    salida,
    "w",
    encoding="utf-8"
) as f:

    f.write(texto)

print("✅ Texto extraído correctamente.")
print(f"📄 Archivo generado: {salida}")