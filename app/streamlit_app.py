import streamlit as st
import pandas as pd
import subprocess
import os
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

st.set_page_config(page_title="Analizador de Contratos", layout="wide")

st.title("📄 Analizador Inteligente de Contratos")

st.write("Sube un contrato PDF y analiza cláusulas abusivas automáticamente.")


def graficos_eda_desde_df(df_clausulas: pd.DataFrame) -> None:
    """Genera y muestra en Streamlit los graficos EDA para el contrato actual."""
    if df_clausulas.empty or "contenido" not in df_clausulas.columns:
        st.info("No hay datos suficientes para generar EDA.")
        return

    sns.set_theme(style="whitegrid")

    # Grafico 1: longitud de clausulas del contrato actual.
    if "longitud" in df_clausulas.columns and "titulo" in df_clausulas.columns:
        fig_long, ax_long = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df_clausulas, x="titulo", y="longitud", palette="viridis", ax=ax_long)
        ax_long.set_title("Longitud de las Cláusulas (Contrato Actual)")
        ax_long.set_xlabel("Cláusula")
        ax_long.set_ylabel("Número de Caracteres")
        ax_long.tick_params(axis="x", rotation=45)
        plt.tight_layout()

        st.subheader("📊 Longitud cláusulas")
        st.pyplot(fig_long)
        plt.close(fig_long)

    # Grafico 2: frecuencia de palabras del contrato actual.
    texto_total = " ".join(df_clausulas["contenido"].astype(str)).lower()
    palabras = re.findall(r"\b[a-z]{4,}\b", texto_total)
    stop_words = {"para", "este", "esta", "con", "que", "las", "los", "del", "por", "una", "como"}
    palabras_filtradas = [p for p in palabras if p not in stop_words]

    comunes = Counter(palabras_filtradas).most_common(15)
    if comunes:
        df_comunes = pd.DataFrame(comunes, columns=["Palabra", "Frecuencia"])

        fig_freq, ax_freq = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df_comunes, x="Frecuencia", y="Palabra", palette="magma", ax=ax_freq)
        ax_freq.set_title("Top 15 Palabras más Frecuentes (Contrato Actual)")
        plt.tight_layout()

        st.subheader("📈 Frecuencia palabras")
        st.pyplot(fig_freq)
        plt.close(fig_freq)

# Subida archivo
archivo = st.file_uploader("Subir contrato PDF", type=["pdf"])

if archivo:

    ruta_guardado = "data/contratosParaAnalizar/contrato.pdf"

    with open(ruta_guardado, "wb") as f:
        f.write(archivo.read())

    st.success("Contrato subido correctamente.")

    if st.button("🔍 Analizar contrato"):

        with st.spinner("Procesando contrato..."):

            subprocess.run(["python", "src/pipeline/single_file/extraccionTexto.py"])
            subprocess.run(["python", "src/pipeline/single_file/creacionBaseClausulas.py"])
            subprocess.run(["python", "src/analysis/ner.py"])
            subprocess.run(["python", "src/analysis/motorDeSimilaridad.py"])

        st.success("Análisis completado.")

        # Resultados
        if os.path.exists("data/prediccionAbusividad.csv"):

            df = pd.read_csv("data/prediccionAbusividad.csv")

            st.subheader("⚠️ Resultado cláusulas")
            st.dataframe(df)

        # EDA dinámico del contrato actual
        ruta_clausulas_actual = "data/contratosParaAnalizar/clausulas_contrato.csv"
        if os.path.exists(ruta_clausulas_actual):
            df_clausulas_actual = pd.read_csv(ruta_clausulas_actual)
            graficos_eda_desde_df(df_clausulas_actual)