# ======================================================
# app/analizar_contrato.py
# ANÁLISIS DE CONTRATOS
# ======================================================

import streamlit as st
import pandas as pd
import subprocess
import os
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re


def limpiar_texto(txt):
    """Limpia el texto para asegurar codificación UTF-8"""
    try:
        return txt.encode("latin1").decode("utf-8")
    except:
        return txt


def colorear_confianza(val):
    """Colorea la confianza según nivel"""
    texto = str(val).replace("%", "").replace(",", ".").strip()

    try:
        confianza = float(texto)
    except ValueError:
        return ""

    if confianza >= 90:
        return "background-color:#d1e7dd; color:#0f5132; font-weight:600"
    elif confianza >= 75:
        return "background-color:#fff3cd; color:#664d03; font-weight:600"
    else:
        return "background-color:#f8d7da; color:#842029; font-weight:600"


def mostrar_metricas(df):
    """Muestra métricas de resultados"""
    abusivas = df["Dictamen"].astype(str).str.contains("ABUSIVA").sum()
    revision = df["Dictamen"].astype(str).str.contains("REVISIÓN").sum()
    legales = len(df) - abusivas - revision

    c1, c2, c3 = st.columns(3)

    c1.metric("⚠️ Abusivas", abusivas)
    c2.metric("🔍 Revisión", revision)
    c3.metric("✅ Legales", legales)


def mostrar_graficos(df):
    """Muestra gráficos de análisis"""
    if df.empty:
        return

    sns.set_theme(style="whitegrid")

    # Longitud cláusulas
    if "titulo" in df.columns and "longitud" in df.columns:
        fig, ax = plt.subplots(figsize=(15, 6))

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

    # Frecuencia palabras
    texto = " ".join(df["contenido"].astype(str)).lower()

    palabras = re.findall(r"\b[a-záéíóúñ]{4,}\b", texto)

    stop = {
        "para", "esta", "este", "como", "donde", "entre",
        "desde", "hasta", "sobre", "tambien", "cuando",
        "debera", "podra", "haber", "seran"
    }

    palabras = [p for p in palabras if p not in stop]

    comunes = Counter(palabras).most_common(15)

    if comunes:
        top = pd.DataFrame(
            comunes,
            columns=["Palabra", "Frecuencia"]
        )

        fig2, ax2 = plt.subplots(figsize=(10, 6))

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


def mostrar_pagina():
    """Página de análisis de contratos"""
    
    if st.button("← Volver al menú"):
        st.session_state.pagina = "menu"
        st.rerun()
    
    st.title("📄 Analizador Inteligente de Contratos")
    st.write("Sube un contrato PDF y analiza cláusulas automáticamente.")
    
    # Inicializar estado de análisis
    if "archivo_actual" not in st.session_state:
        st.session_state.archivo_actual = None
    
    # ================================================
    # SUBIR PDF
    # ================================================
    
    archivo = st.file_uploader(
        "Subir contrato PDF",
        type=["pdf"],
        key="pdf_uploader"
    )

    if archivo:
        # Verificar si es un archivo nuevo
        archivo_changed = st.session_state.archivo_actual != archivo.name
        st.session_state.archivo_actual = archivo.name
        
        # Crear directorio si no existe
        os.makedirs("data/contratosParaAnalizar", exist_ok=True)
        
        # Guardar el PDF
        ruta_pdf = "data/contratosParaAnalizar/contrato.pdf"
        with open(ruta_pdf, "wb") as f:
            f.write(archivo.getbuffer())

        st.success(f"Archivo '{archivo.name}' subido correctamente.")
        st.info(f"Tamaño: {archivo.size / 1024:.2f} KB")

        # ================================================
        # BOTÓN ANALIZAR
        # ================================================
        
        if st.button("🔍 Iniciar Análisis", use_container_width=True):

            with st.spinner("Procesando contrato..."):
                barra = st.progress(0, text="Iniciando análisis...")
                
                procesos = [
                    ("Extrayendo texto del PDF...", "src/pipeline/single_file/extraccionTexto.py", 25),
                    ("Detectando cláusulas...", "src/pipeline/single_file/creacionBaseClausulas.py", 50),
                    ("Analizando entidades (NER)...", "src/analysis/ner.py", 75),
                    ("Evaluando legalidad y abusividad...", "src/analysis/motorDeSimilaridad.py", 100)
                ]

                analisis_exitoso = True
                errores = []

                for i, (mensaje, script, progreso) in enumerate(procesos):
                    barra.progress(progreso, text=mensaje)

                    try:
                        resultado = subprocess.run(
                            ["python", script],
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="ignore",
                            timeout=300
                        )

                        if resultado.returncode != 0:
                            analisis_exitoso = False
                            error_msg = f"Error en {script}: {resultado.stderr[:200]}"
                            errores.append(error_msg)
                            st.warning(error_msg)

                    except subprocess.TimeoutExpired:
                        analisis_exitoso = False
                        error_msg = f"Timeout en {script} (>5 min)"
                        errores.append(error_msg)
                        st.warning(error_msg)
                    except Exception as e:
                        analisis_exitoso = False
                        error_msg = f"Excepción en {script}: {str(e)}"
                        errores.append(error_msg)
                        st.warning(error_msg)

                barra.empty()

                # ================================================
                # MOSTRAR RESULTADOS
                # ================================================

                if analisis_exitoso:
                    st.success("Análisis completado exitosamente!")
                    
                    st.write("---")
                    
                    # RESULTADOS DE PREDICCIÓN
                    ruta_csv = "data/prediccionAbusividad.csv"

                    if os.path.exists(ruta_csv):
                        try:
                            df = pd.read_csv(ruta_csv)

                            # Limpiar texto
                            df = df.applymap(
                                lambda x: limpiar_texto(str(x))
                            )

                            st.subheader("⚠️ Resultado del Análisis")

                            # Mostrar métricas
                            mostrar_metricas(df)

                            # Tabla de resultados
                            styled_df = df.style
                            if "Confianza" in df.columns:
                                styled_df = styled_df.applymap(
                                    colorear_confianza,
                                    subset=["Confianza"]
                                )

                            st.dataframe(
                                styled_df,
                                use_container_width=True,
                                height=500
                            )

                            # Descargar CSV
                            with open(ruta_csv, "rb") as f:
                                st.download_button(
                                    "📥 Descargar Informe CSV",
                                    f,
                                    file_name=f"analisis_{archivo.name.replace('.pdf', '')}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )

                        except Exception as e:
                            st.error(f"Error al leer resultados: {str(e)}")

                    else:
                        st.warning("No se generó el archivo de predicciones")

                    st.write("---")

                    # CLÁUSULAS DETECTADAS
                    ruta_clausulas = "data/contratosParaAnalizar/clausulas_contrato.csv"

                    if os.path.exists(ruta_clausulas):
                        try:
                            dfc = pd.read_csv(ruta_clausulas)

                            dfc = dfc.applymap(
                                lambda x: limpiar_texto(str(x))
                            )

                            st.subheader("📑 Todas las Cláusulas Detectadas")
                            
                            st.info(f"Total de cláusulas encontradas: {len(dfc)}")

                            st.dataframe(
                                dfc,
                                use_container_width=True,
                                height=500
                            )

                            # Gráficos
                            mostrar_graficos(dfc)

                        except Exception as e:
                            st.error(f"Error al leer cláusulas: {str(e)}")

                    else:
                        st.warning("No se generó el archivo de cláusulas")

                else:
                    st.error("El análisis falló. Revisa los errores arriba.")
                    if errores:
                        with st.expander("Ver detalles de errores"):
                            for error in errores:
                                st.text(error)
