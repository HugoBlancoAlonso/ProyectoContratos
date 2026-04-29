# ======================================================
# app/streamlit_app.py
# PUNTO DE ENTRADA PRINCIPAL
# - Menú de navegación
# - Rutas a Analizar y Generar
# ======================================================

import streamlit as st
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------
# CONFIG STREAMLIT
# ------------------------------------------------

st.set_page_config(
    page_title="Analizador IA de Contratos",
    page_icon="⚖️",
    layout="wide"
)

# ------------------------------------------------
# INICIALIZAR SESSION STATE
# ------------------------------------------------

if "pagina" not in st.session_state:
    st.session_state.pagina = "menu"

# ------------------------------------------------
# IMPORTAR PÁGINAS
# ------------------------------------------------

from main import mostrar_menu
from analizar_contrato import mostrar_pagina as mostrar_analizar
from generar_contrato import mostrar_pagina as mostrar_generar

# ================================================
# ROUTER DE NAVEGACIÓN
# ================================================

if st.session_state.pagina == "menu":
    mostrar_menu()

elif st.session_state.pagina == "analizar":
    mostrar_analizar()

elif st.session_state.pagina == "generar":
    mostrar_generar()