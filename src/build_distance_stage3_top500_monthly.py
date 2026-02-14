import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

INP = "data/bi/agenda_counts_stage3_top500_monthly.csv"
OUT = "data/bi/distance_stage3_top500_monthly.csv"

df = pd.read_csv(INP)

rows_out = []

for month, sub in df.groupby("month"):

    pivot = sub.pivot_table(
        index="Medio",
        columns="entity_canon",
        values="count",
        fill_value=0
    )

    medios = pivot.index.tolist()
    X = pivot.to_numpy(dtype=float)

    S = cosine_similarity(X)

    for i in range(len(medios)):
        for j in range(i+1, len(medios)):
            rows_out.append({
                "month": month,
                "Medio_A": medios[i],
                "Medio_B": medios[j],
                "cosine": float(S[i,j])
            })

out = pd.DataFrame(rows_out)
out.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Rows:", len(out))
