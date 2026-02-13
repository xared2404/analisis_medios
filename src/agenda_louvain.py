import pandas as pd
import networkx as nx
import community as community_louvain

SIM_PATH = "data/processed/similarity_cosine.csv"
OUT_COMM = "data/processed/louvain_communities.csv"

THRESHOLD = 0.45  # puedes ajustar

print("[INFO] reading similarity matrix...")
sim = pd.read_csv(SIM_PATH, index_col=0)

medios = sim.index.tolist()

# construir grafo
G = nx.Graph()

for i in medios:
    for j in medios:
        if i == j:
            continue
        weight = sim.loc[i, j]
        if weight >= THRESHOLD:
            G.add_edge(i, j, weight=weight)

print("[INFO] nodes:", G.number_of_nodes())
print("[INFO] edges:", G.number_of_edges())

# Louvain
partition = community_louvain.best_partition(G, weight='weight')

# modularidad
modularity = community_louvain.modularity(partition, G, weight='weight')

print("\nModularity:", round(modularity, 4))

# export
comm_df = pd.DataFrame({
    "Medio": list(partition.keys()),
    "Community": list(partition.values())
}).sort_values("Community")

comm_df.to_csv(OUT_COMM, index=False)

print("\nCommunities detected:")
print(comm_df)

print("\nCommunity sizes:")
print(comm_df["Community"].value_counts())
