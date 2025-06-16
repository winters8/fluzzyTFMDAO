import json
import numpy as np
import tkinter as tk
from tkinter import filedialog

# Función para convertir tiempos en formato mm:ss.SSSSSS a segundos
def convertir_a_segundos(tiempo):
    minutos, segundos = tiempo.split(':')
    segundos, fraccion = segundos.split('.')
    return int(minutos) * 60 + int(segundos) + int(fraccion) / 1e6

# Cargar los datos de los archivos JSON
def cargar_datos(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        return json.load(f)

# Filtrar las zancadas basándose en la tolerancia
def filtrar_zancadas(zancadas_primero, zancadas_segundo, tolerancia=1.0):
    # Extraer los tiempos de inicio de las zancadas
    tiempos_inicio_primero = [z['Tiempo_inicio'] for z in zancadas_primero]
    tiempos_inicio_segundo_csv = [z['Inicio_zancada_CSV'] for z in zancadas_segundo]
    tiempos_inicio_segundo_video = [z['Inicio_zancada_video'] for z in zancadas_segundo]

    # Convertir los tiempos a segundos
    tiempos_inicio_primero_segundos = [convertir_a_segundos(t) for t in tiempos_inicio_primero]
    tiempos_inicio_segundo_csv_segundos = [convertir_a_segundos(t) for t in tiempos_inicio_segundo_csv]
    tiempos_inicio_segundo_video_segundos = [convertir_a_segundos(t) for t in tiempos_inicio_segundo_video]

    # Filtrar las zancadas que están dentro de la tolerancia para CSV
    zancadas_filtradas_csv = [
        zancada for zancada, tiempo in zip(zancadas_segundo, tiempos_inicio_segundo_csv_segundos)
        if any(np.abs(tiempo - t) <= tolerancia for t in tiempos_inicio_primero_segundos)
    ]

    # Filtrar las zancadas que están dentro de la tolerancia para VIDEO
    zancadas_filtradas_video = [
        zancada for zancada, tiempo in zip(zancadas_segundo, tiempos_inicio_segundo_video_segundos)
        if any(np.abs(tiempo - t) <= tolerancia for t in tiempos_inicio_primero_segundos)
    ]
    
    # Devolver las zancadas filtradas
    return zancadas_filtradas_csv, zancadas_filtradas_video

# Guardar el archivo JSON de zancadas filtradas
def guardar_json(zancadas, archivo_salida):
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(zancadas, f, ensure_ascii=False, indent=4)

# Función para abrir la ventana de selección de archivos
def seleccionar_archivo(title="Selecciona el archivo", filetypes=(("JSON Files", "*.json"),)):
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    archivo = filedialog.askopenfilename(title=title, filetypes=filetypes)
    return archivo

# Función para guardar el archivo en una ubicación elegida
def seleccionar_guardado(title="Guardar como", filetypes=(("JSON Files", "*.json"),)):
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    archivo_guardado = filedialog.asksaveasfilename(title=title, defaultextension=".json", filetypes=filetypes)
    return archivo_guardado

# Ejecutar el flujo del programa
if __name__ == "__main__":
    # Seleccionar los archivos JSON
    print("Selecciona el archivo del primer conjunto de zancadas:")
    archivo_primero = seleccionar_archivo("Selecciona el archivo de las primeras zancadas")
    print("Selecciona el archivo del segundo conjunto de zancadas (CSV y Video):")
    archivo_segundo = seleccionar_archivo("Selecciona el archivo de las zancadas CSV y Video")
    
    # Cargar los datos de los archivos
    zancadas_primero = cargar_datos(archivo_primero)
    zancadas_segundo = cargar_datos(archivo_segundo)

    # Filtrar las zancadas con tolerancia de 1 segundo
    zancadas_filtradas_csv, zancadas_filtradas_video = filtrar_zancadas(zancadas_primero, zancadas_segundo, tolerancia=1.0)

    # Combinar las zancadas de CSV y VIDEO
    zancadas_completas = []
    for csv_zancada in zancadas_filtradas_csv:
        # Buscar la zancada VIDEO correspondiente dentro de las filtradas
        video_zancada = next((z for z in zancadas_filtradas_video if 
                              np.abs(convertir_a_segundos(csv_zancada['Inicio_zancada_CSV']) - 
                                     convertir_a_segundos(z['Inicio_zancada_video'])) <= 2.0), None)

        # Verificar si la clave 'Métodos' existe, si no, agregarla
        if 'Métodos' not in csv_zancada:
            csv_zancada['Métodos'] = {}

        # Si existe una zancada VIDEO correspondiente, agregarla solo si 'Métodos' existe en VIDEO
        if video_zancada and 'Métodos' in video_zancada:
            csv_zancada['Métodos']['Video'] = video_zancada['Métodos'].get('Video', {})
        
        zancadas_completas.append(csv_zancada)

    # Seleccionar la ubicación para guardar el archivo resultante
    archivo_guardado = seleccionar_guardado("Guardar archivo filtrado")

    # Guardar el archivo filtrado
    guardar_json(zancadas_completas, archivo_guardado)
    
    print(f"Filtrado y guardado exitoso en: {archivo_guardado}")


