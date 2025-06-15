import pandas as pd
import numpy as np
from scipy.signal import find_peaks

# --- Funciones de utilidad ---
def tiempo_a_segundos(tiempo_str):
    minutos, resto = tiempo_str.split(":")
    segundos, milisegundos = resto.split(".")
    return int(minutos) * 60 + int(segundos) + int(milisegundos) / 1000

def formato_tiempo(segundos):
    minutos = int(segundos // 60)
    segundos_resto = int(segundos % 60)
    milisegundos = int(round((segundos - int(segundos)) * 1000))
    return f"{minutos:02}:{segundos_resto:02}.{milisegundos:03}"

# --- Cargar datos ---
df = pd.read_csv("archivo_con_tiempo_formateado_R_Sebas.csv")
df["Tiempo_s"] = df["Tiempo (mm:ss.mmm)"].apply(tiempo_a_segundos)

# --- Señal de sensores del talón ---
talon_signal = df["PressureSensor 20"] + df["PressureSensor 16"] + df["PressureSensor 23"]

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

# --- Guardar archivo ---
zancadas_formateado.to_csv("zancadas_detectadas_R_Sebas.csv", index=False)

print("Archivo 'zancadas_detectadas.csv' guardado con tiempos formateados.")

