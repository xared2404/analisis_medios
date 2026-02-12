from __future__ import annotations

from pymongo import MongoClient
import pandas as pd
from tqdm import tqdm

from utils import load_env, must_getenv, safe_literal_list, normalize_entity_item, is_probably_landing_url


FIELDS = {
    "URL": 1,
    "Medio": 1,
    "Seccion": 1,
    "Fecha": 1,
    "fecha_real": 1,
    "Titulo": 1,
    "text_clean": 1,
    "predict_emotion": 1,
    "others": 1,
    "joy": 1,
    "sadness": 1,
    "anger": 1,
    "surprise": 1,
    "disgust": 1,
    "fear": 1,
    "hateful": 1,
    "aggressive": 1,
    "targeted": 1,
    "hateful_bin": 1,
    "aggressive_bin": 1,
    "targeted_bin": 1,
    "predict_irony": 1,
    "ironic": 1,
    "not ironic": 1,   # field with space
    "ironic_bin": 1,
    "Entidades": 1,
    "PalabrasClave": 1,
}


def main() -> None:
    load_env()
    uri = must_getenv("MONGO_URI")
    db_name = must_getenv("MONGO_DB")
    coll_name = must_getenv("MONGO_COLLECTION")

    client = MongoClient(uri)
    db = client[db_name]
    coll = db[coll_name]

    # Query: only docs with fecha_real
    query = {"fecha_real": {"$ne": None}}

    print(f"[INFO] Reading from {db_name}.{coll_name} ...")
    cursor = coll.find(query, FIELDS, no_cursor_timeout=True).batch_size(2000)

    data = []
    try:
        for doc in tqdm(cursor, desc="mongo->list"):
            data.append(doc)
    finally:
        cursor.close()

    df = pd.DataFrame(data)
    print("[INFO] Raw rows:", len(df))

    # Drop Mongo's internal _id to avoid confusion
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])

    # Filter landing URLs
    df = df[~df["URL"].apply(is_probably_landing_url)].copy()
    print("[INFO] After landing-url filter:", len(df))

    # Parse serialized lists
    df["Entidades"] = df["Entidades"].apply(safe_literal_list)
    df["PalabrasClave"] = df["PalabrasClave"].apply(safe_literal_list)

    # Derived metrics
    # intensity: "negative-ish" affect load (you can revise later)
    for col in ["anger", "sadness", "fear", "disgust", "joy", "surprise", "others"]:
        if col not in df.columns:
            df[col] = 0.0
    df["intensity"] = df[["anger", "sadness", "fear", "disgust"]].sum(axis=1)
    df["polarity"] = (df["anger"] - df["joy"]).abs()
    df["entity_count"] = df["Entidades"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    df["keyword_count"] = df["PalabrasClave"].apply(lambda x: len(x) if isinstance(x, list) else 0)

    # Save articles table
    out_articles = "data/processed/articles_emotions.csv"
    df.to_csv(out_articles, index=False)
    print("[OK] wrote:", out_articles, "shape=", df.shape)

    # Build entities long table
    rows = []
    # Keep only needed columns for speed
    keep_cols = ["URL", "Medio", "Seccion", "fecha_real", "Titulo", "predict_emotion", "intensity", "polarity", "Entidades"]
    missing = [c for c in keep_cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing expected columns: {missing}")

    for _, r in tqdm(df[keep_cols].iterrows(), total=len(df), desc="entities_long"):
        ents = r["Entidades"]
        if not isinstance(ents, list) or len(ents) == 0:
            continue
        for ent in ents:
            name, etype = normalize_entity_item(ent)
            if not name:
                continue
            rows.append({
                "URL": r["URL"],
                "Medio": r["Medio"],
                "Seccion": r["Seccion"],
                "fecha_real": r["fecha_real"],
                "Titulo": r["Titulo"],
                "predict_emotion": r["predict_emotion"],
                "intensity": r["intensity"],
                "polarity": r["polarity"],
                "entity": name,
                "entity_type": etype
            })

    entities_df = pd.DataFrame(rows)
    out_entities = "data/processed/entities_long.csv"
    entities_df.to_csv(out_entities, index=False)
    print("[OK] wrote:", out_entities, "shape=", entities_df.shape)


if __name__ == "__main__":
    main()
