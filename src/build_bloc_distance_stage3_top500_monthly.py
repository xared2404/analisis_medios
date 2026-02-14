import pandas as pd

INP = "data/bi/distance_stage3_top500_monthly.csv"
META = "data/bi/media_metadata.csv"
OUT = "data/bi/bloc_distance_stage3_top500_monthly.csv"

dist = pd.read_csv(INP)
meta = pd.read_csv(META)

# --- detect country column ---
cols = set(meta.columns)

# prefer explicit ISO-ish columns if present, else country_group
if "country" in cols:
    ccol = "country"
elif "Country" in cols:
    ccol = "Country"
elif "country_group" in cols:
    ccol = "country_group"
elif "group" in cols:
    ccol = "group"
else:
    raise SystemExit(f"[ERROR] Cannot find country column in {META}. Columns={list(meta.columns)}")

meta_dict = dict(zip(meta["Medio"], meta[ccol]))

rows = []

for month, sub in dist.groupby("month", sort=True):
    mx_mx = []
    us_us = []
    mx_us = []

    for _, r in sub.iterrows():
        a = meta_dict.get(r["Medio_A"])
        b = meta_dict.get(r["Medio_B"])
        c = float(r["cosine"])

        if a is None or b is None:
            continue

        if a == "MX" and b == "MX":
            mx_mx.append(c)
        elif a == "US" and b == "US":
            us_us.append(c)
        elif a != b:
            mx_us.append(c)

    rows.append({
        "month": month,
        "mx_mx_mean": sum(mx_mx)/len(mx_mx) if mx_mx else None,
        "us_us_mean": sum(us_us)/len(us_us) if us_us else None,
        "mx_us_mean": sum(mx_us)/len(mx_us) if mx_us else None,
        "mx_mx_n": len(mx_mx),
        "us_us_n": len(us_us),
        "mx_us_n": len(mx_us),
    })

out = pd.DataFrame(rows)
out.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Months:", len(out))
print("Used country column:", ccol)
print(out.head(10).to_string(index=False))
