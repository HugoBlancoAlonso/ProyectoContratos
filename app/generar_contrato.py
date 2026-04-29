# ======================================================
# app/generar_contrato.py
# GENERACIÓN DE CONTRATOS
# ======================================================

import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO


def generar_pdf_contrato(datos):
    """Genera un PDF del contrato con los datos proporcionados"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    y = height - 50
    
    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "CONTRATO")
    y -= 30
    
    # Datos del contratante
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "DATOS DEL CONTRATANTE:")
    y -= 15
    
    c.setFont("Helvetica", 10)
    c.drawString(70, y, f"Nombre: {datos.get('nombre', '')}")
    y -= 15
    c.drawString(70, y, f"Apellidos: {datos.get('apellidos', '')}")
    y -= 15
    c.drawString(70, y, f"DNI: {datos.get('dni', '')}")
    y -= 15
    c.drawString(70, y, f"Email: {datos.get('email', '')}")
    y -= 15
    c.drawString(70, y, f"Teléfono: {datos.get('telefono', '')}")
    y -= 15
    c.drawString(70, y, f"Dirección: {datos.get('direccion', '')}")
    y -= 30
    
    # Datos del contratado
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "DATOS DEL CONTRATADO:")
    y -= 15
    
    c.setFont("Helvetica", 10)
    c.drawString(70, y, f"Empresa: {datos.get('empresa', '')}")
    y -= 15
    c.drawString(70, y, f"Contacto: {datos.get('contacto_empresa', '')}")
    y -= 15
    c.drawString(70, y, f"Email Empresa: {datos.get('email_empresa', '')}")
    y -= 15
    c.drawString(70, y, f"Teléfono Empresa: {datos.get('telefono_empresa', '')}")
    y -= 30
    
    # Detalles del servicio
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "DETALLES DEL SERVICIO:")
    y -= 15
    
    c.setFont("Helvetica", 10)
    c.drawString(70, y, f"Descripción: {datos.get('descripcion_servicio', '')}")
    y -= 15
    c.drawString(70, y, f"Precio: {datos.get('precio', '')} EUR")
    y -= 15
    c.drawString(70, y, f"Duración: {datos.get('duracion', '')}")
    y -= 30
    
    # Fecha
    c.setFont("Helvetica", 9)
    c.drawString(50, y, f"Generado: {pd.Timestamp.now().strftime('%d/%m/%Y')}")
    
    c.save()
    buffer.seek(0)
    return buffer


def mostrar_pagina():
    """Página de generación de contratos"""
    
    if st.button("← Volver al menú"):
        st.session_state.pagina = "menu"
        st.rerun()
    
    st.title("✍️ Generar Contrato")
    st.write("Completa los datos para generar tu contrato personalizado")
    
    st.write("---")
    
    # ========================================
    # DATOS DEL CONTRATANTE
    # ========================================
    
    st.subheader("👤 Datos del Contratante")
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre *", placeholder="Juan")
    with col2:
        apellidos = st.text_input("Apellidos *", placeholder="García López")
    
    col1, col2 = st.columns(2)
    with col1:
        dni = st.text_input("DNI *", placeholder="12345678A")
    with col2:
        telefono = st.text_input("Teléfono *", placeholder="+34 123 456 789")
    
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email *", placeholder="juan@example.com")
    with col2:
        direccion = st.text_input("Dirección *", placeholder="Calle Principal, 123")
    
    st.write("---")
    
    # ========================================
    # DATOS DEL CONTRATADO
    # ========================================
    
    st.subheader("🏢 Datos del Contratado (Empresa/Proveedor)")
    
    col1, col2 = st.columns(2)
    with col1:
        empresa = st.text_input("Nombre Empresa/Proveedor *", placeholder="Tech Services S.L.")
    with col2:
        contacto_empresa = st.text_input("Contacto Empresa *", placeholder="Carlos García")
    
    col1, col2 = st.columns(2)
    with col1:
        email_empresa = st.text_input("Email Empresa *", placeholder="contacto@techservices.com")
    with col2:
        telefono_empresa = st.text_input("Teléfono Empresa *", placeholder="+34 987 654 321")
    
    st.write("---")
    
    # ========================================
    # DETALLES DEL SERVICIO
    # ========================================
    
    st.subheader("📋 Detalles del Servicio/Producto")
    
    descripcion = st.text_area(
        "Descripción del Servicio/Producto *",
        placeholder="Describe detalladamente el servicio o producto que se va a contratar...",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        precio = st.number_input("Precio (EUR) *", min_value=0.0, step=0.01)
    with col2:
        duracion = st.text_input("Duración del Contrato *", placeholder="12 meses / Indefinido")
    
    st.write("---")
    
    # ========================================
    # TÉRMINOS Y CONDICIONES
    # ========================================
    
    st.subheader("📝 Términos y Condiciones Adicionales")
    
    terminos = st.text_area(
        "Añade términos y condiciones adicionales (opcional)",
        placeholder="Introduce aquí cualquier cláusula o término adicional que desees incluir en el contrato...",
        height=120
    )
    
    st.write("---")
    
    # ========================================
    # BOTONES
    # ========================================
    
    col1, col2, col3 = st.columns(3)
    
    with col2:
        if st.button("📄 Generar PDF", use_container_width=True):
            
            # Validar campos obligatorios
            campos_obligatorios = [
                nombre, apellidos, dni, telefono, email, direccion,
                empresa, contacto_empresa, email_empresa, telefono_empresa,
                descripcion, duracion
            ]
            
            if all(campos_obligatorios) and precio > 0:
                
                datos_contrato = {
                    "nombre": nombre,
                    "apellidos": apellidos,
                    "dni": dni,
                    "telefono": telefono,
                    "email": email,
                    "direccion": direccion,
                    "empresa": empresa,
                    "contacto_empresa": contacto_empresa,
                    "email_empresa": email_empresa,
                    "telefono_empresa": telefono_empresa,
                    "descripcion_servicio": descripcion,
                    "precio": precio,
                    "duracion": duracion,
                    "terminos": terminos
                }
                
                pdf = generar_pdf_contrato(datos_contrato)
                
                st.success("Contrato generado exitosamente!")
                
                st.download_button(
                    label="📥 Descargar Contrato PDF",
                    data=pdf,
                    file_name=f"contrato_{apellidos.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            else:
                st.error("Por favor, completa todos los campos obligatorios (*)")
