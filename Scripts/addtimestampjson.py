import pandas as pd
import json
import tkinter as tk
from tkinter import filedialog

# --- Configurar interfaz gráfica ---
root = tk.Tk()
root.withdraw()

# --- Selección de archivo CSV ---
csv_path = filedialog.askopenfilename(
    title="Selecciona el archivo CSV con timestamps",
    filetypes=[("CSV files", "*.csv")]
)
if not csv_path:
    raise Exception("No se seleccionó ningún archivo CSV.")

# --- Selección de archivo JSON ---
json_path = filedialog.askopenfilename(
    title="Selecciona el archivo JSON con datos de gait",
    filetypes=[("JSON files", "*.json")]
)
if not json_path:
    raise Exception("No se seleccionó ningún archivo JSON.")

# --- Cargar archivos ---
csv_data = pd.read_csv(csv_path, header=None)
with open(json_path, 'r') as file:
    json_data = json.load(file)

# --- Obtener timestamps desde la última columna del CSV ---
timestamps = csv_data.iloc[:, -1].tolist()

# --- Añadir timestamps al JSON ---
for idx, record in enumerate(json_data):
    if idx < len(timestamps):
        record['TimeStamp'] = timestamps[idx]

# --- Selección de ruta para guardar el JSON modificado ---
modified_json_path = filedialog.asksaveasfilename(
    title="Guardar archivo JSON modificado",
    defaultextension=".json",
    filetypes=[("JSON files", "*.json")],
    initialfile="gait_con_timestamp.json"
)
if not modified_json_path:
    raise Exception("No se seleccionó una ruta de guardado.")

# --- Guardar JSON modificado ---
with open(modified_json_path, 'w') as file:
    json.dump(json_data, file, indent=4)

print(f"Archivo modificado guardado en: {modified_json_path}")
