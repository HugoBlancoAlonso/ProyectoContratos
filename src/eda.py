import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

# 1. Cargar los datos
df = pd.read_csv("data/base_clausulas.csv")

# Configuración estética
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [10, 6]

# --- ANÁLISIS 1: Longitud de las Cláusulas ---
# Esto nos ayuda a identificar qué partes del contrato son más densas
def graficar_longitudes(df):
    plt.figure()
    sns.barplot(data=df, x="titulo", y="longitud", palette="viridis")
    plt.xticks(rotation=45)
    plt.title("Longitud de las Cláusulas (Caracteres)")
    plt.xlabel("Cláusula")
    plt.ylabel("Número de Caracteres")
    plt.tight_layout()
    plt.savefig("data/eda_longitud.png")
    print("✅ Gráfico de longitud guardado.")

# --- ANÁLISIS 2: Análisis de Términos Frecuentes (NLP Básico) ---
def analizar_frecuencia_palabras(df):
    texto_total = " ".join(df["contenido"]).lower()
    # Limpieza rápida: solo palabras de más de 3 letras que no sean ruidos comunes
    palabras = re.findall(r'\b[a-z]{4,}\b', texto_total)
    
    # Lista de stop-words básicas en español para el EDA
    stop_words = {'para', 'este', 'esta', 'con', 'que', 'las', 'los', 'del', 'por', 'una', 'como'}
    palabras_filtradas = [p for p in palabras if p not in stop_words]
    
    comunes = Counter(palabras_filtradas).most_common(15)
    
    # Convertir a DataFrame para graficar
    df_comunes = pd.DataFrame(comunes, columns=['Palabra', 'Frecuencia'])
    
    plt.figure()
    sns.barplot(data=df_comunes, x="Frecuencia", y="Palabra", palette="magma")
    plt.title("Top 15 Palabras más Frecuentes en el Contrato")
    plt.tight_layout()
    plt.savefig("data/eda_frecuencia.png")
    print("✅ Gráfico de frecuencia guardado.")

# Ejecutar análisis
graficar_longitudes(df)
analizar_frecuencia_palabras(df)

# --- ANÁLISIS 3: Resumen Estadístico ---
print("\n--- Resumen del Corpus ---")
print(f"Total de cláusulas analizadas: {len(df)}")
print(f"Promedio de longitud: {df['longitud'].mean():.2f} caracteres")
print(f"Cláusula más extensa: {df.loc[df['longitud'].idxmax(), 'titulo']}")