import pandas as pd

INPUT = "data/processed/entities_long_clean.csv"
OUT   = "data/processed/doc_presence_counts_by_medio.csv"

df = pd.read_csv(INPUT, usecols=["Medio","entity_canon"], dtype=str)

counts = (
    df.groupby(["Medio","entity_canon"])
      .size()
      .reset_index(name="count")
)

counts.to_csv(OUT, index=False)

print("[OK] doc-presence matrix built")
print("Rows:", len(counts))
