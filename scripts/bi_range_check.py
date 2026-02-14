import pandas as pd

# scope shares in [0,1] and sum approx 1
df = pd.read_csv("data/bi/scope_stage3_top500_monthly.csv")
print("\n=== scope_stage3_top500_monthly ===")
print("min/max national:", df["share_national"].min(), df["share_national"].max())
print("min/max intl:", df["share_international"].min(), df["share_international"].max())
s = (df["share_national"] + df["share_international"])
print("sum min/max:", s.min(), s.max())

# agenda shares in [0,1]
df2 = pd.read_csv("data/bi/agenda_share_stage3_monthly.csv")
print("\n=== agenda_share_stage3_monthly ===")
print("share min/max:", df2["share_within_medio_month"].min(), df2["share_within_medio_month"].max())

# distances cosine in [0,1]
df3 = pd.read_csv("data/bi/distance_stage3_top500_monthly.csv")
print("\n=== distance_stage3_top500_monthly ===")
print("cosine min/max:", df3["cosine"].min(), df3["cosine"].max())

print("\n[DONE] range check")
