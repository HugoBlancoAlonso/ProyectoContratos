import pandas as pd
import re
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ======================================================
# SEGMENTADOR PROFESIONAL DE CLÁUSULAS
# Une ambas versiones:
# - Tu versión estable
# - Su versión con regex ampliado
# ======================================================

def segmentar_clausulas(texto, nombre_archivo):

    # --------------------------------------------------
    # REGEX UNIFICADO Y MEJORADO
    # Detecta:
    # CLAUSULA PRIMERA
    # PRIMERA:
    # DÉCIMA SEGUNDA:
    # VIGÉSIMA TERCERA:
    # 1. OBJETO
    # --------------------------------------------------

    patron = r"(Primera|Segunda|Tercera|Cuarta|Quinta|Sexta|Séptima|Octava|Novena|Décima|Undécima|Duodécima|Décimo\s+primera|Décimo\s+segunda|Décimo\s+tercera|Décimo\s+cuarta|Décimo\s+quinta|Décimo\s+sexta|Décimo\s+séptima|Décimo\s+octava|Décimo\s+novena|Vigésima|Vigésimo\s+primera|Vigésimo\s+segunda|Vigésimo\s+tercera|Vigésimo\s+cuarta|Vigésimo\s+quinta)\."


    matches = list(
        re.finditer(
            patron,
            texto,
            re.IGNORECASE | re.VERBOSE
        )
    )

    clausulas = []

    # --------------------------------------------------
    # SI NO DETECTA CLÁUSULAS
    # --------------------------------------------------

    if len(matches) == 0:

        clausulas.append({
            "contrato_id": nombre_archivo,
            "titulo": "CONTRATO_COMPLETO",
            "contenido": texto,
            "longitud": len(texto)
        })

        return pd.DataFrame(clausulas)

    # --------------------------------------------------
    # EXTRAER CADA CLÁUSULA
    # --------------------------------------------------

    for i in range(len(matches)):

        inicio = matches[i].start()
        titulo = matches[i].group().strip()

        if i + 1 < len(matches):
            fin = matches[i + 1].start()
        else:
            fin = len(texto)

        contenido = texto[inicio:fin].strip()

        # limpieza espacios
        contenido = re.sub(r"\s+", " ", contenido)

        clausulas.append({
            "contrato_id": nombre_archivo,
            "titulo": titulo,
            "contenido": contenido,
            "longitud": len(contenido)
        })

    return pd.DataFrame(clausulas)

# ======================================================
# EJECUCIÓN
# ======================================================

ruta = "data/contratosParaAnalizar/contrato_limpio.txt"

if os.path.exists(ruta):

    with open(ruta, "r", encoding="utf-8") as f:
        texto = f.read()

    df = segmentar_clausulas(
        texto,
        "contrato_01"
    )

    salida = "data/contratosParaAnalizar/clausulas_contrato.csv"

    df.to_csv(
        salida,
        index=False,
        encoding="utf-8"
    )

    print(f"✅ Detectadas {len(df)} cláusulas.")
    print(f"📄 Archivo guardado en: {salida}")

else:

    print("❌ No existe contrato_limpio.txt")