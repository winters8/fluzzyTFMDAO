import pandas as pd
from datetime import datetime
import re

# Ruta al archivo CSV original
archivo_csv = "zancadas_detectadas_L_Sebas.csv"
# Cargar el archivo
df = pd.read_csv(archivo_csv)

# Función para convertir tiempo a timedelta
def tiempo_a_timedelta(tiempo_str):
    return datetime.strptime(tiempo_str, "%M:%S.%f") - datetime.strptime("00:00.000", "%M:%S.%f")

# Función para corregir tiempos con formato incorrecto tipo '01.03.400'
def corregir_formato_tiempo(tiempo):
    if isinstance(tiempo, str) and re.match(r"^\d{2}\.\d{2}\.\d{3}$", tiempo):
        partes = tiempo.split(".")
        return f"{partes[0]}:{partes[1]}.{partes[2]}"
    return tiempo

# Formatear timedelta como MM:SS.mmm
def formatear_timedelta(td):
    total_ms = int(td.total_seconds() * 1000)
    signo = "-" if total_ms < 0 else ""
    total_ms = abs(total_ms)
    minutos = total_ms // 60000
    segundos = (total_ms % 60000) // 1000
    milisegundos = total_ms % 1000
    return f"{signo}{minutos:02}:{segundos:02}.{milisegundos:03}"

# Corregir formato en las columnas de tiempo
df["tiempo_incio_envideo"] = df["tiempo_incio_envideo"].apply(corregir_formato_tiempo)

# Calcular duración de zancada en video
df["Duración_zancada_video_td"] = df.apply(
    lambda row: tiempo_a_timedelta(row["tiempo_fin_envideo"]) - tiempo_a_timedelta(row["tiempo_incio_envideo"]),
    axis=1
)

# Convertir duración del CSV a timedelta
df["Duración_zancada_CSV_td"] = df["Duración_zancada_CSV"].apply(tiempo_a_timedelta)

# Calcular la diferencia entre ambas duraciones
df["Diferencia_duración_td"] = df["Duración_zancada_video_td"] - df["Duración_zancada_CSV_td"]

# Calcular diferencia en porcentaje (con dos decimales y símbolo %)
df["Diferencia_porcentaje_val"] = (
    df["Diferencia_duración_td"].dt.total_seconds() / df["Duración_zancada_CSV_td"].dt.total_seconds()
) * 100
df["Diferencia_porcentaje"] = df["Diferencia_porcentaje_val"].apply(lambda x: f"{x:.2f}%")

# Calcular Z-score solo para observaciones que no sean "gira"
sin_giros = df["observacion"] != "gira"
media_dif = df.loc[sin_giros, "Diferencia_duración_td"].dt.total_seconds().mean()
std_dif = df.loc[sin_giros, "Diferencia_duración_td"].dt.total_seconds().std()

df["Z_score_diferencia"] = None  # inicializar
df.loc[sin_giros, "Z_score_diferencia"] = (
    df.loc[sin_giros, "Diferencia_duración_td"].dt.total_seconds() - media_dif
) / std_dif

# Formatear timedelta a string
df["Duración_zancada_video"] = df["Duración_zancada_video_td"].apply(formatear_timedelta)
df["Duración_zancada_CSV"] = df["Duración_zancada_CSV_td"].apply(formatear_timedelta)
df["Diferencia_duración"] = df["Diferencia_duración_td"].apply(formatear_timedelta)

# Reordenar columnas: colocar duración en video y diferencia justo después de tiempo_fin_envideo
columnas = list(df.columns)
idx = columnas.index("tiempo_fin_envideo")
for col in ["Duración_zancada_video", "Diferencia_duración"][::-1]:
    columnas.insert(idx + 1, columnas.pop(columnas.index(col)))
df = df[columnas]

# Eliminar columnas auxiliares
df.drop(columns=[
    "Duración_zancada_video_td",
    "Duración_zancada_CSV_td",
    "Diferencia_duración_td",
    "Diferencia_porcentaje_val"
], inplace=True)

# Exportar a un nuevo archivo CSV
df.to_csv("zancadas_con_zscore_filtrado_L_Sebas.csv", index=False)

print("Archivo exportado como 'zancadas_con_zscore_filtrado_R_sebas.csv'")


