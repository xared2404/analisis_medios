import pandas as pd

INP = "data/processed/entities_long_clean.csv"
OUT = "data/bi/agenda_counts_stage3_monthly.csv"
CHUNK = 300_000

first = True
total = 0

def to_month(s):
    # fecha_real puede venir como string; esto lo vuelve YYYY-MM robusto
    dt = pd.to_datetime(s, errors="coerce")
    return dt.dt.to_period("M").astype("string")

for chunk in pd.read_csv(INP, usecols=["Medio","fecha_real","entity_canon"], dtype=str, chunksize=CHUNK):
    chunk = chunk.dropna(subset=["Medio","fecha_real","entity_canon"])
    chunk["month"] = to_month(chunk["fecha_real"])
    chunk = chunk.dropna(subset=["month"])
    g = (chunk.groupby(["month","Medio","entity_canon"])
              .size()
              .reset_index(name="count"))
    g.to_csv(OUT, mode="w" if first else "a", index=False, header=first)
    first = False
    total += len(g)

print("[OK] wrote:", OUT)
print("Appended rows:", total)
