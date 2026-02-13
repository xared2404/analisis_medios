import pandas as pd
import networkx as nx

try:
    import community as community_louvain  # python-louvain
except ImportError:
    raise SystemExit("Falta dependencia: pip install python-louvain")

INP = "data/processed/similarity_cosine_stage3.csv"
OUT = "data/processed/louvain_communities_stage3.csv"

THRESH = 0.70  # tuned

df = pd.read_csv(INP)

G = nx.Graph()
for _, r in df.iterrows():
    w = float(r["cosine"])
    if w >= THRESH:
        G.add_edge(r["Medio_A"], r["Medio_B"], weight=w)

print("[INFO] nodes:", G.number_of_nodes())
print("[INFO] edges:", G.number_of_edges())

if G.number_of_nodes() == 0:
    raise SystemExit("Grafo vacío. Baja THRESH.")

part = community_louvain.best_partition(G, weight="weight")
out = pd.DataFrame(sorted(part.items()), columns=["Medio", "Community"])
out.to_csv(OUT, index=False)

# modularidad (extra útil)
mod = community_louvain.modularity(part, G, weight="weight")
print("[INFO] modularity:", mod)
print("[OK] wrote:", OUT)
print(out["Community"].value_counts())
