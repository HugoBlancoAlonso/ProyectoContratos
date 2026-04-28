from fastapi import FastAPI, UploadFile, File
import shutil
import subprocess
import pandas as pd
import os

app = FastAPI(
    title="API Analizador de Contratos",
    description="Sistema NLP para análisis automático de contratos",
    version="1.0"
)

# -----------------------------------
# Endpoint raíz
# -----------------------------------
@app.get("/")
def home():
    return {
        "mensaje": "API funcionando correctamente"
    }


# -----------------------------------
# Endpoint salud sistema
# -----------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# -----------------------------------
# Endpoint principal
# -----------------------------------
@app.post("/analizar")
async def analizar_contrato(file: UploadFile = File(...)):

    try:
        # Guardar PDF subido
        ruta_pdf = "data/contratosParaAnalizar/contrato.pdf"

        with open(ruta_pdf, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ejecutar pipeline actual
        subprocess.run(["python", "src/ArchivoUnico/extraccionTexto.py"])
        subprocess.run(["python", "src/ArchivoUnico/creacionBaseClausulas.py"])
        subprocess.run(["python", "src/eda.py"])
        subprocess.run(["python", "src/motorDeSimilaridad.py"])

        # Leer resultados
        ruta_csv = "data/prediccionAbusividad.csv"

        if os.path.exists(ruta_csv):
            df = pd.read_csv(ruta_csv)

            return {
                "estado": "ok",
                "filas": len(df),
                "resultados": df.to_dict(orient="records")
            }

        return {
            "estado": "error",
            "mensaje": "No se generó archivo de resultados"
        }

    except Exception as e:
        return {
            "estado": "error",
            "detalle": str(e)
        }
    
#ejecutar uvicorn app.api:app --reload