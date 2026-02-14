import pandas as pd

INP = "data/bi/agenda_share_stage3_monthly.csv"
OUT = "data/bi/t_mec_share_stage3_top500_monthly.csv"

df = pd.read_csv(INP)

# --- Palabras clave robustas ---
keywords = ["t-mec", "tmec", "usmca", "nafta", "tratado mexico"]

mask = df["entity_canon"].str.lower().apply(
    lambda x: any(k in x for k in keywords)
)

t_mec = df[mask].copy()

agg = (
    t_mec.groupby(["month","Medio"], as_index=False)
         .agg(
             t_mec_share=("share_within_medio_month","sum")
         )
)

agg.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Rows:", len(agg))
print(agg.head())
