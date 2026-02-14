import pandas as pd

INP = "data/bi/agenda_counts_stage3_top500_monthly.csv"
OUT = "data/bi/agenda_share_stage3_top500_monthly.csv"

df = pd.read_csv(INP)

df["total_medio_month"] = df.groupby(["month","Medio"])["count"].transform("sum")

df["share_within_medio_month"] = df["count"] / df["total_medio_month"]

df.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Rows:", len(df))
