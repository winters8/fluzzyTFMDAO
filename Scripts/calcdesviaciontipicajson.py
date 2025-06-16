import json
import numpy as np
import tkinter as tk
from tkinter import filedialog
import pandas as pd

# Función para convertir tiempos en formato MM:SS.mmmuuu a segundos
def convertir_a_segundos_csv_video(tiempo):
    minutos, segundos = tiempo.split(':')
    segundos, fraccion = segundos.split('.')
    return float(minutos) * 60 + float(segundos) + float(fraccion) / 1e6

# Función para convertir tiempos en formato S.mmmu a segundos (para dominancia)
def convertir_a_segundos_dominancia(tiempo):
    return float(tiempo)  # En el caso de dominancia, ya está en segundos

# Cargar los datos de los archivos JSON
def cargar_datos(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        return json.load(f)

# Función para calcular la desviación típica de las fases comparadas entre dos archivos
def calcular_desviacion_tipica(dominancia_duraciones, metodo_duraciones):
    # Asegurarnos de que ambas listas sean de tipo float
    dominancia_duraciones = [float(d) for d in dominancia_duraciones]
    metodo_duraciones = [float(d) for d in metodo_duraciones]
    
    # Calcular la desviación típica de las duraciones entre las fases para todas las zancadas
    diferencias = np.array(dominancia_duraciones) - np.array(metodo_duraciones)
    desviacion_tipica = np.std(diferencias)
    
    return desviacion_tipica

# Función para seleccionar un archivo y devolver su ruta
def seleccionar_archivo(title="Selecciona el archivo", filetypes=(("JSON Files", "*.json"),)):
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    archivo = filedialog.askopenfilename(title=title, filetypes=filetypes)
    return archivo

# Función para guardar el archivo CSV
def guardar_csv(data, archivo_salida):
    data.to_csv(archivo_salida, index=False)

# Ejecutar el flujo del programa
if __name__ == "__main__":
    # Seleccionar los archivos JSON
    print("Selecciona el archivo de dominancia (zancadas con fases):")
    archivo_dominancia = seleccionar_archivo("Selecciona el archivo de dominancia (zancadas con fases)")
    print("Selecciona el archivo de zancadas con fases CSV y Video:")
    archivo_csv_video = seleccionar_archivo("Selecciona el archivo de zancadas CSV y Video")

    # Cargar los datos de los archivos
    zancadas_dominancia = cargar_datos(archivo_dominancia)
    zancadas_csv_video = cargar_datos(archivo_csv_video)

    # Crear listas para acumular las duraciones de todas las fases
    duraciones_dominancia_lr = []
    duraciones_metodo_csv_lr = []
    duraciones_metodo_video_lr = []
    
    duraciones_dominancia_mst = []
    duraciones_metodo_csv_mst = []
    duraciones_metodo_video_mst = []

    duraciones_dominancia_tst = []
    duraciones_metodo_csv_tst = []
    duraciones_metodo_video_tst = []

    duraciones_dominancia_psw = []
    duraciones_metodo_csv_psw = []
    duraciones_metodo_video_psw = []

    duraciones_dominancia_sw = []
    duraciones_metodo_csv_sw = []
    duraciones_metodo_video_sw = []

    # Iterar a través de cada zancada de dominancia
    for zancada_dominancia in zancadas_dominancia:
        for zancada_csv_video in zancadas_csv_video:
            if zancada_dominancia['Numero_zancada'] == zancada_csv_video['Zancada']:
                # Fases correspondientes según la correspondencia de las fases
                duraciones_dominancia_lr.append(convertir_a_segundos_dominancia(zancada_dominancia['Fases']['LR']['Duracion']))
                duraciones_metodo_csv_lr.append(convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['CSV'][0]['Duración_fase']))
                duraciones_metodo_video_lr.append(convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['Video'][0]['Duración_fase']))

                duraciones_dominancia_mst.append(convertir_a_segundos_dominancia(zancada_dominancia['Fases']['MSt']['Duracion']))
                duraciones_metodo_csv_mst.append(convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['CSV'][1]['Duración_fase']))
                duraciones_metodo_video_mst.append(convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['Video'][1]['Duración_fase']))

                duraciones_dominancia_tst.append(convertir_a_segundos_dominancia(zancada_dominancia['Fases']['TSt']['Duracion']))
                duraciones_metodo_csv_tst.append(convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['CSV'][2]['Duración_fase']))
                duraciones_metodo_video_tst.append(convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['Video'][2]['Duración_fase']))

                duraciones_dominancia_psw.append(convertir_a_segundos_dominancia(zancada_dominancia['Fases']['PSw']['Duracion']))
                duraciones_metodo_csv_psw.append(convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['CSV'][3]['Duración_fase']))
                duraciones_metodo_video_psw.append(convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['Video'][3]['Duración_fase']))

                # Para la fase Sw, sumamos Toe-off, Mid-swing y Terminal swing
                duraciones_dominancia_sw.append(
                    convertir_a_segundos_dominancia(zancada_dominancia['Fases']['PSw']['Duracion']) + convertir_a_segundos_dominancia(zancada_dominancia['Fases']['MSt']['Duracion'])
                    + convertir_a_segundos_dominancia(zancada_dominancia['Fases']['TSt']['Duracion']))
                duraciones_metodo_csv_sw.append(
                    convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['CSV'][4]['Duración_fase']) + convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['CSV'][5]['Duración_fase']) + convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['CSV'][6]['Duración_fase']))
                duraciones_metodo_video_sw.append(
                    convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['Video'][4]['Duración_fase']) + convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['Video'][5]['Duración_fase']) + convertir_a_segundos_csv_video(zancada_csv_video['Métodos']['Video'][6]['Duración_fase']))

    # Calcular la desviación típica para cada fase
    desviacion_lr_csv = calcular_desviacion_tipica(duraciones_dominancia_lr, duraciones_metodo_csv_lr)
    desviacion_lr_video = calcular_desviacion_tipica(duraciones_dominancia_lr, duraciones_metodo_video_lr)

    desviacion_mst_csv = calcular_desviacion_tipica(duraciones_dominancia_mst, duraciones_metodo_csv_mst)
    desviacion_mst_video = calcular_desviacion_tipica(duraciones_dominancia_mst, duraciones_metodo_video_mst)

    desviacion_tst_csv = calcular_desviacion_tipica(duraciones_dominancia_tst, duraciones_metodo_csv_tst)
    desviacion_tst_video = calcular_desviacion_tipica(duraciones_dominancia_tst, duraciones_metodo_video_tst)

    desviacion_psw_csv = calcular_desviacion_tipica(duraciones_dominancia_psw, duraciones_metodo_csv_psw)
    desviacion_psw_video = calcular_desviacion_tipica(duraciones_dominancia_psw, duraciones_metodo_video_psw)

    desviacion_sw_csv = calcular_desviacion_tipica(duraciones_dominancia_sw, duraciones_metodo_csv_sw)
    desviacion_sw_video = calcular_desviacion_tipica(duraciones_dominancia_sw, duraciones_metodo_video_sw)

    # Crear DataFrame con los resultados
    resultados = pd.DataFrame({
        "Fase": ["LR", "MSt", "TSt", "PSw", "Sw"],
        "Desviación Típica por Zancada (dominancia vs CSV)": [desviacion_lr_csv, desviacion_mst_csv, desviacion_tst_csv, desviacion_psw_csv, desviacion_sw_csv],
        "Desviación Típica por Zancada (dominancia vs Video)": [desviacion_lr_video, desviacion_mst_video, desviacion_tst_video, desviacion_psw_video, desviacion_sw_video],
        "Desviación Típica Total (dominancia vs CSV)": [desviacion_lr_csv, desviacion_mst_csv, desviacion_tst_csv, desviacion_psw_csv, desviacion_sw_csv],
        "Desviación Típica Total (dominancia vs Video)": [desviacion_lr_video, desviacion_mst_video, desviacion_tst_video, desviacion_psw_video, desviacion_sw_video]
    })

    # Guardar los resultados en un archivo CSV
    archivo_guardado = filedialog.asksaveasfilename(title="Guardar archivo CSV con resultados", defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    guardar_csv(resultados, archivo_guardado)

    print(f"Desviaciones típicas calculadas y guardadas en: {archivo_guardado}")














