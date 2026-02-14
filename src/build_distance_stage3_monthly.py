import pandas as pd
import numpy as np

INP_COUNTS = "data/bi/agenda_counts_stage3_monthly.csv"
META = "data/bi/media_metadata.csv"
OUT = "data/bi/distance_stage3_monthly.csv"

def cosine_distance_from_dicts(d1, d2):
    if not d1 or not d2:
        return np.nan
    keys = set(d1) | set(d2)
    v1 = np.fromiter((d1.get(k, 0.0) for k in keys), dtype=float)
    v2 = np.fromiter((d2.get(k, 0.0) for k in keys), dtype=float)
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return np.nan
    cos = float(np.dot(v1, v2) / (n1 * n2))
    return 1.0 - cos

df = pd.read_csv(INP_COUNTS, dtype={"month":"string","Medio":"string","entity_canon":"string","count":"int64"})
meta = pd.read_csv(META, dtype={"Medio":"string","country_group":"string"})
df = df.merge(meta, on="Medio", how="left")

rows = []

for month, mdf in df.groupby("month", sort=True):
    # vector por medio
    medio_vec = {
        medio: dict(zip(sdf["entity_canon"], sdf["count"]))
        for medio, sdf in mdf.groupby("Medio")
    }

    # referencia: suma global / suma MX / suma US
    global_sum = mdf.groupby("entity_canon")["count"].sum().to_dict()

    mx = mdf[mdf["country_group"] == "MX"]
    us = mdf[mdf["country_group"] == "US"]

    mx_sum = mx.groupby("entity_canon")["count"].sum().to_dict() if len(mx) else {}
    us_sum = us.groupby("entity_canon")["count"].sum().to_dict() if len(us) else {}

    for medio, v in medio_vec.items():
        rows.append({
            "month": month,
            "Medio": medio,
            "dist_to_global_mean": cosine_distance_from_dicts(v, global_sum),
            "dist_to_mx_mean": cosine_distance_from_dicts(v, mx_sum) if mx_sum else np.nan,
            "dist_to_us_mean": cosine_distance_from_dicts(v, us_sum) if us_sum else np.nan,
        })

out = pd.DataFrame(rows)
out.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Rows:", len(out), "| months:", out["month"].nunique(), "| medios:", out["Medio"].nunique())
print(out.head(5).to_string(index=False))
