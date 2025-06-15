import json
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from datetime import datetime
import csv

# ---------- Configuración ----------
nombre_json = "git_Sebas_L_timestamp.json"
fases_orden = ["LR", "MSt", "TSt", "PSw", "Sw"]
umbral_pico_LR = 0.9
distancia_minima = 20

# ---------- Cargar datos ----------
with open(nombre_json, 'r') as f:
    data = json.load(f)

lr_values = [frame["phases"]["LR"] for frame in data]
timestamps = [frame["TimeStamp"] for frame in data]

# Convertir timestamps a segundos
def ts_to_sec(ts):
    dt = datetime.strptime(ts, "%M:%S.%f")
    return dt.minute * 60 + dt.second + dt.microsecond / 1e6

times_sec = [ts_to_sec(ts) for ts in timestamps]

# ---------- Detectar zancadas ----------
peaks, _ = find_peaks(lr_values, height=umbral_pico_LR, distance=distancia_minima)
print(f"Se detectaron {len(peaks)} zancadas (según picos de LR):")

zancadas_json = []

for i in range(len(peaks) - 1):
    idx_ini, idx_fin = peaks[i], peaks[i + 1]
    tiempo_inicio = timestamps[idx_ini]
    tiempo_final = timestamps[idx_fin]
    tiempo_zancada = round(times_sec[idx_fin] - times_sec[idx_ini], 4)

    # Fase dominante por frame en esa zancada
    frames = data[idx_ini:idx_fin]
    secuencia = []
    for j, frame in enumerate(frames):
        dominante = max(frame["phases"], key=frame["phases"].get)
        secuencia.append((idx_ini + j, dominante))

    # Agrupar frames consecutivos con misma fase
    agrupadas = []
    if secuencia:
        actual_fase = secuencia[0][1]
        grupo = [secuencia[0][0]]
        for idx, fase in secuencia[1:]:
            if fase == actual_fase:
                grupo.append(idx)
            else:
                agrupadas.append((actual_fase, grupo))
                actual_fase = fase
                grupo = [idx]
        agrupadas.append((actual_fase, grupo))

    # Asignar primeras ocurrencias únicas de cada fase
    fase_info = {}
    ya_vistas = set()
    for fase in fases_orden:
        for f, indices in agrupadas:
            if f == fase and f not in ya_vistas:
                ini_idx = indices[0]
                fin_idx = indices[-1]
                t_ini = timestamps[ini_idx]
                t_fin = timestamps[fin_idx]
                dur = round(times_sec[fin_idx] - times_sec[ini_idx], 4)
                fase_info[fase] = {
                    "Tiempo_inicio": t_ini,
                    "Tiempo_final": t_fin,
                    "Tiempo_total": dur
                }
                ya_vistas.add(f)
                break
        if fase not in fase_info:
            fase_info[fase] = {
                "Tiempo_inicio": tiempo_inicio,
                "Tiempo_final": tiempo_inicio,
                "Tiempo_total": 0.0
            }

    zancadas_json.append({
        "Numero_zancada": i + 1,
        "Tiempo_inicio": tiempo_inicio,
        "Tiempo_final": tiempo_final,
        "Tiempo_zancada": tiempo_zancada,
        "Fases": fase_info
    })

# ---------- Guardar JSON ----------
with open("zancadas_fases_dominancia.json", 'w') as f:
    json.dump(zancadas_json, f, indent=4)

# ---------- Guardar CSV resumen ----------
with open("zancadas_fases_dominancia.csv", 'w', newline='') as f:
    writer = csv.writer(f)
    header = ["Zancada", "Inicio", "Fin", "Duracion"] + [f"{fase}_dur" for fase in fases_orden]
    writer.writerow(header)
    for z in zancadas_json:
        row = [z["Numero_zancada"], z["Tiempo_inicio"], z["Tiempo_final"], z["Tiempo_zancada"]]
        row += [z["Fases"][fase]["Tiempo_total"] for fase in fases_orden]
        writer.writerow(row)

print("✅ Exportado a zancadas_fases_dominancia.json y .csv")
