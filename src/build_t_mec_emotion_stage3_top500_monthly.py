import pandas as pd

ENTS = "data/processed/entities_long_clean.csv"
OUT  = "data/bi/t_mec_emotion_stage3_top500_monthly.csv"

keywords = ["t-mec", "tmec", "usmca", "nafta", "tratado mexico"]

df = pd.read_csv(ENTS, usecols=[
    "fecha_real","Medio","entity_canon",
    "predict_emotion","intensity"
])

df["month"] = pd.to_datetime(df["fecha_real"]).dt.to_period("M").astype(str)

mask = df["entity_canon"].str.lower().apply(
    lambda x: any(k in str(x) for k in keywords)
)

t_mec = df[mask].copy()

agg = (
    t_mec.groupby(["month","Medio"], as_index=False)
         .agg(
             mean_intensity=("intensity","mean"),
             n_mentions=("entity_canon","count")
         )
)

agg.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Rows:", len(agg))
print(agg.head())
