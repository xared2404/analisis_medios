import pandas as pd

COUNTS_IN = "data/bi/agenda_counts_stage3_monthly.csv"
SHARE_IN  = "data/bi/agenda_share_stage3_monthly.csv"

COUNTS_OUT = "data/bi/agenda_counts_stage3_monthly_dedup.csv"
SHARE_OUT  = "data/bi/agenda_share_stage3_monthly_dedup.csv"

# 1) COUNTS: colapsar duplicados por llave
c = pd.read_csv(COUNTS_IN, dtype={"month":"string","Medio":"string","entity_canon":"string"})
c["count"] = pd.to_numeric(c["count"], errors="coerce").fillna(0).astype("int64")

c2 = (
    c.groupby(["month","Medio","entity_canon"], as_index=False)["count"]
     .sum()
)

c2.to_csv(COUNTS_OUT, index=False)
print("[OK] wrote:", COUNTS_OUT, "| rows:", len(c2))

# 2) SHARES: recomputar desde counts dedup (más seguro)
tot = (
    c2.groupby(["month","Medio"], as_index=False)["count"]
      .sum()
      .rename(columns={"count":"total_medio_month"})
)

s = c2.merge(tot, on=["month","Medio"], how="left")
s["share_within_medio_month"] = s["count"] / s["total_medio_month"]

s.to_csv(SHARE_OUT, index=False)
print("[OK] wrote:", SHARE_OUT, "| rows:", len(s))

# sanity
dup_c = c2.duplicated(["month","Medio","entity_canon"]).sum()
dup_s = s.duplicated(["month","Medio","entity_canon"]).sum()
print("[INFO] duplicates after fix | counts:", dup_c, "| shares:", dup_s)
