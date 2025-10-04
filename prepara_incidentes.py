import os
import pandas as pd

# Ruta del dataset original
src = os.path.join("data", "incidentes_julio_2025.csv")

# Intentamos leer el CSV con distintas configuraciones comunes
df = None
for config in [
    {"sep": ";", "encoding": "utf-8-sig"},
    {"sep": ",", "encoding": "utf-8-sig"},
    {"sep": ";", "encoding": "latin-1"},
    {"sep": ",", "encoding": "latin-1"},
]:
    try:
        df = pd.read_csv(src, **config)
        break
    except Exception as e:
        last_error = e

if df is None:
    raise last_error

print("✅ Dataset cargado correctamente.")
print("Columnas detectadas:", df.columns.tolist()[:10])
print("Filas y columnas:", df.shape)

# Normalizamos los nombres de columnas
df.columns = [c.strip() for c in df.columns]

# Intentamos detectar columnas clave
fecha_col = next((c for c in df.columns if "fecha" in c.lower()), None)
cod_parroquia = next((c for c in df.columns if "parroquia" in c.lower() and "cod" in c.lower()), None)
subtipo_col = next((c for c in df.columns if "subtipo" in c.lower()), None)

# Convertimos la fecha en variables numéricas
if fecha_col:
    df[fecha_col] = pd.to_datetime(df[fecha_col], dayfirst=True, errors="coerce")
    df["anio"] = df[fecha_col].dt.year
    df["mes"] = df[fecha_col].dt.month
    df["dia"] = df[fecha_col].dt.day
else:
    df["anio"] = pd.NA
    df["mes"] = pd.NA
    df["dia"] = pd.NA

# Creamos la etiqueta binaria: 1 si es accidente con heridos, 0 si no
if subtipo_col:
    df["accidente_con_heridos"] = df[subtipo_col].astype(str).str.lower().str.contains(
        "accidente de tránsito con heridos"
    ).astype(int)
else:
    df["accidente_con_heridos"] = 0

# Seleccionamos las columnas numéricas
cols_finales = ["anio", "mes", "dia", "accidente_con_heridos"]
if cod_parroquia:
    cols_finales.insert(0, cod_parroquia)

df_out = df[cols_finales].dropna().reset_index(drop=True)

# Guardamos el nuevo dataset limpio
out_path = os.path.join("data", "incidentes_clasificacion_ready.csv")
df_out.to_csv(out_path, index=False)
print(f"\n💾 Archivo limpio guardado en: {out_path}")
print("Shape final:", df_out.shape)
print("\nDistribución de la etiqueta:")
print(df_out['accidente_con_heridos'].value_counts())

