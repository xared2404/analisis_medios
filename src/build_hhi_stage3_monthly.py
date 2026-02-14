import pandas as pd

INP = "data/bi/agenda_share_stage3_monthly.csv"
OUT = "data/bi/hhi_stage3_monthly.csv"

df = pd.read_csv(INP, dtype={
    "month":"string",
    "Medio":"string",
    "entity_canon":"string",
    "share_within_medio_month":"float64"
})

hhi = (
    df.assign(hhi_term=df["share_within_medio_month"] ** 2)
      .groupby(["month","Medio"], as_index=False)
      .agg(
          hhi=("hhi_term","sum"),
          n_entities=("entity_canon","nunique")
      )
)

hhi.to_csv(OUT, index=False)
print("[OK] wrote:", OUT)
print("Rows:", len(hhi), "| months:", hhi["month"].nunique(), "| medios:", hhi["Medio"].nunique())
