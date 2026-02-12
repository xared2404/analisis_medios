import pandas as pd
import re
import unicodedata

ART = "data/processed/articles_emotions.csv"
ENTS = "data/processed/entities_long.csv"
OUT  = "data/processed/entities_long_pro.csv"

CHUNK = 1_000_000  # ajusta si tu RAM lo requiere

def canon(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    s = s.replace("“","").replace("”","").replace('"',"").replace("'","")
    s = re.sub(r"\s+", " ", s)
    s = s.lower()
    # quitar acentos
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    # quitar puntuación
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def build_media_set(medios_raw):
    bases = set(canon(m) for m in medios_raw if isinstance(m, str) and m.strip())
    variants = set(bases)

    prefixes = ["diario", "periodico", "revista", "agencia", "portal"]
    suffixes = ["mx", "mexico", "com", "online", "digital", "news"]

    for b in list(bases):
        for p in prefixes:
            variants.add(f"{p} {b}")
        for s in suffixes:
            variants.add(f"{b} {s}")
        if b.startswith("el "):
            variants.add(b[3:])
        if b.startswith("la "):
            variants.add(b[3:])
        if b.startswith("the "):
            variants.add(b[4:])
    return variants

def build_agency_set():
    agencies = {
        "reuters", "agencia reuters",
        "associated press", "the associated press", "ap",
        "afp", "agence france presse", "france presse",
        "efe", "agencia efe",
        "dpa", "deutsche presse agentur",
        "ani", "tass",
        # broadcasters (marcarlos como media-like; tú decides filtrarlos o no)
        "cnn", "bbc", "fox news", "msnbc", "al jazeera"
    }
    return set(canon(a) for a in agencies)

def is_media_like(entity_canon: str, media_set: set, agency_set: set) -> int:
    """
    Heurística robusta:
    - match exacto
    - o contiene tokens típicos de agencia
    - o contiene el nombre de un medio conocido como frase
    """
    if not entity_canon:
        return 0

    if entity_canon in media_set or entity_canon in agency_set:
        return 1

    tokens = set(entity_canon.split())
    short_tokens = {"reuters", "afp", "efe", "ap", "cnn", "bbc", "fox", "msnbc", "aljazeera"}
    if tokens.intersection(short_tokens):
        return 1

    # contains check (frases)
    for m in media_set:
        if len(m) >= 6 and m in entity_canon:
            return 1
    for a in agency_set:
        if len(a) >= 3 and a in entity_canon:
            return 1

    return 0


# Load media list from articles table
df_art = pd.read_csv(ART, usecols=["Medio"])
medios_raw = df_art["Medio"].dropna().unique().tolist()

media_set = build_media_set(medios_raw)
agency_set = build_agency_set()

print("[INFO] media_set size :", len(media_set))
print("[INFO] agency_set size:", len(agency_set))

first = True
total_in = 0
total_out = 0

for chunk in pd.read_csv(ENTS, chunksize=CHUNK):
    total_in += len(chunk)

    # canonicalizar entidad
    chunk["entity_canon"] = chunk["entity"].map(canon)

    # filtrar vacíos
    chunk = chunk[chunk["entity_canon"] != ""]

    # bandera media/agencia (NO se elimina)
    chunk["is_media_like"] = chunk["entity_canon"].map(lambda e: is_media_like(e, media_set, agency_set)).astype("int8")

    # deduplicar por nota (URL+entidad canon)
    chunk = chunk.drop_duplicates(subset=["URL", "entity_canon"])

    # reducir columnas
    keep = ["URL","Medio","Seccion","fecha_real","predict_emotion","intensity","polarity",
            "entity_type","entity","entity_canon","is_media_like"]
    chunk_out = chunk[keep]

    chunk_out.to_csv(OUT, mode="w" if first else "a", index=False, header=first)
    first = False
    total_out += len(chunk_out)

print("[OK] entities PRO built (kept media/agencies, flagged)")
print("in :", total_in)
print("out:", total_out)
print("wrote:", OUT)
