#!/usr/bin/env python3
import os
import sys
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def _p(*parts: str) -> str:
    """Join paths from repo root."""
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(ROOT, *parts)

def load_nodes(nodes_path: str) -> list[str]:
    df = pd.read_csv(nodes_path)
    if "node" not in df.columns:
        raise ValueError(f"[ERROR] {nodes_path} must contain column 'node'. Columns: {list(df.columns)}")
    nodes = df["node"].astype(str).str.strip().tolist()
    nodes = [n for n in nodes if n]  # drop empty
    return nodes

def load_similarity_matrix(matrix_path: str) -> pd.DataFrame:
    A = pd.read_csv(matrix_path, index_col=0)
    # clean labels
    A.index = A.index.astype(str).str.strip()
    A.columns = A.columns.astype(str).str.strip()

    # if matrix accidentally loaded with unnamed column header issues:
    # ensure square and aligned
    if A.shape[0] != A.shape[1]:
        raise ValueError(f"[ERROR] Similarity matrix is not square: {A.shape}")
    # force same ordering of columns as index if possible
    if set(A.index) == set(A.columns):
        A = A.loc[A.index, A.index]
    return A

def main():
    # ---- Paths (robust even when running from scripts/)
    out_dir = _p("figures")
    os.makedirs(out_dir, exist_ok=True)

    # Prefer the canonical file, fallback to processed if needed
    matrix_path = _p("data", "similarity_matrix.csv")
    if not os.path.exists(matrix_path):
        # fallback: use processed cosine matrix if user hasn't copied it
        fallback = _p("data", "processed", "similarity_cosine.csv")
        if os.path.exists(fallback):
            print(f"[WARNING] {matrix_path} not found. Using fallback: {fallback}")
            matrix_path = fallback
        else:
            raise FileNotFoundError(
                f"[ERROR] Could not find similarity matrix.\n"
                f"Tried:\n - {matrix_path}\n - {fallback}\n"
                f"Tip: cp data/processed/similarity_cosine.csv data/similarity_matrix.csv"
            )

    nodes_path = _p("data", "processed", "consensus_nodes_topk3.csv")
    if not os.path.exists(nodes_path):
        raise FileNotFoundError(f"[ERROR] Missing nodes file: {nodes_path}")

    # ---- Load
    A = load_similarity_matrix(matrix_path)
    print("[INFO] Loaded similarity matrix:", A.shape)

    nodes = load_nodes(nodes_path)
    print("[INFO] Nodes requested:", len(nodes))

    # ---- Align nodes
    nodes_in = [n for n in nodes if n in A.index]
    missing = sorted(set(nodes) - set(nodes_in))
    if missing:
        print("[WARNING] Missing nodes (ignored):", missing)
    if len(nodes_in) < 2:
        raise ValueError("[ERROR] Not enough nodes found in similarity matrix after filtering.")

    nodes = nodes_in
    A = A.loc[nodes, nodes]

    # ---- Build graph
    G = nx.Graph()
    G.add_nodes_from(nodes)

    # threshold to remove tiny similarities
    THRESHOLD = 0.15

    # Use numpy for speed / consistency
    M = A.to_numpy(dtype=float)
    n = len(nodes)
    for i in range(n):
        for j in range(i + 1, n):
            w = M[i, j]
            if np.isfinite(w) and w > THRESHOLD:
                G.add_edge(nodes[i], nodes[j], weight=float(w))

    print("[INFO] Graph nodes:", G.number_of_nodes())
    print("[INFO] Graph edges:", G.number_of_edges())

    if G.number_of_edges() == 0:
        raise ValueError(
            f"[ERROR] Graph has 0 edges at THRESHOLD={THRESHOLD}. "
            f"Lower THRESHOLD or check matrix values."
        )

    # ---- Layout (stable)
    pos = nx.spring_layout(G, seed=42, k=0.6)

    # ---- Draw
    plt.figure(figsize=(10, 8))

    weights = [G[u][v]["weight"] * 4 for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=weights, alpha=0.4)
    nx.draw_networkx_nodes(G, pos, node_size=600)
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title("Figure 1 — Media Similarity Network", fontsize=14)
    plt.axis("off")

    output_path = os.path.join(out_dir, "fig1_network.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

    print("[OK] Figure saved to:", output_path)

if __name__ == "__main__":
    main()
