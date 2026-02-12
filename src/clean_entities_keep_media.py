import pandas as pd
import re
import unicodedata

ENTS = "data/processed/entities_long.csv"
OUT  = "data/processed/entities_long_clean_keep_media.csv"

CHUNK = 1_000_000  # ajusta si hace falta

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

first = True
total_in = 0
total_out = 0

for chunk in pd.read_csv(ENTS, chunksize=CHUNK):
    total_in += len(chunk)

    # canonicalizar
    chunk["entity_canon"] = chunk["entity"].map(canon)

    # filtrar vacíos
    chunk = chunk[chunk["entity_canon"] != ""]

    # deduplicar por nota: una entidad cuenta max 1 vez por URL
    chunk = chunk.drop_duplicates(subset=["URL", "entity_canon"])

    # mantener columnas (incluye entity original + canon)
    keep = ["URL","Medio","Seccion","fecha_real","predict_emotion","intensity","polarity","entity_type","entity","entity_canon"]
    chunk_out = chunk[keep]

    chunk_out.to_csv(OUT, mode="w" if first else "a", index=False, header=first)
    first = False
    total_out += len(chunk_out)

print("[OK] entities cleaned (KEEP media/agencies)")
print("in :", total_in)
print("out:", total_out)
print("wrote:", OUT)
