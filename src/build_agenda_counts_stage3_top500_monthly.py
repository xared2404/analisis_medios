import pandas as pd

COUNTS = "data/bi/agenda_counts_stage3_monthly.csv"
TOP = "data/bi/top500_stage3.csv"
OUT = "data/bi/agenda_counts_stage3_top500_monthly.csv"

df = pd.read_csv(COUNTS)
top = pd.read_csv(TOP)

keep = set(top["entity_canon"])

df = df[df["entity_canon"].isin(keep)].copy()

df.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Rows:", len(df))
print("Entities:", df["entity_canon"].nunique())
