import pandas as pd
import re
import unicodedata

ART = "data/processed/articles_emotions.csv"
INP = "data/processed/entities_long_clean_keep_media.csv"
OUT = "data/processed/entities_long_pro_strict.csv"

CHUNK = 1000000

def canon(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    s = s.replace("“","").replace("”","").replace('"',"").replace("'","")
    s = re.sub(r"\s+", " ", s)
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def build_media_set(medios_raw):
    bases = set(canon(m) for m in medios_raw if isinstance(m, str) and m.strip())
    variants = set(bases)
    for b in list(bases):
        if b.startswith("el "):
            variants.add(b[3:])
        if b.startswith("la "):
            variants.add(b[3:])
        if b.startswith("the "):
            variants.add(b[4:])
    return variants

def build_agency_set():
    agencies = {
        "reuters", "associated press", "the associated press", "ap",
        "afp", "efe", "agencia efe", "agencia reuters",
        "dpa", "tass", "ani",
        "bbc", "cnn", "fox news", "msnbc", "al jazeera"
    }
    return set(canon(a) for a in agencies)

df_art = pd.read_csv(ART, usecols=["Medio"])
media_set = build_media_set(df_art["Medio"].dropna().unique().tolist())
agency_set = build_agency_set()

first = True
tot = 0
flagged = 0

for chunk in pd.read_csv(INP, chunksize=CHUNK):
    tot += len(chunk)

    if "entity_canon" not in chunk.columns:
        chunk["entity_canon"] = chunk["entity"].map(canon)

    ent = chunk["entity_canon"]
    etype = chunk["entity_type"].fillna("")

    exact_hit = ent.isin(media_set) | ent.isin(agency_set)
    org_hit = (etype == "ORG") & exact_hit

    chunk["is_media_like"] = (org_hit | exact_hit).astype("int8")

    flagged += int((chunk["is_media_like"]==1).sum())

    chunk.to_csv(OUT, mode="w" if first else "a", index=False, header=first)
    first = False

print("[OK] wrote:", OUT)
print("rows:", tot)
print("media_like:", flagged)
