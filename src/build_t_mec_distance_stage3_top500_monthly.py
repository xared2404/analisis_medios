import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

INP = "data/bi/agenda_counts_stage3_monthly.csv"
META = "data/bi/media_metadata.csv"
OUT = "data/bi/t_mec_distance_stage3_top500_monthly.csv"

keywords = ["t-mec", "tmec", "usmca", "nafta", "tratado mexico"]

df = pd.read_csv(INP)
meta = pd.read_csv(META)

meta_dict = dict(zip(meta["Medio"], meta["country_group"]))

df["scope_match"] = df["entity_canon"].str.lower().apply(
    lambda x: any(k in str(x) for k in keywords)
)

df = df[df["scope_match"]].copy()

rows = []

for month in df["month"].unique():
    sub = df[df["month"] == month]

    medios = sub["Medio"].unique()
    entities = sub["entity_canon"].unique()

    m_index = {m:i for i,m in enumerate(medios)}
    e_index = {e:i for i,e in enumerate(entities)}

    r = sub["Medio"].map(m_index)
    c = sub["entity_canon"].map(e_index)
    v = sub["count"]

    X = csr_matrix((v, (r, c)), shape=(len(medios), len(entities)))

    S = cosine_similarity(X)

    mx_us = []

    for i,m1 in enumerate(medios):
        for j,m2 in enumerate(medios):
            if j <= i:
                continue
            a = meta_dict.get(m1)
            b = meta_dict.get(m2)

            if a != b:
                mx_us.append(S[i,j])

    rows.append({
        "month": month,
        "mx_us_mean_t_mec": sum(mx_us)/len(mx_us) if mx_us else None
    })

out = pd.DataFrame(rows)
out.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print(out.head())
