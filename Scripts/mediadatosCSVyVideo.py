import json
import csv
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
from datetime import datetime

# Mapeo de fases específicas a fases agrupadas
FASE_MAP = {
    "Heel strike - Loading response": "LR",
    "Mid-stance": "MSt",
    "Terminal stance": "TSt",
    "Pre-swing": "PSw",
    "Toe-off": "Sw",
    "Mid-swing": "Sw",
    "Terminal swing": "Sw"
}

# Convertir duración tipo "MM:SS.ffffff" a milisegundos
def duracion_a_milisegundos(duracion_str):
    try:
        t = datetime.strptime(duracion_str, "%M:%S.%f")
        return t.minute * 60000 + t.second * 1000 + int(t.microsecond / 1000)
    except ValueError:
        return 0

def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Selecciona el archivo JSON",
        filetypes=[("Archivos JSON", "*.json")]
    )

def guardar_archivo_csv():
    root = tk.Tk()
    root.withdraw()
    return filedialog.asksaveasfilename(
        title="Guardar resultados como CSV",
        defaultextension=".csv",
        filetypes=[("Archivo CSV", "*.csv")]
    )

def calcular_medias_por_metodo(path_entrada):
    with open(path_entrada, "r", encoding="utf-8") as f:
        data = json.load(f)

    acumulador = {
        "CSV": defaultdict(float),
        "Video": defaultdict(float)
    }
    conteo_zancadas = {
        "CSV": 0,
        "Video": 0
    }

    for zancada in data:
        for metodo in ["CSV", "Video"]:
            fases = zancada.get("Métodos", {}).get(metodo, [])
            if not fases:
                continue

            suma_duracion = 0
            fases_agregadas = defaultdict(float)

            for fase in fases:
                nombre_fase = fase.get("Fase")
                duracion_str = fase.get("Duración_fase", "00:00.000000")
                duracion_ms = duracion_a_milisegundos(duracion_str)
                suma_duracion += duracion_ms

                fase_agrupada = FASE_MAP.get(nombre_fase)
                if fase_agrupada:
                    fases_agregadas[fase_agrupada] += duracion_ms

            if suma_duracion > 0:
                conteo_zancadas[metodo] += 1
                for fase, duracion in fases_agregadas.items():
                    acumulador[metodo][fase] += duracion

    resultados = {}
    for metodo in ["CSV", "Video"]:
        n = conteo_zancadas[metodo]
        if n == 0:
            continue
        resultados[metodo] = {
            fase: round(total / n, 2)
            for fase, total in acumulador[metodo].items()
        }
        resultados[metodo]["Zancadas válidas"] = n

    return resultados

# Ejecución principal
if __name__ == "__main__":
    ruta_entrada = seleccionar_archivo()
    if not ruta_entrada:
        print("No se seleccionó ningún archivo.")
        exit()

    resultados = calcular_medias_por_metodo(ruta_entrada)

    ruta_salida = guardar_archivo_csv()
    if not ruta_salida:
        print("No se seleccionó ubicación para guardar.")
        exit()

    with open(ruta_salida, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Método", "Fase", "Duración media (ms)"])
        for metodo, datos in resultados.items():
            for fase, valor in datos.items():
                if fase != "Zancadas válidas":
                    writer.writerow([metodo, fase, valor])
            writer.writerow([metodo, "Zancadas válidas", datos["Zancadas válidas"]])
            writer.writerow([])

    print(f"✅ Resultados guardados en: {ruta_salida}")
