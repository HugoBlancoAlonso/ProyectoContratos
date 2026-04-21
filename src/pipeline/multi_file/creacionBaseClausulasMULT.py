import pandas as pd
import re
import os

def segmentar_contrato_legal(texto, nombre_archivo):
    # 1. Definimos los encabezados de las cláusulas (del Primera al Vigésima)
    patron_clausulas = r'(Primera|Segunda|Tercera|Cuarta|Quinta|Sexta|Séptima|Octava|Novena|Décima|Undécima|Duodécima|Décimo\s+primera|Décimo\s+segunda|Décimo\s+tercera|Décimo\s+cuarta|Décimo\s+quinta|Décimo\s+sexta|Décimo\s+séptima|Décimo\s+octava|Décimo\s+novena|Vigésima|Vigésimo\s+primera|Vigésimo\s+segunda|Vigésimo\s+tercera|Vigésimo\s+cuarta|Vigésimo\s+quinta)\.'
    
    # 2. Buscamos las posiciones de todos los encabezados
    iter_clausulas = list(re.finditer(patron_clausulas, texto, re.IGNORECASE))
    
    lista_clausulas = []
    
    for i in range(len(iter_clausulas)):
        # Inicio de la cláusula actual
        inicio = iter_clausulas[i].start()
        nombre_clausula = iter_clausulas[i].group()
        
        # El final es el inicio de la siguiente cláusula (o el final del texto)
        fin = iter_clausulas[i+1].start() if i + 1 < len(iter_clausulas) else len(texto)
        
        contenido_clausula = texto[inicio:fin].strip()
        
        # Limpiamos un poco el contenido
        contenido_clausula = re.sub(r'\s+', ' ', contenido_clausula)
        
        lista_clausulas.append({
            "contrato_id": nombre_archivo,
            "titulo": nombre_clausula.capitalize(),
            "contenido": contenido_clausula,
            "longitud": len(contenido_clausula)
        })

    return pd.DataFrame(lista_clausulas)

# --- EJECUCIÓN AUTOMATIZADA POR CARPETA ---

carpeta_entrada = "data/contratosLimpios"
archivo_salida_final = "data/base_clausulas.csv"

# Lista para ir acumulando los DataFrames de cada archivo
todos_los_dataframes = []

if os.path.exists(carpeta_entrada):
    # Recorremos todos los archivos de la carpeta
    for nombre_archivo in os.listdir(carpeta_entrada):
        # Procesamos solo archivos de texto
        if nombre_archivo.lower().endswith(".txt"):
            ruta_completa = os.path.join(carpeta_entrada, nombre_archivo)
            
            with open(ruta_completa, "r", encoding="utf-8") as f:
                contenido_completo = f.read()
            
            # Generar el DataFrame para este archivo específico
            df_temporal = segmentar_contrato_legal(contenido_completo, nombre_archivo)
            
            # Añadirlo a nuestra lista
            todos_los_dataframes.append(df_temporal)
            print(f"Procesado: {nombre_archivo} ({len(df_temporal)} cláusulas)")

    # Si encontramos archivos, los unimos todos en un solo CSV
    if todos_los_dataframes:
        df_final = pd.concat(todos_los_dataframes, ignore_index=True)
        df_final.to_csv(archivo_salida_final, index=False, encoding="utf-8")
        
        print("-" * 30)
        print(f"✅ ¡Proceso completo! Se procesaron {len(todos_los_dataframes)} archivos.")
        print(f"📁 Resultado guardado en: {archivo_salida_final}")
        print(f"Total de cláusulas extraídas: {len(df_final)}")
    else:
        print("No se encontraron archivos .txt en la carpeta especificada.")
else:
    print(f"La carpeta '{carpeta_entrada}' no existe.")