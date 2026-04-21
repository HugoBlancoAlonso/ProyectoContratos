# Proyecto de Analisis de Clausulas Contractuales

Este repositorio procesa contratos de arrendamiento en español para:

1. Extraer texto desde PDF.
2. Segmentar clausulas.
3. Analizar similitud semantica contra un diccionario legal/no legal.
4. Marcar clausulas con posible abusividad y generar justificacion.
5. Ejecutar analisis exploratorio (EDA) y pre-anotacion NER basica.

## Estado actual del proyecto

- El flujo principal de clasificacion esta en src/motorDeSimilaridad.py.
- Hay 2 flujos de preparacion de datos:
1. Archivo unico: src/ArchivoUnico
2. Multiples archivos: src/MultiplesArchivos
- El directorio app/ esta vacio actualmente.

## Estructura relevante

- src/ArchivoUnico/extraccionTexto.py: extrae y limpia texto desde un PDF.
- src/ArchivoUnico/creacionBaseClausulas.py: segmenta texto limpio en clausulas CSV.
- src/MultiplesArchivos/extraccionTextoMULT.py: extrae y limpia varios PDF.
- src/MultiplesArchivos/creacionBaseClausulasMULT.py: crea base consolidada desde varios TXT.
- src/motorDeSimilaridad.py: indexa clausulas de referencia en Chroma y analiza contrato.
- src/eda.py: estadisticas y graficas del corpus segmentado.
- src/ner.py: pre-anotacion de entidades con spaCy Matcher.
- data/clausulas.json: base de referencia legal/no legal.
- data/contratosParaAnalizar/clausulas_contrato.csv: entrada principal del motor de similitud.

## Requisitos

- Windows (probado), Linux o macOS.
- Python 3.10 o superior (recomendado 3.10-3.12).
- Conexion a internet en la primera ejecucion para descargar modelos.

## Instalacion

Desde la raiz del proyecto, crea entorno virtual e instala dependencias.

### PowerShell (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pandas chromadb sentence-transformers spacy pymupdf matplotlib seaborn
python -m spacy download es_core_news_sm
```

### Bash (Linux/macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pandas chromadb sentence-transformers spacy pymupdf matplotlib seaborn
python -m spacy download es_core_news_sm
```

## Flujo de ejecucion recomendado

Importante: ejecuta siempre los scripts desde la raiz del repositorio para que las rutas relativas funcionen.

### Opcion A: Analizar un solo contrato PDF

1. Coloca el contrato en data/contratosParaAnalizar/ con nombre contrato.pdf.
2. Extrae texto limpio:

```powershell
python src/ArchivoUnico/extraccionTexto.py
```

3. Segmenta clausulas:

```powershell
python src/ArchivoUnico/creacionBaseClausulas.py
```

4. Ejecuta analisis de similitud y dictamen:

```powershell
python src/motorDeSimilaridad.py
```

Salida principal:
- data/prediccionAbusividad.csv

### Opcion B: Procesar multiples contratos

1. Coloca todos los PDF en data/contratos/
2. Extrae texto de todos los PDF:

```powershell
python src/MultiplesArchivos/extraccionTextoMULT.py
```

3. Crea base consolidada de clausulas:

```powershell
python src/MultiplesArchivos/creacionBaseClausulasMULT.py
```

Salida principal:
- data/base_clausulas.csv

## Analisis exploratorio (opcional)

Genera resumen estadistico y graficas desde data/base_clausulas.csv:

```powershell
python src/eda.py
```

Archivos generados:
- data/eda_longitud.png
- data/eda_frecuencia.png

## NER basico (opcional)

Ejecuta patrones para montos, duracion, jurisdiccion y partes:

```powershell
python src/ner.py
```

Nota: src/ner.py actualmente apunta por defecto a data/contratosLimpios/contrato_limpio_completo2.txt. Si quieres otro archivo, cambia la variable ruta_archivo dentro del script.

## Base vectorial ChromaDB

El motor usa persistencia local en chroma_db/.

- Primera ejecucion: indexa data/clausulas.json.
- Ejecuciones siguientes: reutiliza la base existente.

Si cambias estructura o metadatos en data/clausulas.json (por ejemplo, agregas explicacion/justificacion), elimina la carpeta chroma_db y vuelve a ejecutar:

```powershell
Remove-Item -Recurse -Force chroma_db
python src/motorDeSimilaridad.py
```

## Formato esperado de datos

### Entrada del motor de similitud

Archivo: data/contratosParaAnalizar/clausulas_contrato.csv

Columnas minimas requeridas:
- titulo
- contenido

### Diccionario de referencia

Archivo: data/clausulas.json

Estructura por entrada:
- valor: boolean (true/false)
- ejemplo: string
- explicacion: string opcional (recomendado para casos no legales)

## Solucion de problemas

1. Error con spaCy model not found:

```powershell
python -m spacy download es_core_news_sm
```

2. Error de rutas (archivo no encontrado):
- Verifica que estas en la raiz del proyecto al ejecutar los scripts.

3. Error al importar fitz:

```powershell
pip install pymupdf
```

4. Chroma no refleja cambios del JSON:
- Borra chroma_db y vuelve a correr src/motorDeSimilaridad.py.

## Roadmap de documentacion

Este README es la base inicial. En futuras iteraciones se puede ampliar con:

1. requirements.txt o pyproject.toml.
2. Script unico de orquestacion del pipeline.
3. Pruebas automatizadas.
4. App interactiva en la carpeta app/.

