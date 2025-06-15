import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

# --- Funciones de utilidad ---
def tiempo_a_segundos(tiempo_str):
    minutos, resto = tiempo_str.split(":")
    segundos, microsegundos = resto.split(".")
    return int(minutos) * 60 + int(segundos) + int(microsegundos) / 1_000_000

def formato_tiempo(segundos):
    minutos = int(segundos // 60)
    segundos_resto = int(segundos % 60)
    microsegundos = int(round((segundos - int(segundos)) * 1_000_000))
    return f"{minutos:02}:{segundos_resto:02}.{microsegundos:06}"

# --- Ventana para seleccionar archivo de entrada ---
root = tk.Tk()
root.withdraw()
archivo_csv = filedialog.askopenfilename(
    title="Selecciona el archivo CSV de entrada",
    filetypes=[("CSV files", "*.csv")]
)
if not archivo_csv:
    raise Exception("No se seleccionó ningún archivo de entrada.")

# --- Cargar datos ---
df = pd.read_csv(archivo_csv)
df["Tiempo_s"] = df["Tiempo (mm:ss.mmmuuu)"].apply(tiempo_a_segundos)

# --- Señal de sensores del talón ---
talon_signal = (
    0.6 * df["PressureSensor 27"] +
    0.2 * df["PressureSensor 30"] +
    0.1 * df["PressureSensor 24"] +
    0.1 * df["PressureSensor 31"]
)

# --- Detección de golpes de talón ---
umbral = np.mean(talon_signal) + 1 * np.std(talon_signal)
picos, _ = find_peaks(talon_signal, height=umbral, distance=10)
tiempos = df.loc[picos, "Tiempo_s"].reset_index(drop=True)

# --- Crear DataFrame formateado ---
inicio = tiempos[:-1].values
fin = tiempos[1:].values
duracion = fin - inicio

zancadas_formateado = pd.DataFrame({
    "Inicio_zancada": [formato_tiempo(t) for t in inicio],
    "Fin_zancada": [formato_tiempo(t) for t in fin],
    "Duración_zancada": [formato_tiempo(d) for d in duracion]
})

# --- Ventana para guardar archivo de salida ---
archivo_salida = filedialog.asksaveasfilename(
    title="Guardar archivo de zancadas detectadas",
    defaultextension=".csv",
    filetypes=[("CSV files", "*.csv")],
    initialfile="zancadas_detectadas.csv"
)
if not archivo_salida:
    raise Exception("No se seleccionó una ruta de guardado.")

# --- Guardar archivo ---
zancadas_formateado.to_csv(archivo_salida, index=False)
print(f"Archivo guardado en: {archivo_salida}")

# --- Visualización ---
plt.figure(figsize=(14, 6))
plt.plot(df["Tiempo_s"], talon_signal, label="Señal talón", color="blue")
plt.plot(df.loc[picos, "Tiempo_s"], talon_signal[picos], "rx", label="Picos detectados")

# Anotar los tiempos en formato mm:ss.mmmuuu junto a cada pico
for idx in range(len(picos)):
    x = df.loc[picos[idx], "Tiempo_s"]
    y = talon_signal[picos[idx]]
    tiempo_formateado = formato_tiempo(x)
    plt.text(x, y + 0.05, tiempo_formateado, fontsize=8, rotation=45, ha='left', va='bottom')

plt.xlabel("Tiempo (s)")
plt.ylabel("Presión")
plt.title("Golpes de talón detectados con time_stamp")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("grafica_golpes_talon.png")
plt.show()

