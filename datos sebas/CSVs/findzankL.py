import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

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
df = pd.read_csv("archivo_con_tiempo_formateado_L_Sebas.csv")
df["Tiempo_s"] = df["Tiempo (mm:ss.mmm)"].apply(tiempo_a_segundos)

# --- Señal de sensores del talón ---
talon_signal = df["PressureSensor 30"] + df["PressureSensor 27"] + df["PressureSensor 24"]

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
"""
# --- Guardar archivo ---
zancadas_formateado.to_csv("zancadas_detectadas_L_Sebas2.csv", index=False)

print("Archivo 'zancadas_detectadas.csv' guardado con tiempos formateados.")
"""
# --- Visualización ---
plt.figure(figsize=(14, 6))
plt.plot(df["Tiempo_s"], talon_signal, label="Señal talón", color="blue")
plt.plot(df.loc[picos, "Tiempo_s"], talon_signal[picos], "rx", label="Picos detectados")

# Anotar los tiempos en formato mm:ss.mmm junto a cada pico
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
plt.show()
plt.savefig("grafica_golpes_talon_R_sebas.png")
