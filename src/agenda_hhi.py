import pandas as pd
import numpy as np

DATA = "data/processed/agenda_counts_non_media.csv"

df = pd.read_csv(DATA)

# total por medio
totals = df.groupby("Medio")["count"].sum().reset_index(name="total")
df = df.merge(totals, on="Medio")
df["share"] = df["count"] / df["total"]

# HHI
hhi = (
    df.groupby("Medio")["share"]
      .apply(lambda x: np.sum(x**2))
      .reset_index(name="HHI")
      .sort_values("HHI", ascending=False)
)

hhi.to_csv("data/processed/agenda_hhi_by_medio.csv", index=False)

print(hhi.head(10))
