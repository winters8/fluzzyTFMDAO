import pandas as pd
from datetime import timedelta
import re
import json
import tkinter as tk
from tkinter import filedialog

# --- Inicializar ventana de selección ---
root = tk.Tk()
root.withdraw()

# --- Seleccionar archivo CSV de entrada ---
archivo_entrada = filedialog.askopenfilename(
    title="Selecciona el archivo CSV con las zancadas",
    filetypes=[("CSV files", "*.csv")]
)
if not archivo_entrada:
    raise Exception("No se seleccionó un archivo CSV.")

# Fases del ciclo de marcha con sus porcentajes
phases = [
    ("Heel strike - Loading response", 0.10),
    ("Mid-stance", 0.20),
    ("Terminal stance", 0.20),
    ("Pre-swing", 0.10),
    ("Toe-off", 0.13),
    ("Mid-swing", 0.14),
    ("Terminal swing", 0.13),
]

# Convierte string "MM:SS.mmmuuu" a timedelta
def safe_str_to_timedelta(time_str):
    match = re.match(r"(\d{2}):(\d{2})\.(\d{1,6})", str(time_str))
    if not match:
        return None
    minutes, seconds, micros_str = match.groups()
    micros_str = micros_str.ljust(6, '0')  # Rellenar a 6 dígitos
    microseconds = int(micros_str)
    return timedelta(
        minutes=int(minutes),
        seconds=int(seconds),
        microseconds=microseconds
    )

# Convierte timedelta a string "MM:SS.mmmuuu"
def format_timedelta(td):
    if td is None:
        return ""
    total_seconds = td.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    microseconds = int((total_seconds - minutes * 60 - seconds) * 1_000_000)
    return f"{minutes:02}:{seconds:02}.{microseconds:06}"

# Calcula fases con inicio, fin y duración
def calcular_fases(inicio_str, duracion_str, metodo, zancada):
    inicio = safe_str_to_timedelta(inicio_str)
    duracion = safe_str_to_timedelta(duracion_str)
    if inicio is None or duracion is None:
        return []
    
    fases = []
    tiempo_actual = inicio
    for nombre, porcentaje in phases:
        duracion_fase = duracion * porcentaje
        fin_fase = tiempo_actual + duracion_fase
        fases.append({
            "Zancada": zancada,
            "Método": metodo,
            "Fase": nombre,
            "Inicio_fase": tiempo_actual,
            "Fin_fase": fin_fase,
            "Duración_fase": duracion_fase
        })
        tiempo_actual = fin_fase
    return fases

# --- Cargar archivo CSV original ---
df = pd.read_csv(archivo_entrada)

# 🔍 FILTRAR: excluir zancadas con observación "gira"
df = df[df["observacion"].str.lower() != "gira"]

# Lista de fases detalladas para el CSV
datos_fases = []

# Calcular fases para cada fila
for _, row in df.iterrows():
    zancada = row['Zancada']
    inicio_csv = row['Inicio_zancada_CSV']
    duracion_csv = row['Duración_zancada_CSV']
    inicio_video = row['tiempo_incio_envideo']
    duracion_video = row['Duración_zancada_video']
    
    for fase in calcular_fases(inicio_csv, duracion_csv, "CSV", zancada):
        fase.update({
            "Inicio_zancada_CSV": inicio_csv,
            "Duración_zancada_CSV": duracion_csv,
            "Inicio_zancada_video": inicio_video,
            "Duración_zancada_video": duracion_video,
        })
        datos_fases.append(fase)

    for fase in calcular_fases(inicio_video, duracion_video, "Video", zancada):
        fase.update({
            "Inicio_zancada_CSV": inicio_csv,
            "Duración_zancada_CSV": duracion_csv,
            "Inicio_zancada_video": inicio_video,
            "Duración_zancada_video": duracion_video,
        })
        datos_fases.append(fase)

# Crear DataFrame de fases
df_fases = pd.DataFrame(datos_fases)

# Formatear columnas de tiempo
for col in ['Inicio_fase', 'Fin_fase', 'Duración_fase']:
    df_fases[col] = df_fases[col].apply(format_timedelta)

# --- Guardar CSV con fases detalladas ---
archivo_csv = filedialog.asksaveasfilename(
    title="Guardar archivo CSV con fases detalladas",
    defaultextension=".csv",
    filetypes=[("CSV files", "*.csv")],
    initialfile="fases_detalladas.csv"
)
if not archivo_csv:
    raise Exception("No se seleccionó ruta de guardado para el CSV.")

df_fases.to_csv(archivo_csv, index=False)
print(f"✅ CSV guardado: {archivo_csv}")

# --- Crear JSON jerárquico: zancada → métodos → fases ---
zancadas_json = []
for zancada, group in df_fases.groupby('Zancada'):
    datos_zancada = {
        "Zancada": int(zancada),
        "Inicio_zancada_CSV": group["Inicio_zancada_CSV"].iloc[0],
        "Duración_zancada_CSV": group["Duración_zancada_CSV"].iloc[0],
        "Inicio_zancada_video": group["Inicio_zancada_video"].iloc[0],
        "Duración_zancada_video": group["Duración_zancada_video"].iloc[0],
        "Métodos": {}
    }
    for metodo, subgrupo in group.groupby("Método"):
        fases = subgrupo[["Fase", "Inicio_fase", "Fin_fase", "Duración_fase"]].to_dict(orient='records')
        datos_zancada["Métodos"][metodo] = fases
    zancadas_json.append(datos_zancada)

# --- Guardar JSON jerárquico ---
archivo_json = filedialog.asksaveasfilename(
    title="Guardar archivo JSON jerárquico de fases",
    defaultextension=".json",
    filetypes=[("JSON files", "*.json")],
    initialfile="zancadas_con_fases.json"
)
if not archivo_json:
    raise Exception("No se seleccionó ruta de guardado para el JSON.")

with open(archivo_json, "w", encoding="utf-8") as f:
    json.dump(zancadas_json, f, ensure_ascii=False, indent=2)

print(f"✅ JSON jerárquico guardado: {archivo_json}")
