# ======================================================
# app/generar_contrato.py
# GENERACIÓN DE CONTRATOS
# ======================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from fpdf import FPDF

def generar_pdf_contrato(datos):

    class ContratoVivienda(FPDF):
        def header(self):
            # Fuente para el título principal
            self.set_font("Arial", "B", 12)
            if self.page_no() == 1:
                self.multi_cell(0, 10, "MODELO ORIENTATIVO DE CONTRATO DE ARRENDAMIENTO DE VIVIENDA", align="C")
                self.ln(5)

        def footer(self):
            # Posición a 1.5 cm del final
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            # Número de página
            self.cell(0, 10, f"Página {self.page_no()}", align="C")

        def titulo_seccion(self, texto):
            self.set_font("Arial", "B", 11)
            self.cell(0, 10, texto.upper(), ln=True)
            self.ln(2)

        def parrafo(self, texto):
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 5, texto, align="J")
            self.ln(4)

        def clausula(self, titulo, cuerpo):
            self.set_font("Arial", "B", 10)
            self.multi_cell(0, 5, titulo)
            self.ln(1)
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 5, cuerpo, align="J")
            self.ln(4)


    pdf = ContratoVivienda()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- ENCABEZADO FECHA ---
    hoy = datetime.now()
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"En {datos["ciudadV"]}, a {hoy.day} de {hoy.month} de {hoy.year}", ln=True)
    pdf.ln(5)

    # --- SECCIÓN REUNIDOS ---
    pdf.titulo_seccion("REUNIDOS")
    reunidos_texto = (
        f"De una parte, y como arrendador, persona física, D/Dña. {datos["nombreV"]} {datos["apellidoV"]}, mayor de edad, "
        f"domiciliado/a en {datos["direccionV"]} y con NIF nº {datos["dniV"]} Y con datos de contacto a efectos de "
        f"notificaciones: correo electrónico: {datos["emailV"]} y número de teléfono: {datos["telefonoV"]}\n\n"
        f"De otra parte, y como arrendatario, D/Dña. {datos["nombreC"]} {datos["apellidoC"]} mayor de edad, con NIF {datos["dniC"]} "
        f"con domicilio a efectos de notificaciones en la vivienda objeto de arrendamiento. Y con datos "
        f"de contacto a efectos de notificaciones: correo electrónico: {datos["emailC"]} y número de teléfono: {datos["telefonoC"]}\n\n"
        f"Ambas partes se reconocen la capacidad legalmente necesaria para el otorgamiento del presente contrato de arrendamiento."
    )
    pdf.parrafo(reunidos_texto)

    # --- SECCIÓN EXPONEN ---
    pdf.titulo_seccion("EXPONEN")
    exponen_texto = (
        f"Que D/ Dña. {datos["nombreV"]} arrendador, es propietario/a de una vivienda localizada en la "
        f"{datos["dirVivienda"]} con Referencia Catastral {datos["refCatastral"]} e inscrita en el Registro de la "
        f"Propiedad ({datos["registro"]}) y de una vivienda amueblada de {datos["metros"]} m2.\n\n"
        f"Se deja constancia de que la vivienda posee el preceptivo certificado de eficiencia energética, "
        f"de conformidad con lo establecido por el Real Decreto 235/2013, de 5 de abril, por el que se "
        f"aprueba el procedimiento básico para la certificación de la eficiencia energética de los edificios.\n\n"
        f"Que D/Dña {datos["nombreC"]} está interesado/a en arrendar para uso permanente de vivienda suyo y/o "
        f"de su familia. En la totalidad de uso permanente {datos["numeroPersonas"]} persona/s.\n\n"
        f"Ambas partes se comprometen a cumplir con lo pactado en el presente contrato de arrendamiento."
    )
    pdf.parrafo(exponen_texto)

    # --- SECCIÓN CLÁUSULAS ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "CLÁUSULAS", ln=True, align="C")
    pdf.ln(2)

    pdf.clausula("Primera. Regulación", 
        "El presente contrato se regulará por lo aquí pactado y en su defecto por lo establecido por la Ley de Arrendamientos Urbanos.")

    pdf.clausula("Segunda. Objeto y entrega de la posesión.", 
        f"El contenido del contrato es el alquiler de un inmueble con destino a vivienda permanente para {datos["numeroPersonas"]} personas. "
        "El arrendador, hace entrega con la firma de este contrato de las llaves de la vivienda alquilada y de su posesión. "
        "También entrega en cumplimiento de la normativa vigente el certificado energético de la vivienda. "
        "El arrendatario la recibe con pleno conocimiento de las condiciones en las que se encuentra y se somete al "
        "régimen de propiedad horizontal en el que se encuentra el inmueble. Asimismo el arrendatario se compromete a: \n"
        "- Utilizar la vivienda con la debida diligencia y destinarla al que está destinada.\n"
        "- Conservarla en las condiciones en las que le fue entregada, sin que sufra mayores deterioros que el propio "
        "de su utilización ordinaria y el deterioro producido por el paso del tiempo o por causa inevitable.\n"
        "- No realizar actividades de tipo industrial o actividades molestas, insalubres, nocivas o peligrosas.")

    pdf.clausula("Tercera. Plazo de duración.", 
        f"El plazo de duración del presente contrato de arrendamiento es {datos["duracion"]}, a contar desde la fecha del otorgamiento de este contrato. "
        f"El arrendamiento se prorrogará de manera automática por períodos de {datos["duracion"]} hasta un plazo de 5 años, salvo que el arrendatario "
        "comunique por escrito al arrendador su intención de no renovarlo con treinta días de antelación al cumplimiento del plazo pactado o de "
        "cualquiera de sus prórrogas anuales.")

    pdf.clausula("Cuarta. Prórroga tácita", 
        "Una vez transcurridos como mínimo cinco años de duración del contrato, si el arrendatario no ha notificado al arrendador su intención de "
        "no renovarlo con un plazo de 2 meses de antelación, ni el arrendador al arrendatario con un plazo de 4 meses, el contrato se prorrogará "
        "obligatoriamente por plazos anuales hasta un máximo de tres años más, salvo que el arrendatario manifieste al arrendador con un mes de "
        "antelación a la fecha de terminación de cualquiera de las anualidades, su voluntad de no renovar el contrato.")

    pdf.clausula("Quinta. Renta", 
        f"Se fija como renta mensual la cantidad de {datos["precio"]}€. Se pagará mensualmente por meses anticipados, dentro de los siete primeros días de "
        f"cada mes, mediante ingreso en metálico o transferencia bancaria a favor del Arrendador en la cuenta que a nombre de este último y con el nº "
        f"{datos["numeroBancoV"]} existe en el Banco {datos["bancoV"]}, sucursal nº {datos["sucursalV"]} .\n\n"
        "El pago se acreditará de manera suficiente mediante el oportuno resguardo del ingreso o transferencia realizados o, si se paga en metálico, "
        "mediante el correspondiente recibo expedido por el arrendador.")

    pdf.clausula("Sexta. Actualización de la renta.", 
        "La renta solo podrá ser actualizada en la fecha en que se cumpla cada año de vigencia del contrato. Se actualizará para cada anualidad por "
        f"referencia a la variación anual del Índice de Garantía de Competitividad a fecha de cada actualizacion. El incremento producido no podrá exceder del IPC... "
        "La renta actualizada será exigible a partir del mes siguiente a su notificación por escrito.")

    pdf.clausula("Septima. Gastos y servicios", 
        "El precio del arrendamiento incluye los gastos generales del inmueble, servicios, tributos, cargas que consistan en comunidad y tasas de basuras, "
        "así como las demás responsabilidades no susceptibles de individualización.")

    pdf.clausula("Octava. Fianza", 
        f"En el momento de la firma de este contrato, el arrendatario hace entrega al arrendador del importe de una mensualidad de renta, {datos["precio"]} euros, "
        "en concepto de fianza legal. La fianza legal queda establecida en garantía de las obligaciones legales y contractuales del arrendatario. "
        "En ningún caso su importe podrá imputarse al pago de la renta. La devolución se hará al finalizar el contrato.")

    pdf.clausula("Novena. Conservación de la vivienda", 
        "El arrendador se compromete a realizar las reparaciones necesarias para conservar la vivienda en condiciones de habitabilidad, sin derecho a elevar por ello la renta, " 
        "salvo que aquellas sean consecuencia directa del arrendatario. "
        "Transcurrido los cinco primeros años, el arrendador podrá realizar obras de mejora con derecho a elevar la renta según la LAU.")

    pdf.clausula("Décima. Obras del arrendatario", 
        "El arrendatario no podrá realizar obras que modifiquen la configuración de la vivienda sin permiso por escrito. Las obras autorizadas quedarán "
        "en beneficio de la propiedad al término del contrato.")

    pdf.clausula("Undécima. Cesión y subarriendo", 
        "El contrato no se podrá ceder o subarrendar por el arrendatario sin el consentimiento escrito del arrendador. " 
        "En el caso de tener dicho consentimiento se regulará por lo pactado entre las partes.En todo caso, se extinguirá cuando lo haga el del arrendatario y el precio " 
        "no podrá exceder del establecido para el arrendamiento.")

    pdf.clausula("Duodécima. Resolución del contrato", 
        "El incumplimiento de cualquiera de las cláusulas de este contrato y, en su defecto, de la normativa que resulte de aplicación, será causa de resolución del contrato " 
        "para cualquiera de las partes.")

    pdf.clausula("Décimo cuarta. Resolución de conflictos.", 
        "Para la resolución de cualquier conflicto derivado de la interpretación del presente las partes se someten a la jurisdicción ordinaria.")
    
    if (datos["terminos"]):
        pdf.clausula("Clausulas específicas del arrendador.", 
        f"{datos["terminos"]}")

    # Devolver el PDF en memoria como bytes para que Streamlit lo descargue
    out = pdf.output(dest='S')
    if isinstance(out, str):
        pdf_bytes = out.encode('latin-1')
    elif isinstance(out, bytearray):
        pdf_bytes = bytes(out)
    else:
        # already bytes
        pdf_bytes = out

    print("Contrato generado en memoria.")
    return pdf_bytes


def mostrar_pagina():
    """Página de generación de contratos"""
    
    if st.button("← Volver al menú"):
        st.session_state.pagina = "menu"
        st.rerun()
    
    st.title("✍️ Generar Contrato")
    st.write("Completa los datos para generar tu contrato personalizado")
    
    st.write("---")
    
    # ========================================
    # DATOS DEL Arrendador
    # ========================================
    
    st.subheader("👤 Datos del ARRENDADOR")
    
    col1, col2 = st.columns(2)
    with col1:
        nombreV = st.text_input("Nombre arrendador *", placeholder="Juan")
    with col2:
        apellidosV = st.text_input("Apellidos arrendador *", placeholder="García López")
    
    col1, col2 = st.columns(2)
    with col1:
        dniV = st.text_input("DNI arrendador *", placeholder="12345678A")
    with col2:
        telefonoV = st.text_input("Teléfono arrendador *", placeholder="+34 123 456 789")
    
    col1, col2 = st.columns(2)
    with col1:
        emailV = st.text_input("Email arrendador *", placeholder="juan@example.com")
    with col2:
        ciudadV = st.text_input("Ciudad arrendador *", placeholder="Madrid")

    col1, col2 = st.columns(2)
    with col1:
        direccionV = st.text_input("Dirección arrendador *", placeholder="Calle Principal, 123")
        
    with col2:
        numeroBancoV = st.text_input("Numero cuenta bancaria arrendador *", placeholder="43283649237432")
        

    col1, col2 = st.columns(2)
    with col1:
        bancoV = st.text_input("Nombre del banco *", placeholder="Santander")
    with col2:   
        sucursalV = st.text_input("Sucursal *", placeholder="7")
    
    st.write("---")

    # ========================================
    # DATOS DEL ARRENDATARIO
    # ========================================
    
    st.subheader("👤 Datos del ARRENDADOR")
    
    col1, col2 = st.columns(2)
    with col1:
        nombreC = st.text_input("Nombre arrendatario *", placeholder="Juan")
    with col2:
        apellidosC = st.text_input("Apellidos arrendatario *", placeholder="García López")
    
    col1, col2 = st.columns(2)
    with col1:
        dniC = st.text_input("DNI arrendatario *", placeholder="12345678A")
    with col2:
        telefonoC = st.text_input("Teléfono arrendatario *", placeholder="+34 123 456 789")
    
    col1, col2 = st.columns(2)
    with col1:
        emailC = st.text_input("Email arrendatario *", placeholder="juan@example.com")
    
    st.write("---")
    
    # ========================================
    # DETALLES DEL SERVICIO
    # ========================================
    
    st.subheader("📋 Detalles del Contrato")
    
    col1, col2 = st.columns(2)
    with col1:
        precio = st.number_input("Precio (EUR) *", min_value=0.0, step=0.01)
    with col2:
        duracion = st.text_input("Duración del Contrato *", placeholder="12 meses / Indefinido")

    col1, col2 = st.columns(2)
    with col1:
        metros = st.number_input("Metros (m2) *", placeholder="97")
    with col2:
        numeroPersonas = st.text_input("Numero de personas *", placeholder="4")

    col1, col2 = st.columns(2)
    with col1:
        dirVivienda = st.text_input("Direccion de la vivienda a alquilar *", placeholder="Calle San Mames numero 10 1A")
    with col2:
        refCatastral = st.text_input("Referancia catastral *", placeholder="12345678901234567890")
    
    col1, col2 = st.columns(2)
    with col1:
        registro = st.text_input("Registro *", placeholder="si / no")

    
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
                nombreV, apellidosV, dniV, telefonoV, emailV, ciudadV, direccionV, nombreC, apellidosC, dniC, telefonoC, emailC,
                numeroBancoV,bancoV, sucursalV, precio, metros, numeroPersonas, duracion, dirVivienda, refCatastral, registro
            ]
            
            if all(campos_obligatorios) and precio > 0:
                
                datos_contrato = {
                    "nombreV": nombreV,
                    "apellidosV": apellidosV,
                    "dniV": dniV,
                    "telefonoV": telefonoV,
                    "emailV": emailV,
                    "ciudadV": ciudadV,
                    "direccionV": direccionV,
                    "nombreC": nombreC,
                    "apellidosC": apellidosC,
                    "dniC": dniC,
                    "telefonoC": telefonoC,
                    "emailC": emailC,
                    "numeroBancoV": numeroBancoV,
                    "bancoV": bancoV,
                    "sucursalV": sucursalV,
                    "precio": precio,
                    "metros": metros,
                    "numeroPersonas": numeroPersonas,
                    "duracion": duracion,
                    "dirVivienda": dirVivienda,
                    "refCatastral": refCatastral,
                    "registro": registro,
                    "terminos": terminos
                }
                
                pdf = generar_pdf_contrato(datos_contrato)
                
                st.success("Contrato generado exitosamente!")
                
                st.download_button(
                    label="📥 Descargar Contrato PDF",
                    data=pdf,
                    file_name=f"contrato_{apellidosV.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            else:
                st.error("Por favor, completa todos los campos obligatorios (*)")
