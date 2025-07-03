import pandas as pd
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

def convertir_tiempo(tiempo_str):
    """
    Convierte un string MM:SS.mmmuuu a segundos.
    """
    try:
        t = datetime.strptime(tiempo_str, "%M:%S.%f")
        return t.minute * 60 + t.second + t.microsecond / 1e6
    except Exception as e:
        print(f"Error al convertir tiempo '{tiempo_str}': {e}")
        return None

# Crear ventana oculta de tkinter
root = tk.Tk()
root.withdraw()

# ==========================
# Seleccionar primer CSV
# ==========================
print("Selecciona el primer archivo CSV (zancadas detectadas):")
file_zancadas = filedialog.askopenfilename(
    title="Seleccionar CSV de zancadas detectadas",
    filetypes=[("CSV files", "*.csv")]
)

if not file_zancadas:
    print("No se seleccionó ningún archivo. Saliendo.")
    exit()

# ==========================
# Seleccionar segundo CSV
# ==========================
print("Selecciona el segundo archivo CSV (datos de sensores):")
file_sensores = filedialog.askopenfilename(
    title="Seleccionar CSV de datos de sensores",
    filetypes=[("CSV files", "*.csv")]
)

if not file_sensores:
    print("No se seleccionó ningún archivo. Saliendo.")
    exit()

# ==========================
# Cargar datos
# ==========================
print("Cargando datos...")
df_zancadas = pd.read_csv(file_zancadas)
df_sensores = pd.read_csv(file_sensores)

# Normalizar nombres de columnas del CSV de zancadas
df_zancadas.columns = [c.strip().lower().replace(" ", "_") for c in df_zancadas.columns]

# Configura aquí el nombre de la columna de tiempo en sensores
columna_tiempo_sensores = "Tiempo (mm:ss.mmmuuu)"

if columna_tiempo_sensores not in df_sensores.columns:
    print(f"La columna '{columna_tiempo_sensores}' no está en el CSV de sensores.")
    print("Columnas encontradas:", df_sensores.columns.tolist())
    exit()

# Convertir tiempos de zancadas a segundos
df_zancadas["inicio_seg"] = df_zancadas["inicio_zancada_csv"].apply(convertir_tiempo)
df_zancadas["fin_seg"] = df_zancadas["fin_zancada_csv"].apply(convertir_tiempo)

# Filtrar zancadas normales
df_normales = df_zancadas[df_zancadas["observacion"].str.lower() == "ninguna"].copy()

# Ordenar por inicio
df_normales = df_normales.sort_values("inicio_seg").reset_index(drop=True)

# Agrupar bloques consecutivos (separación menor de 1 segundo)
bloques = []
if not df_normales.empty:
    inicio_actual = df_normales.loc[0, "inicio_seg"]
    fin_actual = df_normales.loc[0, "fin_seg"]

    for idx in range(1, len(df_normales)):
        inicio = df_normales.loc[idx, "inicio_seg"]
        fin = df_normales.loc[idx, "fin_seg"]
        if inicio - fin_actual <= 1.0:
            fin_actual = fin
        else:
            bloques.append((inicio_actual, fin_actual))
            inicio_actual = inicio
            fin_actual = fin
    bloques.append((inicio_actual, fin_actual))

# Convertir tiempos sensores a segundos
df_sensores["tiempo_seg"] = df_sensores[columna_tiempo_sensores].apply(convertir_tiempo)

# Ordenar por tiempo
df_sensores = df_sensores.sort_values("tiempo_seg").reset_index(drop=True)

# Extraer registros por bloques
indices_totales = set()

for bloque_inicio, bloque_fin in bloques:
    idx_in = df_sensores[
        (df_sensores["tiempo_seg"] >= bloque_inicio) &
        (df_sensores["tiempo_seg"] <= bloque_fin)
    ].index.tolist()

    if not idx_in:
        continue

    idx_min = idx_in[0]
    idx_max = idx_in[-1]

    # Añadir 35 registros antes y después
    idx_rango = range(max(0, idx_min - 35), min(len(df_sensores), idx_max + 36))
    indices_totales.update(idx_rango)

# Crear DataFrame final
df_resultado = df_sensores.loc[sorted(indices_totales)].reset_index(drop=True)

print(f"Registros extraídos antes de eliminar duplicados: {df_resultado.shape[0]}")

# Verificar duplicados
num_duplicados = df_resultado.duplicated().sum()
if num_duplicados > 0:
    print(f"⚠️ Atención: Se encontraron {num_duplicados} registros duplicados por solapamiento de bloques.")
    eliminar = input("¿Quieres eliminar duplicados antes de guardar? (s/N): ").strip().lower()
    if eliminar == "s":
        df_resultado = df_resultado.drop_duplicates().reset_index(drop=True)
        print("Duplicados eliminados.")
    else:
        print("Duplicados NO eliminados.")
else:
    print("No se encontraron registros duplicados.")

print(f"Total de registros que se guardarán: {df_resultado.shape[0]}")

cols_a_eliminar = ["tiempo_seg", "Tiempo (mm:ss.mmmuuu)"]
df_resultado = df_resultado.drop(columns=[col for col in cols_a_eliminar if col in df_resultado.columns])

# ==========================
# Guardar CSV resultado
# ==========================
print("Selecciona dónde guardar el CSV generado:")
output_file = filedialog.asksaveasfilename(
    title="Guardar CSV de salida",
    defaultextension=".csv",
    filetypes=[("CSV files", "*.csv")]
)

if output_file:
    df_resultado.to_csv(output_file, index=False)
    print(f"✅ Archivo guardado correctamente en: {output_file}")
else:
    print("No se seleccionó ubicación de guardado. Saliendo.")
