import os, sys
import pandas as pd

csv_path = os.path.join("data", "MAATE_concentracionpm25_2021diciembre.csv")
print("Leyendo:", csv_path)

def leer_pm25(path):
    # intento 1: latin-1 + separador ; + decimal ,
    try:
        return pd.read_csv(path, sep=";", encoding="latin-1", decimal=",")
    except Exception as e1:
        print("Fallo latin-1:", repr(e1))
    # intento 2: utf-8-sig
    try:
        return pd.read_csv(path, sep=";", encoding="utf-8-sig", decimal=",")
    except Exception as e2:
        print("Fallo utf-8-sig:", repr(e2))
    # intento 3: tolerar filas raras
    return pd.read_csv(path, sep=";", encoding="latin-1", decimal=",",
                       on_bad_lines="skip", engine="python")

df = leer_pm25(csv_path)

print("\n✅ Cargado. Shape:", df.shape)
print("\nColumnas:\n", list(df.columns))
print("\nPrimeras filas:\n", df.head(10))

# Tip: estandarizamos nombres a minúsculas sin espacios
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# Guardamos una versión limpia para el proyecto (respaldo)
out_path = os.path.join("data", "pm25_ecuador_clean.csv")
df.to_csv(out_path, index=False)
print("\n💾 Guardado limpio en:", out_path)

