# 📘 Guía Completa API Analizador de Contratos

## ✨ Mejoras v2.0

✅ **Modelos cargados en memoria** - Los modelos se cargan una sola vez al iniciar la API  
✅ **Sin subprocess** - Toda la lógica integrada directamente en FastAPI  
✅ **Múltiples usuarios simultáneos** - La API puede atender varias peticiones a la vez  
✅ **Mejor manejo de errores** - Respuestas HTTP estándar  
✅ **Endpoints de monitoreo** - Verificar estado y salud del sistema  

---

## 🚀 Inicio Rápido

### 1️⃣ Instalar dependencias (si no las tienes)

```bash
pip install fastapi uvicorn python-multipart pandas fitz pymupdf chromadb sentence-transformers
```

### 2️⃣ Iniciar la API

Desde la carpeta raíz del proyecto:

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

**Explicación:**
- `--reload`: La API se reinicia automáticamente si cambias el código (desarrollo)
- `--host 0.0.0.0`: Accesible desde cualquier máquina en la red
- `--port 8000`: Puerto donde corre la API

**Primer inicio:** Puede tardar 1-2 minutos descargando los modelos de HuggingFace

### 3️⃣ Acceder a la API

- 📘 **Documentación interactiva**: http://localhost:8000/docs
- 🧪 **Testing alternativo**: http://localhost:8000/redoc
- 🏥 **Estado**: http://localhost:8000/health
- 📊 **Dashboard**: http://localhost:8000/status

---

## 📡 Endpoints Disponibles

### GET `/` - Información Principal
Retorna info general de la API

**Respuesta:**
```json
{
  "nombre": "API Analizador de Contratos",
  "version": "2.0",
  "estado": "modelos cargados",
  "endpoints": {
    "docs": "/docs",
    "health": "/health",
    "status": "/status",
    "analizar": "/analizar (POST)"
  }
}
```

### GET `/health` - Verificar Salud
Comprueba que todo está corriendo

**Respuesta:**
```json
{
  "status": "ok",
  "modelos_cargados": true,
  "tiempo_uptime": 1234.5
}
```

### GET `/status` - Estado Detallado
Información completa del sistema

**Respuesta:**
```json
{
  "api_status": "healthy",
  "modelos_cargados": true,
  "chroma_db_conectado": true,
  "clausulas_indexadas": 250,
  "tiempo_uptime_segundos": 1234.5,
  "hora_inicio": "2024-01-15T10:30:45"
}
```

### POST `/analizar` - Procesar Contrato
Sube un PDF y obtén el análisis de cláusulas

**Parámetros:**
- `file`: Archivo PDF (multipart/form-data)

**Respuesta:**
```json
{
  "estado": "exito",
  "archivo": "contrato.pdf",
  "clausulas_procesadas": 15,
  "timestamp": "2024-01-15T10:35:20.123456",
  "resultados": [
    {
      "clausula": "Primera",
      "contenido": "Regulación del presente contrato...",
      "dictamen": "✅ LEGAL",
      "confianza": "85.50%",
      "referencia": "Contrato de arrendamiento estándar...",
      "justificacion": "La cláusula coincide con patrones legales válidos.",
      "longitud_original": 245
    },
    {
      "clausula": "Segunda",
      "contenido": "Objeto del arrendamiento...",
      "dictamen": "⚠️ POSIBLE ABUSIVA",
      "confianza": "82.30%",
      "referencia": "Cláusula con restricción excesiva...",
      "justificacion": "Se recomienda revisión legal",
      "longitud_original": 318
    }
  ]
}
```

---

## 🧪 Testing sin Interfaz

### Usando `curl` (Terminal)

```bash
# Test básico
curl http://localhost:8000/

# Revisar salud
curl http://localhost:8000/health

# Analizar contrato
curl -X POST -F "file=@ruta/al/contrato.pdf" http://localhost:8000/analizar
```

### Usando Python

```python
import requests

# Endpoint raíz
response = requests.get("http://localhost:8000/")
print(response.json())

# Salud
response = requests.get("http://localhost:8000/health")
print(response.json())

# Analizar
with open("contrato.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/analizar", files=files)
    resultado = response.json()
    
    print(f"Clausulas procesadas: {resultado['clausulas_procesadas']}")
    for item in resultado['resultados']:
        print(f"{item['clausula']}: {item['dictamen']}")
```

### Usando JavaScript/Fetch

```javascript
// Fetch API
const formData = new FormData();
formData.append("file", document.getElementById("fileInput").files[0]);

fetch("http://localhost:8000/analizar", {
  method: "POST",
  body: formData
})
.then(res => res.json())
.then(data => {
  console.log(`Procesadas: ${data.clausulas_procesadas} cláusulas`);
  data.resultados.forEach(r => {
    console.log(`${r.clausula}: ${r.dictamen}`);
  });
});
```

---

## ⚙️ Configuración y Tuning

### Modificar Umbrales de Confianza

En `app/api.py`, línea ~300:

```python
UMBRAL_LEGAL = 0.50      # Aumentar = más estricto
UMBRAL_ABUSIVO = 0.80    # Aumentar = menos falsos positivos
```

### Cambiar Modelo de Embeddings

En `app/api.py`, línea ~130:

```python
model_name = "paraphrase-multilingual-MiniLM-L12-v2"  # Cambiar a otro
```

**Alternativas recomendadas:**
- `all-MiniLM-L6-v2` - Más rápido, menos preciso
- `all-mpnet-base-v2` - Más lento, más preciso
- `distiluse-base-multilingual-cased-v2` - Multilengua

### Puerto Personalizado

```bash
uvicorn app.api:app --port 9000 --host 0.0.0.0
```

---

## 🔍 Explicación Técnica del Flujo

```
Usuario sube PDF
        ↓
    [FastAPI recibe]
        ↓
1. Extrae texto con PyMuPDF (fitz)
        ↓
2. Limpia y normaliza texto
        ↓
3. Segmenta en cláusulas individuales
        ↓
4. Genera embeddings con SentenceTransformers
        ↓
5. Compara contra ChromaDB (base de referencia)
        ↓
6. Clasifica según reglas de confianza
        ↓
7. Retorna JSON con resultados
```

**Ventajas vs Versión Anterior:**
- ❌ Antes: Cargaba modelos en cada petición (lento)
- ✅ Ahora: Modelos en memoria durante toda la ejecución

---

## 📊 Monitoreo en Producción

### Ver logs de la API
```bash
# Con timestamps
uvicorn app.api:app --log-level info

# Más verboso
uvicorn app.api:app --log-level debug
```

### Revisar carga del sistema
```bash
# En otra terminal
watch -n 1 'curl -s http://localhost:8000/status | python -m json.tool'
```

### Métricas útiles
- `tiempo_uptime_segundos` - Cuánto lleva corriendo
- `clausulas_indexadas` - Cantidad de referencias legales cargadas
- `modelos_cargados` - Estado de los modelos

---

## ❌ Troubleshooting

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: chromadb` | `pip install chromadb` |
| `Port 8000 already in use` | `uvicorn app.api:app --port 9000` |
| `SyntaxError` en API | Verificar encoding UTF-8 en terminal |
| API lenta al analizar | Es normal primera vez, se cachean modelos |
| `CORS error` desde frontend | Ver sección CORS más abajo |

### Habilitar CORS (para frontend remoto)

En `app/api.py`, después de crear la app:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a dominio específico en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔒 Seguridad en Producción

Para desplegar en producción:

```bash
# Usar Gunicorn + Uvicorn (múltiples workers)
gunicorn app.api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# O usar nginx como reverse proxy
# Ver docker-compose más adelante para setup completo
```

---

## 📝 Próximos Pasos

✅ Fase 1 (Actual): API con modelos en memoria  
📋 Fase 2: Dockerizar todo  
📋 Fase 3: Autenticación y rate limiting  
📋 Fase 4: Deploy en producción (AWS/GCP)  

---

**¿Dudas?** Revisar respuestas de endpoints en http://localhost:8000/docs
