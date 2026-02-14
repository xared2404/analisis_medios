import pandas as pd

INP = "data/processed/agenda_counts_stage3.csv"
OUT = "data/bi/top_entities_global_stage3.csv"

TOP_N = 5000

df = pd.read_csv(INP, usecols=["entity_canon","count"], dtype=str)
df["count"] = df["count"].astype(int)

top = (
    df.groupby("entity_canon")["count"]
      .sum()
      .sort_values(ascending=False)
      .head(TOP_N)
      .reset_index()
)

top.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Rows:", len(top))
print(top.head(10).to_string(index=False))
