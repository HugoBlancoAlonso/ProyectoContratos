# ======================================================
# app/streamlit_app.py
# VERSION FINAL PROFESIONAL
# - No muestra logs durante análisis
# - Barra progreso limpia
# - Resultados completos
# - Tabla bonita
# - Todas las cláusulas
# - Gráficas correctas
# ======================================================

import streamlit as st
import pandas as pd
import subprocess
import os
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------
# CONFIG
# ------------------------------------------------

st.set_page_config(
    page_title="Analizador IA de Contratos",
    page_icon="⚖️",
    layout="wide"
)

st.title("📄 Analizador Inteligente de Contratos")
st.write("Sube un contrato PDF y analiza cláusulas automáticamente.")

# ------------------------------------------------
# FUNCIONES
# ------------------------------------------------

def limpiar_texto(txt):
    try:
        return txt.encode("latin1").decode("utf-8")
    except:
        return txt


def colorear_dictamen(val):

    val = str(val)

    if "ABUSIVA" in val:
        return "background-color:#ffcccc"

    elif "REVISIÓN" in val:
        return "background-color:#fff3cd"

    else:
        return "background-color:#d4edda"


def mostrar_metricas(df):

    abusivas = df["Dictamen"].astype(str).str.contains("ABUSIVA").sum()
    revision = df["Dictamen"].astype(str).str.contains("REVISIÓN").sum()
    legales = len(df) - abusivas - revision

    c1, c2, c3 = st.columns(3)

    c1.metric("⚠️ Abusivas", abusivas)
    c2.metric("🔍 Revisión", revision)
    c3.metric("✅ Legales", legales)


def mostrar_graficos(df):

    if df.empty:
        return

    sns.set_theme(style="whitegrid")

    # --------------------------------------
    # LONGITUD CLAUSULAS
    # --------------------------------------

    if "titulo" in df.columns and "longitud" in df.columns:

        fig, ax = plt.subplots(figsize=(15,6))

        sns.barplot(
            data=df,
            x="titulo",
            y="longitud",
            palette="viridis",
            ax=ax
        )

        ax.set_title("Longitud de todas las cláusulas")
        ax.set_xlabel("Cláusulas")
        ax.set_ylabel("Caracteres")

        plt.xticks(rotation=45, ha="right")

        st.subheader("📊 Longitud cláusulas")
        st.pyplot(fig)

    # --------------------------------------
    # FRECUENCIA PALABRAS
    # --------------------------------------

    texto = " ".join(df["contenido"].astype(str)).lower()

    palabras = re.findall(r"\b[a-záéíóúñ]{4,}\b", texto)

    stop = {
        "para","esta","este","como","donde","entre",
        "desde","hasta","sobre","tambien","cuando",
        "debera","podra","haber","seran"
    }

    palabras = [p for p in palabras if p not in stop]

    comunes = Counter(palabras).most_common(15)

    if comunes:

        top = pd.DataFrame(
            comunes,
            columns=["Palabra","Frecuencia"]
        )

        fig2, ax2 = plt.subplots(figsize=(10,6))

        sns.barplot(
            data=top,
            x="Frecuencia",
            y="Palabra",
            palette="magma",
            ax=ax2
        )

        ax2.set_title("Top 15 palabras")

        st.subheader("📈 Frecuencia palabras")
        st.pyplot(fig2)

# ------------------------------------------------
# SUBIR PDF
# ------------------------------------------------

archivo = st.file_uploader(
    "Subir contrato PDF",
    type=["pdf"]
)

# ------------------------------------------------
# SI HAY PDF
# ------------------------------------------------

if archivo:

    ruta_pdf = "data/contratosParaAnalizar/contrato.pdf"

    with open(ruta_pdf, "wb") as f:
        f.write(archivo.read())

    st.success("Contrato subido correctamente.")

    if st.button("🔍 Analizar contrato"):

        barra = st.progress(0)
        estado = st.empty()

        procesos = [
            ("Extrayendo texto...", "src/pipeline/single_file/extraccionTexto.py"),
            ("Detectando cláusulas...", "src/pipeline/single_file/creacionBaseClausulas.py"),
            ("Analizando entidades...", "src/analysis/ner.py"),
            ("Evaluando legalidad...", "src/analysis/motorDeSimilaridad.py")
        ]

        for i, (mensaje, script) in enumerate(procesos):

            estado.info(mensaje)

            resultado = subprocess.run(
                ["python", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            barra.progress((i + 1) * 25)

            if resultado.returncode != 0:
                st.error(f"Error en {script}")
                st.code(resultado.stderr)
                st.stop()

        barra.empty()
        estado.empty()

        st.success("✅ Análisis completado")

        # ------------------------------------------------
        # RESULTADOS
        # ------------------------------------------------

        ruta_csv = "data/prediccionAbusividad.csv"

        if os.path.exists(ruta_csv):

            df = pd.read_csv(ruta_csv)

            df = df.applymap(
                lambda x: limpiar_texto(str(x))
            )

            st.subheader("⚠️ Resultado análisis")

            mostrar_metricas(df)

            st.dataframe(
                df.style.applymap(
                    colorear_dictamen,
                    subset=["Dictamen"]
                ),
                use_container_width=True,
                height=500
            )

            with open(ruta_csv, "rb") as f:

                st.download_button(
                    "📥 Descargar Informe CSV",
                    f,
                    file_name="resultado_analisis.csv",
                    mime="text/csv"
                )

        # ------------------------------------------------
        # CLAUSULAS
        # ------------------------------------------------

        ruta_clausulas = "data/contratosParaAnalizar/clausulas_contrato.csv"

        if os.path.exists(ruta_clausulas):

            dfc = pd.read_csv(ruta_clausulas)

            dfc = dfc.applymap(
                lambda x: limpiar_texto(str(x))
            )

            st.subheader("📑 Todas las cláusulas detectadas")

            st.dataframe(
                dfc,
                use_container_width=True,
                height=500
            )

            mostrar_graficos(dfc)