import pandas as pd
import ast

# === CARGA ===
# Ajusta rutas si es necesario
raw_path = "data/raw/dataset.csv"          # <- cambia si tu raw está en otro lugar
clean_path = "data/processed/dataset.csv"  # <- cambia si tu clean está en otro lugar

print("\n=== LOADING DATA ===")

try:
    raw_df = pd.read_csv(raw_path)
    print(f"[OK] Raw loaded: {len(raw_df)} rows")
except Exception as e:
    print(f"[ERROR] Could not load raw: {e}")
    exit()

try:
    clean_df = pd.read_csv(clean_path)
    print(f"[OK] Clean loaded: {len(clean_df)} rows")
except Exception as e:
    print(f"[ERROR] Could not load clean: {e}")
    exit()


print("\n=== BASIC COUNTS ===")

print("Docs originales:", len(raw_df))
print("Docs post-normalización:", len(clean_df))

loss = len(raw_df) - len(clean_df)
if len(raw_df) > 0:
    pct = (loss / len(raw_df)) * 100
else:
    pct = 0

print(f"Docs perdidos: {loss} ({pct:.2f}%)")


print("\n=== TEXT AVAILABILITY (RAW) ===")
if "Texto" in raw_df.columns:
    print("Con texto (raw):", raw_df["Texto"].notna().sum())
else:
    print("No existe columna 'Texto' en raw")

print("\n=== ENTITY TYPE CHECK (RAW) ===")

def is_list(x):
    return isinstance(x, list)

def looks_like_stringified_list(x):
    return isinstance(x, str) and x.strip().startswith("[")

if "Entidades" in raw_df.columns:
    print("Entidades tipo list real:",
          raw_df["Entidades"].apply(is_list).sum())
    print("Entidades stringificadas:",
          raw_df["Entidades"].apply(looks_like_stringified_list).sum())
else:
    print("No existe columna 'Entidades' en raw")


print("\n=== EMPTY ENTITY CHECK (CLEAN) ===")

if "Entidades" in clean_df.columns:
    print("Entidades vacías en clean:",
          clean_df["Entidades"].isna().sum())
else:
    print("No existe columna 'Entidades' en clean")


print("\n=== DONE ===")
