import pandas as pd
import re
import unicodedata

ART = "data/processed/articles_emotions.csv"
ENTS = "data/processed/entities_long.csv"
OUT = "data/processed/entities_long_clean.csv"

CHUNK = 1_000_000  # baja si te pega RAM

def canon(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    s = s.replace("“","").replace("”","").replace('"',"").replace("'","")
    s = re.sub(r"\s+", " ", s)
    s = s.lower()
    # quitar acentos
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    # quitar puntuación común
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def build_media_blacklist(medios_raw):
    """
    Crea blacklist robusta de medios:
    - exactos canonicalizados
    - variantes comunes (con 'diario', 'periodico', 'revista', etc.)
    """
    bases = set(canon(m) for m in medios_raw if isinstance(m, str) and m.strip())
    variants = set()

    prefixes = ["diario", "periodico", "revista", "agencia", "portal"]
    suffixes = ["mx", "mexico", "com", "online", "digital", "news"]

    for b in bases:
        variants.add(b)
        for p in prefixes:
            variants.add(f"{p} {b}")
        for s in suffixes:
            variants.add(f"{b} {s}")

    # también agrega versiones sin artículos iniciales
    for b in list(bases):
        if b.startswith("el "):
            variants.add(b[3:])
        if b.startswith("la "):
            variants.add(b[3:])
        if b.startswith("the "):
            variants.add(b[4:])

    return variants

def build_agency_blacklist():
    """
    Agencias y marcas periodísticas comunes (robusto a acentos/puntuación).
    Incluye variantes frecuentes.
    """
    agencies = {
        "reuters", "agencia reuters",
        "associated press", "the associated press", "ap",
        "afp", "agence france presse", "france presse",
        "efe", "agencia efe",
        "dpa", "deutsche presse agentur",
        "ani", "tass",
        "cnn", "bbc",  # opcional: si quieres excluir broadcasters como "entidad"
    }
    return set(canon(a) for a in agencies)

def looks_like_media_or_agency(entity_canon: str, media_set: set, agency_set: set) -> bool:
    """
    Regla robusta:
    - match exacto en medios/agencias
    - o contiene el nombre de un medio/agencia como token significativo
      (ej: "el universal deportes" o "reuters staff")
    """
    if not entity_canon:
        return True

    if entity_canon in media_set or entity_canon in agency_set:
        return True

    # token check para evitar falsos positivos por substrings raros
    tokens = set(entity_canon.split())
    # match tokenizado con nombres cortos
    short_agency_tokens = {"reuters", "afp", "efe", "ap", "bbc", "cnn"}
    if tokens.intersection(short_agency_tokens):
        return True

    # contains check (frases)
    # (esto atrapa "el universal deportes", "infobae mexico", "agencia reuters", etc.)
    for m in media_set:
        if len(m) >= 6 and m in entity_canon:
            return True
    for a in agency_set:
        if len(a) >= 3 and a in entity_canon:
            return True

    return False

# 1) cargar medios reales del dataset
df_art = pd.read_csv(ART, usecols=["Medio"])
medios_raw = df_art["Medio"].dropna().unique().tolist()

media_set = build_media_blacklist(medios_raw)
agency_set = build_agency_blacklist()

print("[INFO] media blacklist size:", len(media_set))
print("[INFO] agency blacklist size:", len(agency_set))

# 2) limpiar entidades por chunks
first = True
total_in = 0
total_out = 0

for chunk in pd.read_csv(ENTS, chunksize=CHUNK):
    total_in += len(chunk)

    chunk["entity_canon"] = chunk["entity"].map(canon)

    # filtrar vacíos
    chunk = chunk[chunk["entity_canon"] != ""]

    # filtrar medios/agencias con heurística robusta
    mask_drop = (
        chunk["entity_type"].isin(["ORG","MISC"]) &
        chunk["entity_canon"].map(lambda e: looks_like_media_or_agency(e, media_set, agency_set))
    )
    chunk = chunk[~mask_drop]

    # deduplicar por URL + entidad canon (una entidad cuenta máximo 1 vez por nota)
    chunk = chunk.drop_duplicates(subset=["URL", "entity_canon"])

    # reducir columnas
    keep = ["URL","Medio","Seccion","fecha_real","predict_emotion","intensity","polarity","entity_type","entity","entity_canon"]
    chunk_out = chunk[keep]

    chunk_out.to_csv(OUT, mode="w" if first else "a", index=False, header=first)
    first = False
    total_out += len(chunk_out)

print("[OK] entities cleaned")
print("in :", total_in)
print("out:", total_out)
print("wrote:", OUT)
