import pandas as pd
from datetime import datetime
import re
import tkinter as tk
from tkinter import filedialog

# --- Selección de archivos con GUI ---
root = tk.Tk()
root.withdraw()

# --- Selección del archivo CSV de entrada ---
archivo_csv = filedialog.askopenfilename(
    title="Selecciona el archivo CSV con datos de zancadas y video",
    filetypes=[("CSV files", "*.csv")]
)
if not archivo_csv:
    raise Exception("No se seleccionó ningún archivo.")

# --- Cargar el archivo ---
df = pd.read_csv(archivo_csv)

# --- Función para convertir tiempo a timedelta ---
def tiempo_a_timedelta(tiempo_str):
    return datetime.strptime(tiempo_str, "%M:%S.%f") - datetime.strptime("00:00.000", "%M:%S.%f")

# --- Función para corregir tiempos con formato incorrecto tipo '01.03.400' ---
def corregir_formato_tiempo(tiempo):
    if isinstance(tiempo, str) and re.match(r"^\d{2}\.\d{2}\.\d{3}$", tiempo):
        partes = tiempo.split(".")
        return f"{partes[0]}:{partes[1]}.{partes[2]}"
    return tiempo

# --- Formatear timedelta como MM:SS.mmmuuu ---
def formatear_timedelta(td):
    total_us = int(td.total_seconds() * 1_000_000)
    signo = "-" if total_us < 0 else ""
    total_us = abs(total_us)
    minutos = total_us // 60_000_000
    segundos = (total_us % 60_000_000) // 1_000_000
    microsegundos = total_us % 1_000_000
    return f"{signo}{minutos:02}:{segundos:02}.{microsegundos:06}"

# --- Corregir formato en las columnas de tiempo ---
df["tiempo_incio_envideo"] = df["tiempo_incio_envideo"].apply(corregir_formato_tiempo)

# --- Calcular duración de zancada en video ---
df["Duración_zancada_video_td"] = df.apply(
    lambda row: tiempo_a_timedelta(row["tiempo_fin_envideo"]) - tiempo_a_timedelta(row["tiempo_incio_envideo"]),
    axis=1
)

# --- Convertir duración del CSV a timedelta ---
df["Duración_zancada_CSV_td"] = df["Duración_zancada_CSV"].apply(tiempo_a_timedelta)

# --- Calcular la diferencia entre ambas duraciones ---
df["Diferencia_duración_td"] = df["Duración_zancada_video_td"] - df["Duración_zancada_CSV_td"]

# --- Calcular diferencia en porcentaje ---
df["Diferencia_porcentaje_val"] = (
    df["Diferencia_duración_td"].dt.total_seconds() / df["Duración_zancada_CSV_td"].dt.total_seconds()
) * 100
df["Diferencia_porcentaje"] = df["Diferencia_porcentaje_val"].apply(lambda x: f"{x:.2f}%")

# --- Calcular Z-score para zancadas que no sean "gira" ---
sin_giros = df["observacion"] != "gira"
media_dif = df.loc[sin_giros, "Diferencia_duración_td"].dt.total_seconds().mean()
std_dif = df.loc[sin_giros, "Diferencia_duración_td"].dt.total_seconds().std()

df["Z_score_diferencia"] = None  # Inicializar
df.loc[sin_giros, "Z_score_diferencia"] = (
    df.loc[sin_giros, "Diferencia_duración_td"].dt.total_seconds() - media_dif
) / std_dif

# --- Formatear timedelta a string ---
df["Duración_zancada_video"] = df["Duración_zancada_video_td"].apply(formatear_timedelta)
df["Duración_zancada_CSV"] = df["Duración_zancada_CSV_td"].apply(formatear_timedelta)
df["Diferencia_duración"] = df["Diferencia_duración_td"].apply(formatear_timedelta)

# --- Reordenar columnas ---
columnas = list(df.columns)
idx = columnas.index("tiempo_fin_envideo")
for col in ["Duración_zancada_video", "Diferencia_duración"][::-1]:
    columnas.insert(idx + 1, columnas.pop(columnas.index(col)))
df = df[columnas]

# --- Eliminar columnas auxiliares ---
df.drop(columns=[
    "Duración_zancada_video_td",
    "Duración_zancada_CSV_td",
    "Diferencia_duración_td",
    "Diferencia_porcentaje_val"
], inplace=True)

# --- Eliminar filas con observación "gira" ---
df = df[df["observacion"] != "gira"].copy()

# --- Selección del archivo CSV de salida ---
archivo_salida = filedialog.asksaveasfilename(
    title="Guardar archivo CSV con análisis y Z-score",
    defaultextension=".csv",
    filetypes=[("CSV files", "*.csv")],
    initialfile="zancadas_con_zscore_filtrado.csv"
)
if not archivo_salida:
    raise Exception("No se seleccionó una ruta de guardado.")

# --- Guardar archivo resultante ---
df.to_csv(archivo_salida, index=False)
print(f"✅ Archivo exportado como: {archivo_salida}")

