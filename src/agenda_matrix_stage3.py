import pandas as pd

INP = "data/processed/doc_presence_counts_by_medio.csv"
OUT = "data/processed/agenda_counts_stage3.csv"

df = pd.read_csv(INP, dtype={"Medio":"string","entity_canon":"string","count":"int64"})

# opcional: filtra entidades demasiado raras (ruido)
MIN_COUNT_GLOBAL = 50

global_counts = df.groupby("entity_canon")["count"].sum()
keep = set(global_counts[global_counts >= MIN_COUNT_GLOBAL].index)

df = df[df["entity_canon"].isin(keep)].copy()

df.to_csv(OUT, index=False)
print("[OK] wrote:", OUT)
print("Rows:", len(df))
print("Unique medios:", df["Medio"].nunique())
print("Unique entities:", df["entity_canon"].nunique())
