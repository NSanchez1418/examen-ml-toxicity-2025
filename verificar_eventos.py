import os, sys, glob
import pandas as pd

print("=== Verificación/Limpieza: Eventos Peligrosos SNGRE ===")
data_dir = os.path.join("data")

# 1) Localizar el archivo original (maneja variantes como (1))
pattern = os.path.join(data_dir, "SGR_EventosPeligrosos_2010_2022Diciembre*.csv")
cands = glob.glob(pattern)
if not cands:
    print("ERROR: No encuentro el CSV original en:", pattern)
    print("Asegúrate de que está en ML_trabajo/data y no fue renombrado raramente.")
    sys.exit(1)

src = cands[0]
print("Usando archivo:", src)

# 2) Leer robusto: separador ';' + encoding latin-1 (fallback a utf-8-sig)
def read_events(path):
    try:
        return pd.read_csv(path, sep=";", encoding="latin-1")
    except Exception as e1:
        print("Fallo latin-1:", repr(e1))
        try:
            return pd.read_csv(path, sep=";", encoding="utf-8-sig")
        except Exception as e2:
            print("Fallo utf-8-sig:", repr(e2))
            # último intento tolerante
            return pd.read_csv(path, sep=";", encoding="latin-1", on_bad_lines="skip", engine="python")

df = read_events(src)

print("Shape original:", df.shape)
print("Primeras columnas:", list(df.columns)[:12], "...")
print(df.head(5))

# 3) Normalizar nombres de columnas
df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

# 4) Detectar columna de tipo de evento (para crear etiqueta)
tipo_col = None
for cand in ["tipo_evento", "tipo_de_evento", "evento", "evento_principal"]:
    if cand in df.columns:
        tipo_col = cand
        break

if tipo_col is None:
    print("ERROR: No encuentro columna de tipo de evento para crear la etiqueta binaria.")
    print("Columnas disponibles:", list(df.columns))
    sys.exit(1)

# 5) Crear etiqueta binaria: evento_sismo = 1 si contiene 'SISMO'
df["evento_sismo"] = (df[tipo_col].astype(str).str.upper().str.contains("SISMO")).astype(int)

# 6) Seleccionar columnas numéricas útiles si existen
cands_num = ["anio", "año", "ano", "mes", "afectados", "damnificados", "viviendas_destruidas", "fallecidos"]
presentes = [c for c in cands_num if c in df.columns]

# Armonizar 'anio'
if "anio" not in df.columns:
    if "año" in df.columns: df = df.rename(columns={"año": "anio"})
    elif "ano" in df.columns: df = df.rename(columns={"ano": "anio"})

keep = ["evento_sismo"] + [c for c in ["anio", "mes", "afectados", "damnificados", "viviendas_destruidas", "fallecidos"] if c in df.columns]
df_out = df[keep].copy()

# 7) Convertir a numérico donde aplique
for c in ["anio", "mes", "afectados", "damnificados", "viviendas_destruidas", "fallecidos"]:
    if c in df_out.columns:
        df_out[c] = pd.to_numeric(df_out[c], errors="coerce")

# 8) Limpiar nulos
antes = df_out.shape
df_out = df_out.dropna().reset_index(drop=True)
despues = df_out.shape

print("\nColumnas finales:", list(df_out.columns))
print("Shape limpio:", despues, "(antes era", antes, ")")
print("\nBalance etiqueta (evento_sismo):")
print(df_out["evento_sismo"].value_counts())

# 9) Guardar limpio para el proyecto
out_path = os.path.join(data_dir, "eventos_peligrosos_ecuador_clean.csv")
df_out.to_csv(out_path, index=False)
print("\n✅ Guardado limpio en:", out_path)
