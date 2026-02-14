import pandas as pd

INP = "data/bi/top_entities_global_stage3.csv"
OUT = "data/bi/entity_taxonomy_stage3.csv"

df = pd.read_csv(INP)

df["scope"] = ""
df["notes"] = ""

df.to_csv(OUT, index=False)

print("[OK] wrote taxonomy template:", OUT)
print("Open and classify scope as:")
print("  national")
print("  international")
print("  regional")
print("  institutional")
print("  other")
