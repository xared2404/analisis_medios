"""
figures_results.py

Genera:
- Fig1: red baseline coloreada (p=0)
- Fig2: modularity vs noise
- Fig3: consensus entropy H vs noise
- Fig4: VI vs noise
- Fig5: overlay Q y H vs noise

Requisitos:
pip install numpy pandas matplotlib networkx
(opcional) python-louvain si recalculas comunidades aquí, pero este script asume que YA tienes particiones.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx


# -----------------------------
# Helpers: entropy + VI
# -----------------------------

def safe_log(x: float) -> float:
    # para 0*log(0)=0
    if x <= 0.0:
        return 0.0
    return math.log(x)

def consensus_matrix(partitions: np.ndarray) -> np.ndarray:
    """
    partitions: shape (R, N) labels enteros/string
    retorna C: (N, N) con prob co-asignación.
    """
    R, N = partitions.shape
    C = np.zeros((N, N), dtype=float)
    for r in range(R):
        lab = partitions[r]
        # co-asignación: matriz booleana NxN
        same = (lab[:, None] == lab[None, :]).astype(float)
        C += same
    C /= float(R)
    return C

def consensus_entropy(C: np.ndarray, symmetric_unordered: bool = True) -> float:
    """
    H = - 1/(N(N-1)) sum_{i!=j} [Cij log Cij + (1-Cij) log(1-Cij)]
    Si symmetric_unordered=True, promediamos sobre pares no ordenados i<j y normalizamos por N(N-1)/2
    (equivalente a la redacción "unordered distinct node pairs counted symmetrically").
    """
    N = C.shape[0]
    if symmetric_unordered:
        denom = N * (N - 1) / 2.0
        s = 0.0
        for i in range(N):
            for j in range(i + 1, N):
                pij = float(C[i, j])
                s += (pij * safe_log(pij) + (1.0 - pij) * safe_log(1.0 - pij))
        return -s / denom if denom > 0 else 0.0
    else:
        denom = N * (N - 1)
        s = 0.0
        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                pij = float(C[i, j])
                s += (pij * safe_log(pij) + (1.0 - pij) * safe_log(1.0 - pij))
        return -s / denom if denom > 0 else 0.0

def partition_entropy(labels: np.ndarray) -> float:
    """
    Shannon entropy H(X) de la distribución de etiquetas.
    """
    _, counts = np.unique(labels, return_counts=True)
    p = counts / counts.sum()
    return float(-np.sum([pi * safe_log(float(pi)) for pi in p]))

def mutual_information(x: np.ndarray, y: np.ndarray) -> float:
    """
    I(X;Y) para dos particiones (labels).
    """
    x_vals, x_inv = np.unique(x, return_inverse=True)
    y_vals, y_inv = np.unique(y, return_inverse=True)

    # tabla conjunta
    joint = np.zeros((len(x_vals), len(y_vals)), dtype=float)
    for i in range(len(x_inv)):
        joint[x_inv[i], y_inv[i]] += 1.0
    joint /= joint.sum()

    px = joint.sum(axis=1, keepdims=True)
    py = joint.sum(axis=0, keepdims=True)

    mi = 0.0
    for i in range(joint.shape[0]):
        for j in range(joint.shape[1]):
            pxy = joint[i, j]
            if pxy <= 0:
                continue
            mi += float(pxy) * (safe_log(float(pxy)) - safe_log(float(px[i, 0])) - safe_log(float(py[0, j])))
    return float(mi)

def variation_of_information(x: np.ndarray, y: np.ndarray) -> float:
    """
    VI(X,Y)=H(X)+H(Y)-2I(X;Y)
    """
    hx = partition_entropy(x)
    hy = partition_entropy(y)
    ixy = mutual_information(x, y)
    return float(hx + hy - 2.0 * ixy)

def mean_pairwise_vi(partitions: np.ndarray, max_pairs: int | None = 300) -> float:
    """
    Promedio de VI entre pares de particiones dentro de un mismo p.
    Para R=50, pares=1225; puedes computar todos o samplear.
    """
    R = partitions.shape[0]
    pairs = [(i, j) for i in range(R) for j in range(i + 1, R)]
    if max_pairs is not None and len(pairs) > max_pairs:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(pairs), size=max_pairs, replace=False)
        pairs = [pairs[k] for k in idx]

    vis = []
    for i, j in pairs:
        vis.append(variation_of_information(partitions[i], partitions[j]))
    return float(np.mean(vis)) if vis else 0.0


# -----------------------------
# Data container
# -----------------------------

@dataclass
class Run:
    Q: float
    partition: np.ndarray  # shape (N,)

@dataclass
class NoiseLevelData:
    p: float
    runs: List[Run]  # length R


# -----------------------------
# ADAPTER: carga tus resultados
# -----------------------------

def load_results_from_json(path: str | Path) -> List[NoiseLevelData]:
    """
    Espera un JSON con estructura ejemplo:

    {
      "nodes": ["Animal Politico", "El Universal", ...],   # opcional pero recomendado
      "levels": [
        {"p": 0.0, "runs": [{"Q": 0.12, "partition": [0,0,1,...]}, ...]},
        {"p": 0.1, "runs": [{"Q": 0.10, "partition": [...]}, ...]}
      ]
    }

    Ajusta aquí si tu formato es distinto.
    """
    path = Path(path)
    obj = json.loads(path.read_text(encoding="utf-8"))
    levels = []
    for lvl in obj["levels"]:
        p = float(lvl["p"])
        runs = []
        for r in lvl["runs"]:
            runs.append(Run(Q=float(r["Q"]), partition=np.array(r["partition"])))
        levels.append(NoiseLevelData(p=p, runs=runs))
    return levels, obj.get("nodes", None)

# Si no tienes JSON, puedes armarlo desde tus outputs.
# Ejemplo de minimal JSON (p=0, p=0.1):
# {"levels":[{"p":0.0,"runs":[{"Q":0.08,"partition":[0,1,1,...]}, ...]}, ...]}


# -----------------------------
# Figures
# -----------------------------

def fig1_network_baseline(G: nx.Graph, nodes: List[str], partition: np.ndarray, outpath: Path) -> None:
    """
    Fig1: red con color por comunidad (baseline).
    """
    plt.figure()
    pos = nx.spring_layout(G, seed=42)
    # map labels -> color index
    labs = partition
    uniq = {lab: i for i, lab in enumerate(np.unique(labs))}
    colors = [uniq[labs[i]] for i in range(len(nodes))]

    nx.draw_networkx_edges(G, pos, alpha=0.4)
    nx.draw_networkx_nodes(G, pos, node_color=colors)
    nx.draw_networkx_labels(G, pos, labels={i: nodes[i] for i in range(len(nodes))}, font_size=8)

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()

def plot_line_with_ci(df: pd.DataFrame, x: str, y: str, ylo: str | None, yhi: str | None,
                      title: str, xlabel: str, ylabel: str, outpath: Path) -> None:
    plt.figure()
    plt.plot(df[x], df[y])
    if ylo and yhi:
        plt.fill_between(df[x], df[ylo], df[yhi], alpha=0.2)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


# -----------------------------
# Main compute
# -----------------------------

def summarize(levels: List[NoiseLevelData]) -> pd.DataFrame:
    rows = []
    for lvl in sorted(levels, key=lambda z: z.p):
        p = lvl.p
        Qs = np.array([r.Q for r in lvl.runs], dtype=float)
        parts = np.stack([r.partition for r in lvl.runs], axis=0)  # (R,N)

        C = consensus_matrix(parts)
        H = consensus_entropy(C, symmetric_unordered=True)
        VI = mean_pairwise_vi(parts, max_pairs=None)  # con R=50, pares=1225, esto es ok

        rows.append({
            "p": p,
            "Q_mean": float(Qs.mean()),
            "Q_std": float(Qs.std(ddof=1)) if len(Qs) > 1 else 0.0,
            "Q_lo": float(np.quantile(Qs, 0.25)),
            "Q_hi": float(np.quantile(Qs, 0.75)),
            "H": H,
            "VI": VI
        })
    return pd.DataFrame(rows)

def fig2_modularity(df: pd.DataFrame, outdir: Path) -> None:
    plot_line_with_ci(
        df, x="p", y="Q_mean", ylo="Q_lo", yhi="Q_hi",
        title="Modularity vs noise", xlabel="Noise level p", ylabel="Modularity Q",
        outpath=outdir / "Fig2_modularity_vs_noise.png"
    )

def fig3_entropy(df: pd.DataFrame, outdir: Path) -> None:
    plt.figure()
    plt.plot(df["p"], df["H"])
    plt.title("Consensus entropy vs noise")
    plt.xlabel("Noise level p")
    plt.ylabel("Consensus entropy H")
    plt.tight_layout()
    plt.savefig(outdir / "Fig3_entropy_vs_noise.png", dpi=300)
    plt.close()

def fig4_vi(df: pd.DataFrame, outdir: Path) -> None:
    plt.figure()
    plt.plot(df["p"], df["VI"])
    plt.title("Variation of Information vs noise")
    plt.xlabel("Noise level p")
    plt.ylabel("Mean pairwise VI")
    plt.tight_layout()
    plt.savefig(outdir / "Fig4_VI_vs_noise.png", dpi=300)
    plt.close()

def fig5_overlay(df: pd.DataFrame, outdir: Path) -> None:
    plt.figure()
    plt.plot(df["p"], df["Q_mean"], label="Modularity Q (mean)")
    plt.plot(df["p"], df["H"], label="Consensus entropy H")
    plt.title("Detectability without identifiability: Q and H vs noise")
    plt.xlabel("Noise level p")
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "Fig5_overlay_Q_H.png", dpi=300)
    plt.close()


def build_graph_from_adjacency(A: np.ndarray) -> nx.Graph:
    """
    A: NxN simétrica, diagonal 0.
    """
    N = A.shape[0]
    G = nx.Graph()
    G.add_nodes_from(range(N))
    for i in range(N):
        for j in range(i + 1, N):
            w = float(A[i, j])
            if w != 0.0:
                G.add_edge(i, j, weight=w)
    return G


def main():
    # -------------------------
    # 1) CARGA TUS RESULTADOS
    # -------------------------
    # Cambia esta ruta al JSON que exportes desde tu pipeline
    results_path = Path("outputs/perturbation_runs.json")
    levels, nodes = load_results_from_json(results_path)

    # (opcional) si guardaste adjacency matrix para p=0:
    # A0 = np.load("outputs/adjacency_p0.npy")
    # G0 = build_graph_from_adjacency(A0)

    # Si NO tienes A0, pero sí tienes el grafo en edge list:
    # G0 = nx.read_weighted_edgelist("outputs/graph_p0.edgelist", nodetype=int)

    # Si no hay nombres de nodos:
    if nodes is None:
        N = len(levels[0].runs[0].partition)
        nodes = [f"node_{i}" for i in range(N)]

    outdir = Path("paper_figures")
    outdir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # 2) RESUMEN (Q, H, VI)
    # -------------------------
    df = summarize(levels)
    df.to_csv(outdir / "summary_by_p.csv", index=False)

    # -------------------------
    # 3) FIGURAS 2-5
    # -------------------------
    fig2_modularity(df, outdir)
    fig3_entropy(df, outdir)
    fig4_vi(df, outdir)
    fig5_overlay(df, outdir)

    # -------------------------
    # 4) FIGURA 1 (baseline)
    # -------------------------
    # Necesitas G0 (p=0) para visualizar la red.
    # Si ya tienes A0 o edgelist, descomenta.
    #
    # baseline = next(l for l in levels if abs(l.p - 0.0) < 1e-12)
    # # elige el run de mayor modularity (o el primero)
    # best = max(baseline.runs, key=lambda r: r.Q)
    # fig1_network_baseline(G0, nodes, best.partition, outdir / "Fig1_network_baseline.png")

    print("OK: Figuras y CSV en:", outdir.resolve())

if __name__ == "__main__":
    main()