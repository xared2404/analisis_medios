import pandas as pd

INPUT = "data/processed/entities_long.csv"
OUT   = "data/processed/mentions_counts_by_medio.csv"

df = pd.read_csv(INPUT, usecols=["Medio","entity","entity_type"], dtype=str)

counts = (
    df.groupby(["Medio","entity"])
      .size()
      .reset_index(name="count")
)

counts.to_csv(OUT, index=False)

print("[OK] mentions matrix built")
print("Rows:", len(counts))
