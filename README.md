# Proyecto de Analisis de Clausulas Contractuales

Aplicacion para subir un contrato PDF, extraer y segmentar clausulas, analizar abusividad con similitud semantica y mostrar resultados en Streamlit.

## Estructura actual

- [app/streamlit_app.py](app/streamlit_app.py): interfaz principal de Streamlit.
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

1. El usuario sube un PDF.
2. Se guarda en [data/contratosParaAnalizar/contrato.pdf](data/contratosParaAnalizar/contrato.pdf).
3. Se ejecuta [src/pipeline/single_file/extraccionTexto.py](src/pipeline/single_file/extraccionTexto.py).
4. Se ejecuta [src/pipeline/single_file/creacionBaseClausulas.py](src/pipeline/single_file/creacionBaseClausulas.py).
5. Se ejecuta [src/analysis/ner.py](src/analysis/ner.py).
6. Se ejecuta [src/analysis/motorDeSimilaridad.py](src/analysis/motorDeSimilaridad.py).
7. Streamlit lee [data/prediccionAbusividad.csv](data/prediccionAbusividad.csv) y genera el EDA dinámico en pantalla.

## Requisitos

- Windows, Linux o macOS.
- Python 3.10 o superior.
- Conectividad a internet en la primera ejecucion para descargar modelos de spaCy y SentenceTransformers.

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pandas chromadb sentence-transformers spacy pymupdf matplotlib seaborn streamlit
python -m spacy download es_core_news_sm
```

## Ejecucion correcta

No ejecutes la app como script de Python. Streamlit debe arrancarse asi:

```powershell
python -m streamlit run app/streamlit_app.py
```

Si usas directamente el ejecutable de Python:

```powershell
c:\python313\python.exe -m streamlit run app\streamlit_app.py
```

El mensaje `missing ScriptRunContext` aparece cuando ejecutas Streamlit como un script normal, por ejemplo con `python app/streamlit_app.py`. Eso no es el modo correcto.

## Salidas generadas

- [data/contratosParaAnalizar/contrato_limpio.txt](data/contratosParaAnalizar/contrato_limpio.txt): texto limpio extraido.
- [data/contratosParaAnalizar/clausulas_contrato.csv](data/contratosParaAnalizar/clausulas_contrato.csv): clausulas segmentadas.
- [data/prediccionAbusividad.csv](data/prediccionAbusividad.csv): dictamen final por clausula.

## Notas sobre ChromaDB

- La primera ejecucion crea o actualiza la base en [chroma_db/](chroma_db).
- Si cambias [data/clausulas.json](data/clausulas.json), elimina [chroma_db/](chroma_db) para forzar un reindexado.

## Solucion de problemas

1. Si falta spaCy en español:

```powershell
python -m spacy download es_core_news_sm
```

2. Si falla la libreria PyMuPDF:

```powershell
pip install pymupdf
```

3. Si Streamlit no abre en el navegador:
- Usa `python -m streamlit run app/streamlit_app.py` desde la raiz del proyecto.

## Estado del proyecto

Actualmente el proyecto esta centrado en la app de Streamlit y en el flujo de analisis de un unico contrato. Las capas de API y generador interactivo se pueden añadir despues sin cambiar este flujo base.

