import json
import pandas as pd
from tkinter import filedialog, Tk
import os

def parse_time(t):
    """Convierte MM:SS.mmmuuu a microsegundos sin usar timestamp UNIX"""
    try:
        minutos, resto = t.strip().split(":")
        segundos, micros = resto.split(".")
        total_us = int(minutos) * 60_000_000 + int(segundos) * 1_000_000 + int(micros[:6].ljust(6, '0'))
        return total_us
    except Exception as e:
        raise ValueError(f"Error en tiempo '{t}': {e}")

def main():
    # Ventana para seleccionar archivos
    root = Tk()
    root.withdraw()

    json_path = filedialog.askopenfilename(title="Selecciona el archivo JSON", filetypes=[("JSON files", "*.json")])
    csv_path = filedialog.askopenfilename(title="Selecciona el archivo CSV", filetypes=[("CSV files", "*.csv")])

    if not json_path or not csv_path:
        print("No se seleccionaron archivos.")
        return

    # Cargar archivos
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    csv_data = pd.read_csv(csv_path)

    # Filtrar filas con observación "gira"
    gira_intervals = csv_data[csv_data["observacion"].str.lower() == "gira"]

    # Convertir intervalos a microsegundos
    gira_ranges = []
    for _, row in gira_intervals.iterrows():
        try:
            start = parse_time(row["Inicio_zancada_CSV"])
            end = parse_time(row["Fin_zancada_CSV"])
            gira_ranges.append((start, end))
        except ValueError as e:
            print(f"Saltando fila por error: {e}")

    # Filtrar el JSON original
    filtered_data = []
    for entry in json_data:
        try:
            timestamp_us = parse_time(entry["TimeStamp"])
            if any(start <= timestamp_us <= end for start, end in gira_ranges):
                continue  # Eliminar si está en el rango de una zancada "gira"
            filtered_data.append(entry)
        except ValueError as e:
            print(f"Saltando entrada JSON por error: {e}")

    # Guardar el nuevo JSON
    output_path = os.path.splitext(json_path)[0] + "_filtrado.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, indent=4)

    print(f"Archivo filtrado guardado como: {output_path}")

if __name__ == "__main__":
    main()
