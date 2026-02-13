import pandas as pd

ENTS = "data/processed/entities_long_clean.csv"
OUT  = "data/processed/agenda_emotion_by_medio.csv"

df = pd.read_csv(ENTS, usecols=["Medio","entity_canon","predict_emotion"], dtype=str)

agg = (
    df.groupby(["Medio","entity_canon","predict_emotion"])
      .size()
      .reset_index(name="count")
)

agg.to_csv(OUT, index=False)

print("[OK] agenda-emotion matrix built")
print("Rows:", len(agg))
