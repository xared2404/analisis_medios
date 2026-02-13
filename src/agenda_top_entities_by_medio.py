import pandas as pd

DATA = "data/processed/agenda_counts_non_media.csv"
OUT  = "data/processed/agenda_top50_by_medio.csv"

df = pd.read_csv(DATA)

top = (
    df.sort_values(["Medio","count"], ascending=[True, False])
      .groupby("Medio")
      .head(50)
)

top.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("rows:", len(top))
print("medios:", top["Medio"].nunique())
