import pandas as pd

INP = "data/bi/top_entities_global_stage3.csv"
OUT = "data/bi/top500_stage3.csv"

df = pd.read_csv(INP)

top500 = df.head(500).copy()

top500.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Entities:", len(top500))
