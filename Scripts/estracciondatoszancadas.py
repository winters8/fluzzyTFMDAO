import pandas as pd
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def extraer_segmentos_por_zancada(ruta_archivo_registros, ruta_archivo_zancadas, carpeta_salida):
    # Cargar archivos CSV
    df_registros = pd.read_csv(ruta_archivo_registros)
    df_zancadas = pd.read_csv(ruta_archivo_zancadas)

    # Filtrar solo zancadas que NO sean "gira"
    df_zancadas = df_zancadas[df_zancadas["observacion"].str.lower().str.strip() != "gira"]

    # Convertir tiempos a datetime
    df_registros["Tiempo"] = pd.to_datetime(df_registros["Tiempo (mm:ss.mmmuuu)"], format="%M:%S.%f")
    df_zancadas["Inicio_zancada"] = pd.to_datetime(df_zancadas["Inicio_zancada_CSV"], format="%M:%S.%f")
    df_zancadas["Fin_zancada"] = pd.to_datetime(df_zancadas["Fin_zancada_CSV"], format="%M:%S.%f")

    segmentos = []
    for _, row in df_zancadas.iterrows():
        inicio = row["Inicio_zancada"]
        fin = row["Fin_zancada"]
        idx_inicio = df_registros["Tiempo"].sub(inicio).abs().idxmin()
        idx_fin = df_registros["Tiempo"].sub(fin).abs().idxmin()
        idx_inicio_ext = max(0, idx_inicio - 50)
        idx_fin_ext = min(len(df_registros) - 1, idx_fin + 50)
        segmento = df_registros.iloc[idx_inicio_ext:idx_fin_ext + 1].copy()
        segmentos.append(segmento)

    df_resultado = pd.concat(segmentos, ignore_index=True)

    # Crear la columna Tiempo_formateado en formato MM:SS.mmmuuu
    df_resultado["Tiempo_formateado"] = (
        df_resultado["Tiempo"].dt.strftime("%M:%S.") +
        df_resultado["Tiempo"].dt.microsecond.astype(str).str.zfill(6)
    )

    # Crear DataFrame con la columna Tiempo_formateado
    df_con_tiempo = df_resultado.drop(columns=["Tiempo (mm:ss.mmmuuu)", "Tiempo"])
    df_con_tiempo = df_con_tiempo.copy()
    df_con_tiempo["Tiempo_formateado"] = df_resultado["Tiempo_formateado"]

    # Crear DataFrame sin columna Tiempo_formateado
    df_sin_tiempo = df_con_tiempo.drop(columns=["Tiempo_formateado"])

    # Guardar archivos
    os.makedirs(carpeta_salida, exist_ok=True)
    ruta_con_tiempo = os.path.join(carpeta_salida, "con_tiempo.csv")
    ruta_sin_tiempo = os.path.join(carpeta_salida, "sin_tiempo.csv")
    df_con_tiempo.to_csv(ruta_con_tiempo, index=False)
    df_sin_tiempo.to_csv(ruta_sin_tiempo, index=False)

    messagebox.showinfo("Éxito", f"Archivos guardados:\n- {ruta_con_tiempo}\n- {ruta_sin_tiempo}")

def main():
    root = tk.Tk()
    root.withdraw()

    ruta_registros = filedialog.askopenfilename(title="Selecciona el archivo de registros (con tiempo)")
    ruta_zancadas = filedialog.askopenfilename(title="Selecciona el archivo de zancadas")
    carpeta_salida = filedialog.askdirectory(title="Selecciona la carpeta donde guardar los resultados")

    if ruta_registros and ruta_zancadas and carpeta_salida:
        extraer_segmentos_por_zancada(ruta_registros, ruta_zancadas, carpeta_salida)
    else:
        messagebox.showerror("Error", "Debes seleccionar todos los archivos y carpeta para continuar.")

if __name__ == "__main__":
    main()
