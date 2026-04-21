import fitz  # PyMuPDF
import re
import os  # Necesario para manejar carpetas

def extraer_texto_legal_pro(ruta_pdf):
    """
    Extrae texto eliminando superíndices y ruidos mediante 
    análisis de metadatos de fuente y regex.
    """
    try:
        doc = fitz.open(ruta_pdf)
        texto_final = []

        for num_pag, pagina in enumerate(doc):
            # 1. Obtener estructura detallada de la página
            dict_pag = pagina.get_text("dict")
            
            # 2. Identificar el tamaño de fuente predominante (cuerpo del texto)
            tamanos = []
            for bloque in dict_pag["blocks"]:
                if "lines" in bloque:
                    for linea in bloque["lines"]:
                        for span in linea["spans"]:
                            # Limpiamos espacios vacíos para no falsear la estadística
                            if span["text"].strip():
                                tamanos.append(round(span["size"], 1))
            
            if not tamanos:
                continue
                
            # La moda (valor más frecuente) será nuestro tamaño de referencia
            fuente_principal = max(set(tamanos), key=tamanos.count)
            
            texto_pagina = ""
            for bloque in dict_pag["blocks"]:
                if "lines" in bloque:
                    for linea in bloque["lines"]:
                        linea_texto = ""
                        for span in linea["spans"]:
                            # FILTRO CRÍTICO: 
                            # Solo aceptamos texto cuyo tamaño sea >= al 95% de la fuente principal.
                            # Esto descarta superíndices y notas al pie minúsculas.
                            if span["size"] >= (fuente_principal * 0.95):
                                linea_texto += span["text"]
                        
                        texto_pagina += linea_texto + " "
                    texto_pagina += "\n"

            # 3. Limpieza final con Regex (para ruidos estructurales)
            # Eliminar números de página: "Página X de Y"
            texto_pagina = re.sub(r'(?i)p[áa]gina\s+\d+\s+de\s+\d+', '', texto_pagina)
            # Normalizar saltos de línea y espacios
            texto_pagina = re.sub(r' {2,}', ' ', texto_pagina)
            
            texto_final.append(texto_pagina)

        # Unir y limpiar espacios en blanco excesivos
        resultado = "\n".join(texto_final)
        return re.sub(r'\n{3,}', '\n\n', resultado).strip()

    except Exception as e:
        return f"Error en el pipeline: {e}"

# --- NUEVA LÓGICA PARA PROCESAR CARPETA ---

carpeta_entrada = "data/raw/contratos"  # Define aquí tu carpeta de origen
carpeta_salida = "data/processed/contratosLimpios"  # Define aquí tu carpeta de destino

# Crear la carpeta de salida si no existe
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Iterar por todos los archivos de la carpeta
for nombre_archivo in os.listdir(carpeta_entrada):
    # Procesar solo archivos con extensión .pdf
    if nombre_archivo.lower().endswith(".pdf"):
        ruta_completa = os.path.join(carpeta_entrada, nombre_archivo)
        
        print(f"Procesando: {nombre_archivo}...")
        
        # Llamada a tu función original
        texto_puro = extraer_texto_legal_pro(ruta_completa)

        # Definir el nombre de salida: nombre original + .txt
        nombre_raiz, _ = os.path.splitext(nombre_archivo)
        nombre_salida = f"{nombre_raiz}.txt"
        ruta_salida = os.path.join(carpeta_salida, nombre_salida)

        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(texto_puro)

print("¡Listo! Todos los archivos han sido procesados.")