import pandas as pd

INP = "data/bi/agenda_counts_stage2_mentions_monthly.csv"
OUT = "data/bi/agenda_share_stage2_mentions_monthly.csv"

MIN_COUNT_GLOBAL_MONTH = 50  # ajustable

df = pd.read_csv(INP, dtype={"month":"string","Medio":"string","entity":"string","count":"int64"})

# filtro por mes (evita ruido cuando hay meses pequeños)
gcnt = df.groupby(["month","entity"])["count"].sum().reset_index(name="gcount")
keep = gcnt[gcnt["gcount"] >= MIN_COUNT_GLOBAL_MONTH][["month","entity"]]

df = df.merge(keep, on=["month","entity"], how="inner")

tot = df.groupby(["month","Medio"])["count"].sum().reset_index(name="total_medio_month")
df = df.merge(tot, on=["month","Medio"], how="left")
df["share_within_medio_month"] = df["count"] / df["total_medio_month"]

df.to_csv(OUT, index=False)
print("[OK] wrote:", OUT)
print("Rows:", len(df))
print("Months:", df["month"].nunique(), "| Medios:", df["Medio"].nunique())
