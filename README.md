# Proyecto de Analisis de Clausulas Contractuales

Aplicacion para subir un contrato PDF, extraer y segmentar clausulas, analizar abusividad con similitud semantica y mostrar resultados en Streamlit.

## Estructura actual

- [app/streamlit_app.py](app/streamlit_app.py): interfaz principal de Streamlit.
- [app/api.py](app/api.py): Api Rest con FastAPI.
- [src/pipeline/single_file/extraccionTexto.py](src/pipeline/single_file/extraccionTexto.py): extrae texto limpio de un PDF unico.
- [src/pipeline/single_file/creacionBaseClausulas.py](src/pipeline/single_file/creacionBaseClausulas.py): segmenta el texto en clausulas.
- [src/analysis/ner.py](src/analysis/ner.py): pre-anotacion basica con spaCy.
- [src/analysis/motorDeSimilaridad.py](src/analysis/motorDeSimilaridad.py): clasificacion final con ChromaDB.
- [data/clausulas.json](data/clausulas.json): diccionario de referencia legal/no legal.
- [data/contratosParaAnalizar/](data/contratosParaAnalizar): carpeta de entrada y salida intermedia del contrato actual.
- [data/prediccionAbusividad.csv](data/prediccionAbusividad.csv): resultado final del analisis.
- [chroma_db/](chroma_db): base vectorial persistente de ChromaDB.

## Flujo activo

La app de Streamlit hace este proceso:

0.  Activar Streamlit  `python -m streamlit run app/streamlit_app.py `
1. El usuario sube un PDF.
2. Se guarda en [data/contratosParaAnalizar/contrato.pdf](data/contratosParaAnalizar/contrato.pdf).
3. Se ejecuta [src/pipeline/single_file/extraccionTexto.py](src/pipeline/single_file/extraccionTexto.py).
4. Se ejecuta [src/pipeline/single_file/creacionBaseClausulas.py](src/pipeline/single_file/creacionBaseClausulas.py).
5. Se ejecuta [src/analysis/ner.py](src/analysis/ner.py).
6. Se ejecuta [src/analysis/motorDeSimilaridad.py](src/analysis/motorDeSimilaridad.py).
7. Streamlit lee [data/prediccionAbusividad.csv](data/prediccionAbusividad.csv) y genera el EDA dinámico en pantalla.

La Api Rest hace este proceso:

0. Activar API  `python -m uvicorn app.api:app --reload `
1. El usuario accede a `http://127.0.0.1:8000/docs`.
2. Usa el endpoint `POST /analizar`.
3. Sube un contrato PDF desde Swagger o cualquier cliente HTTP.
4. Se guarda en [data/contratosParaAnalizar/contrato.pdf](data/contratosParaAnalizar/contrato.pdf).
5. Se ejecuta [src/pipeline/single_file/extraccionTexto.py](src/pipeline/single_file/extraccionTexto.py).
6. Se ejecuta [src/pipeline/single_file/creacionBaseClausulas.py](src/pipeline/single_file/creacionBaseClausulas.py).
7. Se ejecuta [src/analysis/ner.py](src/analysis/ner.py).
8. Se ejecuta [src/analysis/motorDeSimilaridad.py](src/analysis/motorDeSimilaridad.py).
9. La API lee [data/prediccionAbusividad.csv](data/prediccionAbusividad.csv).
10. Devuelve respuesta JSON con estado del proceso y resultados.

## Requisitos

- Windows, Linux o macOS.
- Python 3.10 o superior.
- Conectividad a internet en la primera ejecucion para descargar modelos de spaCy y SentenceTransformers.

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pandas chromadb sentence-transformers spacy pymupdf matplotlib seaborn streamlit fastapi uvicorn python-multipart
python -m spacy download es_core_news_sm 
```





Desde la carpeta del proyecto, abre dos terminales y ejecuta esto en este orden:

API
python.exe -m uvicorn app.api:app --host 0.0.0.0 --port 8000

Streamlit
python.exe -m streamlit run streamlit_app.py

Si quieres recargar cambios en desarrollo, puedes usar en la API:
python.exe -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000



python -m uvicorn app.api:app --host 0.0.0.0 --port 8000

python -m streamlit run app/streamlit_app.py


python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000