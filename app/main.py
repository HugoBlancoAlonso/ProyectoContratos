# ======================================================
# app/main.py
# MENÚ PRINCIPAL - Punto de entrada de la app
# ======================================================

import streamlit as st


def mostrar_menu():
    """Menú principal con dos opciones"""
    st.title("📄 Analizador Inteligente de Contratos")
    st.write("Bienvenido a la plataforma de gestión de contratos")
    
    st.write("---")
    st.write("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("")
        st.write("")
        if st.button("🔍 Analizar Contrato", use_container_width=True, key="btn_analizar"):
            st.session_state.pagina = "analizar"
            st.rerun()
    
    with col2:
        st.write("")
        st.write("")
        if st.button("✍️ Generar Contrato", use_container_width=True, key="btn_generar"):
            st.session_state.pagina = "generar"
            st.rerun()
