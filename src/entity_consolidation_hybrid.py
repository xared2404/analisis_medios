import re
import unicodedata
import pandas as pd
from rapidfuzz import fuzz, process

# Entradas/salidas
IN_COUNTS = "data/processed/agenda_counts_non_media.csv"      # medio-entity-count (ya lo tienes)
OUT_COUNTS = "data/processed/agenda_counts_non_media_cons.csv" # consolidado
OUT_MAP = "data/processed/entity_map_hybrid.csv"              # mapping original->consolidated

# --- 1) Canon básico (tu entity_canon ya viene bien; aquí solo refuerzo limpieza) ---
def canon(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# --- 2) Reglas curadas (alta precisión) ---
RULES = {
    # EEUU / variantes
    "u s": "united states",
    "u s a": "united states",
    "us": "united states",
    "usa": "united states",
    "united states of america": "united states",
    "america": "united states",
    "american": "united states",
    "americans": "united states",

    # Trump
    "donald j trump": "donald trump",
    "president donald trump": "donald trump",
    
    # --- Trump variants ---
    "trump": "donald trump",
    "donald j trump": "donald trump",

    # --- Party variants ---
    "democratic": "democrat",
    "democrats": "democrat",
    "democratic party": "democrat",
    "democrats": "democrat",
    "republicans": "republican",
    
    # Harris (ojo: si luego metes otra Harris, la refinamos
    "harris": "kamala harris",

     # Sheinbaum
    "sheinbaum": "claudia sheinbaum",
    "claudia sheinbaum pardo": "claudia sheinbaum",

    # AMLO
    "amlo": "andres manuel lopez obrador",
    "lopez obrador": "andres manuel lopez obrador",
    
    # NYT/WaPo strings raros a veces
    "the times": "the new york times",
    "new york times": "the new york times",}
    "the new york times": "",
    "new york times": "",
    
# --- 3) Plural stripping muy conservador ---

def de_pluralize(s: str) -> str:
    # solo palabras simples: democrats -> democrat, republicans -> republican
    # evita romper "us" o siglas
    if len(s) <= 3:
        return s
    if s.endswith("ies") and len(s) > 4:
        return s[:-3] + "y"
    if s.endswith("s") and not s.endswith("ss"):
        return s[:-1]
    return s

# --- 4) Pipeline de consolidación base (reglas + plural) ---
def base_consolidate(ent: str) -> str:
    e = canon(ent)
    if not e:
        return ""
    if e in RULES:
        e = RULES[e]
    # plural simple palabra única
    if " " not in e:
        e2 = de_pluralize(e)
        # re-aplica regla si tras depluralize cae en algo conocido
        e = RULES.get(e2, e2)
    return e

def main():
    df = pd.read_csv(IN_COUNTS)
    df["entity_canon"] = df["entity_canon"].astype(str)

    # aplica consolidación base
    df["entity_base"] = df["entity_canon"].map(base_consolidate)

    # --- 5) Fuzzy SOLO en entidades frecuentes (controlado) ---
    # idea: si una entidad aparece mucho, vale la pena agrupar variantes (ej. democratic/democrats)
    # threshold de "frecuencia global" para entrar a fuzzy:
    MIN_GLOBAL = 800

    global_counts = df.groupby("entity_base")["count"].sum().sort_values(ascending=False)
    frequent = global_counts[global_counts >= MIN_GLOBAL].index.tolist()

    # diccionario final base->final
    base_to_final = {e: e for e in df["entity_base"].unique()}

    # fuzzy: construye clusters en el set frecuente
    # estrategia: recorre frecuentes por orden de volumen y "absorbe" variantes muy similares
    used = set()
    frequent_sorted = sorted(frequent, key=lambda x: global_counts[x], reverse=True)

    for anchor in frequent_sorted:
        if anchor in used:
            continue
        used.add(anchor)

        # candidatos: top matches para anchor dentro del universo frecuente
        matches = process.extract(
            anchor,
            frequent_sorted,
            scorer=fuzz.token_sort_ratio,
            limit=50
        )

        for cand, score, _ in matches:
            if cand == anchor or cand in used:
                continue
            # umbral alto para evitar falsos positivos
            if score >= 93:
                base_to_final[cand] = anchor
                used.add(cand)

    # aplica mapping final y agrega conteos
    df["entity_final"] = df["entity_base"].map(lambda x: base_to_final.get(x, x))

    cons = (
        df.groupby(["Medio", "entity_final"], as_index=False)["count"]
          .sum()
          .rename(columns={"entity_final": "entity_canon"})
    )

    cons.to_csv(OUT_COUNTS, index=False)

    # exporta mapping (útil para auditoría)
    mapping = (
        df[["entity_canon", "entity_base", "entity_final"]]
          .drop_duplicates()
          .rename(columns={"entity_final": "entity_consolidated"})
    )
    mapping.to_csv(OUT_MAP, index=False)

    print("[OK] wrote:", OUT_COUNTS, "rows=", len(cons))
    print("[OK] wrote:", OUT_MAP, "rows=", len(mapping))

    # sanity check: top 20 global
    top = cons.groupby("entity_canon")["count"].sum().sort_values(ascending=False).head(20)
    print("\nTop 20 global (consolidated):")
    print(top)

if __name__ == "__main__":
    main()
