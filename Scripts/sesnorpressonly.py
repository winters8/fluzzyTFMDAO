import pandas as pd

# Carga el archivo CSV
df = pd.read_csv('datos sebas/CSVs/archivo_con_tiempo_formateado_L_Sebas.csv')

# Filtra solo las columnas que empiezan por 'PressureSensor'
df_presion = df.filter(like='PressureSensor')

# Guarda el nuevo DataFrame si quieres
df_presion.to_csv('onlypresssensorL_Sebas.csv', index=False)
