import json
import csv
from datetime import datetime
from scipy.signal import find_peaks
import tkinter as tk
from tkinter import filedialog, messagebox

# ---------- INTERFAZ DE ARCHIVOS ----------
root = tk.Tk()
root.withdraw()

entrada_json = filedialog.askopenfilename(
    title="Selecciona el archivo JSON con datos y timestamps",
    filetypes=[("JSON files", "*.json")]
)
if not entrada_json:
    messagebox.showerror("Error", "No se seleccionó ningún archivo de entrada.")
    raise SystemExit

salida_json = filedialog.asksaveasfilename(
    title="Guardar archivo JSON de salida",
    defaultextension=".json",
    filetypes=[("JSON files", "*.json")],
    initialfile="zancadas_integradas.json"
)
if not salida_json:
    messagebox.showerror("Error", "No se seleccionó dónde guardar el archivo JSON.")
    raise SystemExit

salida_csv = filedialog.asksaveasfilename(
    title="Guardar archivo CSV resumen",
    defaultextension=".csv",
    filetypes=[("CSV files", "*.csv")],
    initialfile="zancadas_integradas.csv"
)
if not salida_csv:
    messagebox.showerror("Error", "No se seleccionó dónde guardar el archivo CSV.")
    raise SystemExit

# ---------- CONFIGURACIÓN ----------
umbral_pico_LR = 0.90
distancia_minima = 50  # muestras
fases_orden = ["LR", "MSt", "TSt", "PSw", "Sw"]

# ---------- FUNCIONES ----------
def ts_to_sec(ts):
    dt = datetime.strptime(ts, "%M:%S.%f")
    return dt.minute * 60 + dt.second + dt.microsecond / 1e6

def integrar_fase(tiempos, valores):
    return sum(
        (valores[i] + valores[i+1]) / 2 * (tiempos[i+1] - tiempos[i])
        for i in range(len(tiempos) - 1)
    )

# ---------- CARGAR DATOS ----------
with open(entrada_json, 'r') as f:
    data = json.load(f)

lr_values = [frame["phases"]["LR"] for frame in data]
timestamps = [frame["TimeStamp"] for frame in data]
times_sec = [ts_to_sec(ts) for ts in timestamps]

# ---------- DETECTAR PUNTOS DE INICIO ----------
picos_detectados, _ = find_peaks(lr_values, height=umbral_pico_LR, distance=distancia_minima)

# ---------- PROCESAR ZANCADAS ----------
zancadas = []
descartadas = 0

for i in range(len(picos_detectados) - 1):
    idx_ini, idx_fin = picos_detectados[i], picos_detectados[i + 1]
    t_ini = times_sec[idx_ini]
    t_fin = times_sec[idx_fin]
    dur_total = t_fin - t_ini

    if dur_total < 0.5 or dur_total > 2.5:
        descartadas += 1
        continue

    segmento = data[idx_ini:idx_fin + 1]
    tiempo_segmento = [ts_to_sec(f["TimeStamp"]) for f in segmento]

    fase_duraciones = []
    for fase in fases_orden:
        valores = [f["phases"][fase] for f in segmento]
        dur = integrar_fase(tiempo_segmento, valores)
        fase_duraciones.append((fase, round(dur, 4)))

    zancadas.append({
        "Numero_zancada": len(zancadas) + 1,
        "Tiempo_inicio": timestamps[idx_ini],
        "Tiempo_final": timestamps[idx_fin],
        "Tiempo_zancada": round(dur_total, 4),
        "Fases": {
            fase: {
                "Duracion": dur
            } for fase, dur in fase_duraciones
        }
    })

# ---------- GUARDAR ARCHIVOS ----------
with open(salida_json, "w") as f:
    json.dump(zancadas, f, indent=4)

with open(salida_csv, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Zancada", "Inicio", "Fin", "Duración"] + [f"{f}_dur" for f in fases_orden])
    for z in zancadas:
        row = [
            z["Numero_zancada"],
            z["Tiempo_inicio"],
            z["Tiempo_final"],
            z["Tiempo_zancada"]
        ] + [z["Fases"][f]["Duracion"] for f in fases_orden]
        writer.writerow(row)

# ---------- MENSAJE FINAL ----------
messagebox.showinfo("Exportación completa", f"""
✅ Exportado correctamente:

- JSON: {salida_json}
- CSV: {salida_csv}

Zancadas válidas: {len(zancadas)} / {len(picos_detectados) - 1}
Zancadas descartadas por duración: {descartadas}
""")

