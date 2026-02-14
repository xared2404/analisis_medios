import pandas as pd

INP = "data/bi/agenda_share_stage3_top500_monthly.csv"
OUT = "data/bi/hhi_stage3_top500_monthly.csv"

df = pd.read_csv(INP)

hhi = (
    df.assign(hhi_term=df["share_within_medio_month"]**2)
      .groupby(["month","Medio"], as_index=False)
      .agg(hhi=("hhi_term","sum"))
)

hhi.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Rows:", len(hhi))
