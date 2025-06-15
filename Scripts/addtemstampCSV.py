import pandas as pd
import tkinter as tk
from tkinter import filedialog

# --- Configurar ventana para selección de archivos ---
root = tk.Tk()
root.withdraw()

# --- Selección de archivo CSV de entrada ---
archivo_entrada = filedialog.askopenfilename(
    title="Selecciona el archivo CSV de entrada",
    filetypes=[("CSV files", "*.csv")]
)
if not archivo_entrada:
    raise Exception("No se seleccionó ningún archivo de entrada.")

# --- Cargar el archivo CSV ---
df = pd.read_csv(archivo_entrada)

# --- Frecuencia de muestreo (Hz) ---
sampling_rate = 64
sampling_period = 1 / sampling_rate  # Tiempo entre muestras en segundos

# --- Calcular tiempo como una Serie (para poder usar .apply) ---
tiempo_segundos = pd.Series(df.index * sampling_period)

# --- Convertir a formato mm:ss.mmmuuu (milisegundos y microsegundos) ---
df['Tiempo (mm:ss.mmmuuu)'] = tiempo_segundos.apply(
    lambda x: f"{int(x // 60):02d}:{int(x % 60):02d}.{int((x % 1) * 1_000_000):06d}"
)

# --- Selección de archivo CSV de salida ---
archivo_salida = filedialog.asksaveasfilename(
    title="Guardar archivo con tiempo formateado",
    defaultextension=".csv",
    filetypes=[("CSV files", "*.csv")],
    initialfile="archivo_con_tiempo_formateado.csv"
)
if not archivo_salida:
    raise Exception("No se seleccionó una ruta de guardado.")

# --- Guardar el nuevo archivo CSV ---
df.to_csv(archivo_salida, index=False)
print(f"Archivo guardado con tiempo formateado en: {archivo_salida}")


