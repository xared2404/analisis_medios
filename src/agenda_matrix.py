import pandas as pd

DATA = "data/processed/entities_long_pro_strict.csv"

use = ["Medio","entity_canon","is_media_like"]
df = pd.read_csv(DATA, usecols=use)

# excluir medios/agencias
df = df[df["is_media_like"] == 0]

# conteo por medio-entidad
counts = (
    df.groupby(["Medio","entity_canon"])
      .size()
      .reset_index(name="count")
)

counts.to_csv("data/processed/agenda_counts_non_media.csv", index=False)

print("Rows:", len(counts))
print("Medios:", counts["Medio"].nunique())
print("Entidades únicas:", counts["entity_canon"].nunique())
