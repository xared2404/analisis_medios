import pandas as pd

INP = "data/processed/mentions_counts_by_medio.csv"
OUT = "data/processed/agenda_counts_stage2_mentions.csv"

df = pd.read_csv(INP, dtype={"Medio":"string","entity":"string","count":"int64"})

# filtro global mínimo para eliminar ruido
MIN_COUNT_GLOBAL = 100  # un poco más alto que Stage 3

global_counts = df.groupby("entity")["count"].sum()
keep = set(global_counts[global_counts >= MIN_COUNT_GLOBAL].index)

df = df[df["entity"].isin(keep)].copy()

df.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Rows:", len(df))
print("Unique medios:", df["Medio"].nunique())
print("Unique entities:", df["entity"].nunique())
