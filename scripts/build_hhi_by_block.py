import argparse
import pandas as pd

def compute_hhi(df: pd.DataFrame, month_col: str, block_col: str, item_col: str, weight_col: str) -> pd.DataFrame:
    # Limpieza mínima
    df = df[[month_col, block_col, item_col, weight_col]].dropna()
    df[weight_col] = pd.to_numeric(df[weight_col], errors="coerce").fillna(0.0)

    # Suma por (month, block, item) por si hay duplicados
    g = df.groupby([month_col, block_col, item_col], as_index=False)[weight_col].sum()

    # Total por (month, block)
    totals = g.groupby([month_col, block_col], as_index=False)[weight_col].sum().rename(columns={weight_col: "total_weight"})
    g = g.merge(totals, on=[month_col, block_col], how="left")

    # p_i
    g["p"] = g[weight_col] / g["total_weight"].replace({0: pd.NA})
    g["p2"] = g["p"] ** 2

    # HHI
    hhi = g.groupby([month_col, block_col], as_index=False)["p2"].sum().rename(columns={"p2": "hhi"})

    return hhi

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV/Parquet con month, country_group, item, weight")
    ap.add_argument("--output", required=True, help="Salida CSV/Parquet")
    ap.add_argument("--month-col", default="month")
    ap.add_argument("--block-col", default="country_group")
    ap.add_argument("--item-col", default="item")
    ap.add_argument("--weight-col", default="weight")
    args = ap.parse_args()

    # Carga
    if args.input.lower().endswith(".parquet"):
        df = pd.read_parquet(args.input)
    else:
        df = pd.read_csv(args.input)

    hhi = compute_hhi(df, args.month_col, args.block_col, args.item_col, args.weight_col)

    # Orden
    hhi = hhi.sort_values([args.block_col, args.month_col])

    # Guarda
    if args.output.lower().endswith(".parquet"):
        hhi.to_parquet(args.output, index=False)
    else:
        hhi.to_csv(args.output, index=False)

    print("[OK] wrote:", args.output, "rows=", len(hhi))

if __name__ == "__main__":
    main()
