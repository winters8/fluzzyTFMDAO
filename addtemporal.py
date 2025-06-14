import pandas as pd

# Cargar el archivo CSV
df = pd.read_csv("exp_27_part_63_trial_308_sw_1_R.csv")  # Reemplaza con el nombre real de tu archivo

# Frecuencia de muestreo (Hz)
sampling_rate = 64
sampling_period = 1 / sampling_rate  # Tiempo entre muestras en segundos

# Calcular tiempo como una Serie (para poder usar .apply)
tiempo_segundos = pd.Series(df.index * sampling_period)

# Convertir a formato mm:ss.mmm
df['Tiempo (mm:ss.mmm)'] = tiempo_segundos.apply(
    lambda x: f"{int(x // 60):02d}:{int(x % 60):02d}.{int((x % 1) * 1000):03d}"
)

# Guardar el nuevo archivo CSV
df.to_csv('archivo_con_tiempo_formateado_R_Sebas.csv', index=False)
