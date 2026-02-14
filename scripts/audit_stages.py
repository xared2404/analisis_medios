import pandas as pd
from pathlib import Path

BASE = Path("data/processed")

FILES = {
    "articles_emotions": BASE / "articles_emotions.csv",
    "entities_long": BASE / "entities_long.csv",
    "entities_long_clean": BASE / "entities_long_clean.csv",
    "entities_long_pro": BASE / "entities_long_pro.csv",
    "entities_long_pro_strict": BASE / "entities_long_pro_strict.csv",
    "entities_long_clean_keep_media": BASE / "entities_long_clean_keep_media.csv",
}

def safe_read(path: Path):
    if not path.exists():
        return None
    return pd.read_csv(path)

def count_unique(df, cols):
    if df is None: 
        return None
    for c in cols:
        if c not in df.columns:
            return None
    return df.dropna(subset=cols)[cols].astype(str).agg("|".join, axis=1).nunique()

def main():
    print("\n=== STAGE AUDIT (existing artifacts) ===")
    dfs = {k: safe_read(p) for k,p in FILES.items()}

    for k, df in dfs.items():
        if df is None:
            print(f"[MISS] {k}: file not found ({FILES[k]})")
            continue
        print(f"[OK] {k}: rows={len(df):,} cols={len(df.columns)}")

    # --- Try to infer "article id" columns commonly used ---
    # We'll check a few candidates and report which exists.
    id_candidates = ["_id", "id", "article_id", "url", "link", "guid", "Titulo", "title"]
    print("\n=== ID COLUMN PRESENCE ===")
    for name, df in dfs.items():
        if df is None: 
            continue
        present = [c for c in id_candidates if c in df.columns]
        print(f"{name}: {present if present else 'NO obvious id cols'}")

    # --- Articles coverage audit ---
    ae = dfs["articles_emotions"]
    if ae is not None:
        # Identify best id column among candidates
        id_col = next((c for c in ["_id","article_id","id","url","link","guid"] if c in ae.columns), None)
        print("\n=== ARTICLES_EMOTIONS COVERAGE ===")
        if id_col:
            print(f"Using id_col='{id_col}'")
            print("Unique articles:", ae[id_col].nunique())
        else:
            # fallback: unique by (Titulo, Medio) if exists
            if "Titulo" in ae.columns and "Medio" in ae.columns:
                print("Unique (Titulo,Medio):", count_unique(ae, ["Titulo","Medio"]))
            else:
                print("Cannot estimate unique articles (no id/url/link/guid and no (Titulo,Medio))")

        # empty text check
        txt_col = next((c for c in ["Texto","text","text_clean","paragraph","parrafo"] if c in ae.columns), None)
        if txt_col:
            print(f"Non-empty {txt_col}:", ae[txt_col].fillna("").str.strip().ne("").sum(), "/", len(ae))
        else:
            print("No obvious text column found in articles_emotions.csv")

    # --- Entities retention audit ---
    base = dfs["entities_long"]
    for variant in ["entities_long_clean","entities_long_pro","entities_long_pro_strict","entities_long_clean_keep_media"]:
        df = dfs.get(variant)
        if base is None or df is None:
            continue
        print(f"\n=== ENTITY RETENTION: {variant} vs entities_long ===")
        print("Rows:", f"{len(df):,} / {len(base):,}",
              f"({(len(df)/len(base)*100 if len(base)>0 else 0):.2f}%)")

        # compare unique entity strings if possible
        ent_col = next((c for c in ["Entidad","entity","ent_text","text"] if c in df.columns), None)
        if ent_col and ent_col in base.columns:
            print("Unique entities:", df[ent_col].nunique(), "/", base[ent_col].nunique())

    print("\n=== DONE ===")

if __name__ == "__main__":
    main()
