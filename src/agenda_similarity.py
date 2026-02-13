import pandas as pd
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity

DATA = "data/processed/agenda_counts_non_media_cons.csv"
OUT_SIM = "data/processed/similarity_cosine.csv"
OUT_NN  = "data/processed/nearest_neighbors.csv"

# Control de tamaño: usa las entidades más frecuentes globalmente
TOPK_ENTITIES = 50000  # si quieres más fino: 100k (más RAM/tiempo)

# Opcional: remover self-entities obvias (si no las consolidaste a "")
DROP_SELF = set([
    "the new york times",
    "the washington post",
    "el universal",
    "infobae",
    "reuters",
    "efe",
    "afp",
    "associated press",
    "the associated press",
])

print("[INFO] reading counts...")
df = pd.read_csv(DATA)

# filtra self entities opcional
df = df[~df["entity_canon"].isin(DROP_SELF)]

# topK entidades por volumen global (para limitar vocabulario)
global_top = (df.groupby("entity_canon")["count"].sum()
                .sort_values(ascending=False)
                .head(TOPK_ENTITIES)
                .index)

df = df[df["entity_canon"].isin(global_top)].copy()

medios = sorted(df["Medio"].unique().tolist())
entities = sorted(df["entity_canon"].unique().tolist())

medio_index = {m:i for i,m in enumerate(medios)}
ent_index = {e:i for i,e in enumerate(entities)}

rows = df["Medio"].map(medio_index).to_numpy()
cols = df["entity_canon"].map(ent_index).to_numpy()
vals = df["count"].to_numpy(dtype=np.float64)

X = sparse.csr_matrix((vals, (rows, cols)), shape=(len(medios), len(entities)))

print("[INFO] matrix shape:", X.shape, "nnz:", X.nnz)

# TF-IDF sobre counts
tfidf = TfidfTransformer(norm="l2", use_idf=True, smooth_idf=True, sublinear_tf=True)
X_tfidf = tfidf.fit_transform(X)

# Cosine similarity entre medios (18x18)
S = cosine_similarity(X_tfidf)

sim_df = pd.DataFrame(S, index=medios, columns=medios)
sim_df.to_csv(OUT_SIM)
print("[OK] wrote:", OUT_SIM)

# Nearest neighbors (top 5, excluyendo sí mismo)
rows_out = []
for i, m in enumerate(medios):
    sims = list(enumerate(S[i]))
    sims = sorted(sims, key=lambda t: t[1], reverse=True)
    for j, score in sims[1:6]:
        rows_out.append({"Medio": m, "Neighbor": medios[j], "cosine": float(score)})

nn_df = pd.DataFrame(rows_out)
nn_df.to_csv(OUT_NN, index=False)
print("[OK] wrote:", OUT_NN)

# imprime preview
print("\nTop neighbors preview:")
print(nn_df.head(20))
