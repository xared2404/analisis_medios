import pandas as pd

INP = "data/processed/articles_emotions.csv"
OUT = "data/bi/month_completeness.csv"

df = pd.read_csv(INP, usecols=["fecha_real"], dtype=str)
dt = pd.to_datetime(df["fecha_real"], errors="coerce").dropna()

tmp = pd.DataFrame({"date": dt})
tmp["month"] = tmp["date"].dt.to_period("M").astype("string")
tmp["day"] = tmp["date"].dt.day

days = tmp.groupby("month")["day"].nunique().reset_index(name="unique_days_observed")

# heurística: si tiene >= 25 días distintos, lo consideramos “casi completo”
days["is_complete_month"] = (days["unique_days_observed"] >= 25).astype(int)

days.to_csv(OUT, index=False)
print("[OK] wrote:", OUT)
print(days.sort_values("month").to_string(index=False))
