import pandas as pd

INP = "data/bi/agenda_counts_stage3_monthly.csv"
OUT = "data/bi/agenda_share_stage3_monthly.csv"

df = pd.read_csv(INP, dtype={"month":"string","Medio":"string","entity_canon":"string","count":"int64"})

tot = (df.groupby(["month","Medio"])["count"].sum().reset_index(name="total_medio_month"))
df = df.merge(tot, on=["month","Medio"], how="left")
df["share_within_medio_month"] = df["count"] / df["total_medio_month"]

df.to_csv(OUT, index=False)
print("[OK] wrote:", OUT)
print("Rows:", len(df))
