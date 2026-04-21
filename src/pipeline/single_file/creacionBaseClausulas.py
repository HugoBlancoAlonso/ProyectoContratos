import pandas as pd
import re
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")


def segmentar_clausulas(texto, nombre_archivo):

    # ----------------------------------------
    # REGEX MEJORADO
    # ----------------------------------------

    patron = r"""
    (
        CLAUSULA\s+[A-ZÁÉÍÓÚÑ]+ |
        CLÁUSULA\s+[A-ZÁÉÍÓÚÑ]+ |
        PRIMERA[\.\:\-] |
        SEGUNDA[\.\:\-] |
        TERCERA[\.\:\-] |
        CUARTA[\.\:\-] |
        QUINTA[\.\:\-] |
        SEXTA[\.\:\-] |
        SEPTIMA[\.\:\-] |
        SÉPTIMA[\.\:\-] |
        OCTAVA[\.\:\-] |
        NOVENA[\.\:\-] |
        DECIMA[\.\:\-] |
        DÉCIMA[\.\:\-] |
        \n\d+\.\s+[A-Z]
    )
    """

    matches = list(
        re.finditer(
            patron,
            texto,
            re.IGNORECASE | re.VERBOSE
        )
    )

    clausulas = []

    # Si no detecta nada
    if len(matches) == 0:

        clausulas.append({
            "contrato_id": nombre_archivo,
            "titulo": "CONTRATO_COMPLETO",
            "contenido": texto,
            "longitud": len(texto)
        })

        return pd.DataFrame(clausulas)

    # Detectar todas
    for i in range(len(matches)):

        inicio = matches[i].start()
        titulo = matches[i].group().strip()

        if i + 1 < len(matches):
            fin = matches[i + 1].start()
        else:
            fin = len(texto)

        contenido = texto[inicio:fin].strip()
        contenido = re.sub(r"\s+", " ", contenido)

        clausulas.append({
            "contrato_id": nombre_archivo,
            "titulo": titulo,
            "contenido": contenido,
            "longitud": len(contenido)
        })

    return pd.DataFrame(clausulas)


# ----------------------------------------
# EJECUCIÓN
# ----------------------------------------

ruta = "data/contratosParaAnalizar/contrato_limpio.txt"

if os.path.exists(ruta):

    with open(ruta, "r", encoding="utf-8") as f:
        texto = f.read()

    df = segmentar_clausulas(texto, "contrato_01")

    df.to_csv(
        "data/contratosParaAnalizar/clausulas_contrato.csv",
        index=False,
        encoding="utf-8"
    )

    print(f"Detectadas {len(df)} clausulas")

else:
    print("No existe contrato_limpio.txt")