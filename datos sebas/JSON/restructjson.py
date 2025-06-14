import pandas as pd
import json

# Cargar los datos desde el archivo JSON
file_path = 'git_Sebas_L_timestamp.json'  # Cambia la ruta del archivo
data = pd.read_json(file_path)

# Extraer los valores de las fases desde el campo 'phases'
data['LR'] = data['phases'].apply(lambda x: x.get('LR', None))
data['MSt'] = data['phases'].apply(lambda x: x.get('MSt', None))
data['TSt'] = data['phases'].apply(lambda x: x.get('TSt', None))
data['PSw'] = data['phases'].apply(lambda x: x.get('PSw', None))
data['Sw'] = data['phases'].apply(lambda x: x.get('Sw', None))

# Convertir TimeStamp a formato datetime
data['TimeStamp'] = pd.to_datetime(data['TimeStamp'])

# Filtrar los picos de la fase 'LR' (cuando LR > 0.9)
threshold_lr = 0.9
peaks_lr = data[data['LR'] > threshold_lr]

# Crear una lista para almacenar los resultados
results = []

# Agrupar las zancadas basadas en los picos de 'LR' (con un umbral para determinar una nueva zancada)
zancada_id = 1
zancada = None
last_time = None

for idx, peak in peaks_lr.iterrows():
    # Si la diferencia de tiempo con el último golpe de talón es demasiado larga, se considera una nueva zancada
    if last_time is not None and (peak['TimeStamp'] - last_time).total_seconds() > 2:
        # Guardar la zancada anterior si existe
        if zancada is not None:
            results.append(zancada)
        
        # Iniciar una nueva zancada y asegurar que las fases estén inicializadas correctamente
        zancada = {
            "Numero_ancada": zancada_id,
            "Tiempo_inicio": peak['TimeStamp'].strftime('%M:%S.%f')[:-3],
            "Tiempo_final": '',
            "Tiempo_zancada": '',
            "Fases": {
                "LR": {"Tiempo_inicio": '', "Tiempo_final": '', "Tiempo_total": ''},
                "MSt": {"Tiempo_inicio": '', "Tiempo_final": '', "Tiempo_total": ''},
                "TSt": {"Tiempo_inicio": '', "Tiempo_final": '', "Tiempo_total": ''},
                "PSw": {"Tiempo_inicio": '', "Tiempo_final": '', "Tiempo_total": ''},
                "Sw": {"Tiempo_inicio": '', "Tiempo_final": '', "Tiempo_total": ''}
            }
        }
        zancada_id += 1
    
    # Asegurarnos de que las fases estén correctamente inicializadas
    if zancada is not None:
        # Asignar los tiempos de la fase 'LR' para la zancada actual
        zancada["Fases"]["LR"]["Tiempo_inicio"] = peak['TimeStamp'].strftime('%M:%S.%f')[:-3]
        zancada["Fases"]["LR"]["Tiempo_final"] = peak['TimeStamp'].strftime('%M:%S.%f')[:-3]
        zancada["Fases"]["LR"]["Tiempo_total"] = ''

        # Asignar las otras fases (MSt, TSt, PSw, Sw)
        for phase in ['MSt', 'TSt', 'PSw', 'Sw']:
            if peak['phases'].get(phase, None) is not None:
                zancada["Fases"][phase]["Tiempo_inicio"] = peak['TimeStamp'].strftime('%M:%S.%f')[:-3]
                zancada["Fases"][phase]["Tiempo_final"] = peak['TimeStamp'].strftime('%M:%S.%f')[:-3]
                zancada["Fases"][phase]["Tiempo_total"] = ''  # Esto puede ser calculado si tienes la lógica de transiciones

    # Actualizar el último tiempo para la comparación
    last_time = peak['TimeStamp']

# Asegurarse de agregar la última zancada al final
if zancada is not None:
    results.append(zancada)

# Convertir los resultados a formato JSON
json_result = json.dumps(results, indent=4)

# Imprimir el resultado
# print(json_result)

# Si necesitas guardar el JSON en un archivo
with open('resultado_zancadas.json', 'w') as f:
     f.write(json_result)








