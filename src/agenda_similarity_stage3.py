import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

INP = "data/processed/agenda_counts_stage3.csv"
OUT = "data/processed/similarity_cosine_stage3.csv"

df = pd.read_csv(INP, dtype={"Medio":"string","entity_canon":"string","count":"int64"})

medios = sorted(df["Medio"].unique())
entities = sorted(df["entity_canon"].unique())

m_index = {m:i for i,m in enumerate(medios)}
e_index = {e:i for i,e in enumerate(entities)}

rows = df["Medio"].map(m_index).to_numpy()
cols = df["entity_canon"].map(e_index).to_numpy()
vals = df["count"].to_numpy(dtype=float)

X = csr_matrix((vals, (rows, cols)), shape=(len(medios), len(entities)))

S = cosine_similarity(X)

# guardar long-form (parejas)
out = []
for i in range(len(medios)):
    for j in range(i+1, len(medios)):
        out.append((medios[i], medios[j], float(S[i, j])))

sim_df = pd.DataFrame(out, columns=["Medio_A","Medio_B","cosine"])
sim_df.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Pairs:", len(sim_df))
