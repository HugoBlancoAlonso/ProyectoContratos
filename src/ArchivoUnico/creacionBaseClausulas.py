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
            "titulo": nombre_clausula,
            "contenido": contenido_clausula,
            "longitud": len(contenido_clausula)
        })

    return pd.DataFrame(lista_clausulas)

# --- EJECUCIÓN ---
ruta_archivo = "data/contratosParaAnalizar/contrato_limpio.txt"

if os.path.exists(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido_completo = f.read()
   
    # Generar la base de datos real
    df_clausulas = segmentar_contrato_legal(contenido_completo, "contrato_01.txt")
   
    # Guardar
    df_clausulas.to_csv("data/contratosParaAnalizar/clausulas_contrato.csv", index=False, encoding="utf-8")
    print(f"✅ ¡Ahora sí! Se han extraído {len(df_clausulas)} cláusulas correctamente.")
    print(df_clausulas[['titulo', 'longitud']].head(15)) # Vista rápida

else:
    print("No se encontró el archivo de texto.")