from app.streamlit_app import *  # noqa: F401,F403
import streamlit as st
import pandas as pd
import subprocess
import os

st.set_page_config(page_title="Analizador de Contratos", layout="wide")

st.title("📄 Analizador Inteligente de Contratos")

st.write("Sube un contrato PDF y analiza cláusulas abusivas automáticamente.")

# Subida archivo
archivo = st.file_uploader("Subir contrato PDF", type=["pdf"])

if archivo:

    ruta_guardado = "data/contratosParaAnalizar/contrato.pdf"

    with open(ruta_guardado, "wb") as f:
        f.write(archivo.read())

    st.success("Contrato subido correctamente.")

    if st.button("🔍 Analizar contrato"):

        with st.spinner("Procesando contrato..."):

            subprocess.run(["python", "src/ArchivoUnico/extraccionTexto.py"])
            subprocess.run(["python", "src/ArchivoUnico/creacionBaseClausulas.py"])
            subprocess.run(["python", "src/eda.py"])
            subprocess.run(["python", "src/ner.py"])
            subprocess.run(["python", "src/motorDeSimilaridad.py"])

        st.success("Análisis completado.")

        # Resultados
        if os.path.exists("data/prediccionAbusividad.csv"):

            df = pd.read_csv("data/prediccionAbusividad.csv")

            st.subheader("⚠️ Resultado cláusulas")
            st.dataframe(df)

        # Gráficos
        if os.path.exists("data/eda_longitud.png"):
            st.subheader("📊 Longitud cláusulas")
            st.image("data/eda_longitud.png")

        if os.path.exists("data/eda_frecuencia.png"):
            st.subheader("📈 Frecuencia palabras")
            st.image("data/eda_frecuencia.png")