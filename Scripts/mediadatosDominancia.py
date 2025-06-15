import json
import csv
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
import pandas as pd

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

def calcular_medias_por_fase(path_entrada):
    with open(path_entrada, "r") as f:
        data = json.load(f)

    fases_totales = defaultdict(float)
    conteo_zancadas_validas = 0

    for zancada in data:
        if zancada.get("Tiempo_zancada", 0.0) == 0.0:
            continue
        conteo_zancadas_validas += 1
        for fase, detalles in zancada.get("Fases", {}).items():
            fases_totales[fase] += detalles.get("Duracion", 0.0)

    # Convertir segundos a milisegundos
    medias_fases = {
        fase: round((total / conteo_zancadas_validas) * 1000, 2)  # en milisegundos
        for fase, total in fases_totales.items()
    }

    return conteo_zancadas_validas, medias_fases

# Ejecución principal
if __name__ == "__main__":
    ruta_entrada = seleccionar_archivo()
    if not ruta_entrada:
        print("No se seleccionó ningún archivo.")
        exit()

    zancadas_validas, medias = calcular_medias_por_fase(ruta_entrada)

    ruta_salida = guardar_archivo_csv()
    if not ruta_salida:
        print("No se seleccionó ubicación para guardar.")
        exit()

    with open(ruta_salida, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Fase", "Duración media (ms)"])
        for fase, media in medias.items():
            writer.writerow([fase, media])
        writer.writerow([])
        writer.writerow(["Zancadas válidas", zancadas_validas])

    print(f"Resultados guardados en: {ruta_salida}")
  
