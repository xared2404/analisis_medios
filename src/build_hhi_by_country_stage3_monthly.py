#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

PROCESSED_DIR = Path("data/processed")
OUT = Path("data/bi/agenda_counts_stage3_monthly.csv")

# Candidatos típicos (ajusta/añade si hace falta)
CANDIDATES = [
    PROCESSED_DIR / "entities_long_clean_keep_media.csv",
    PROCESSED_DIR / "entities_long_clean.csv",
    PROCESSED_DIR / "entities_long_pro_strict.csv",
    PROCESSED_DIR / "entities_long_pro.csv",
    PROCESSED_DIR / "entities_long.csv",
    PROCESSED_DIR / "agenda_counts_stage2_mentions.csv",
    PROCESSED_DIR / "agenda_counts_stage3.csv",
]

def _pick_existing(candidates):
    return [p for p in candidates if p.exists()]

def _standardize_cols(df: pd.DataFrame) -> pd.DataFrame:
    # Normaliza nombres por si vienen como "medio", "source", etc.
    cols = {c: c.strip() for c in df.columns}
    df = df.rename(columns=cols)

    # Candidatos de columnas
    medio_candidates = ["Medio", "medio", "source", "outlet", "media", "sitio", "fuente"]
    entity_candidates = ["entity_canon", "entity", "entidad", "entity_norm", "canon", "Entity"]
    month_candidates = ["month", "Month", "mes"]
    date_candidates = ["date", "fecha", "published_at", "datetime", "created_at", "timestamp"]

    def find_first(name_list):
        for n in name_list:
            if n in df.columns:
                return n
        return None

    medio_col = find_first(medio_candidates)
    entity_col = find_first(entity_candidates)
    month_col = find_first(month_candidates)
    date_col = find_first(date_candidates)

    if medio_col is None or entity_col is None:
        raise ValueError(
            f"No encontré columnas requeridas. "
            f"Necesito algo tipo Medio y entity_canon. Columnas disponibles: {list(df.columns)}"
        )

    # Renombra a estándar
    if medio_col != "Medio":
        df = df.rename(columns={medio_col: "Medio"})
    if entity_col != "entity_canon":
        df = df.rename(columns={entity_col: "entity_canon"})

    # Construye month si no existe
    if month_col is None:
        if date_col is None:
            raise ValueError(
                "No encuentro 'month' ni una columna de fecha para derivarlo (date/fecha/published_at...). "
                f"Columnas: {list(df.columns)}"
            )
        # Parse fecha → month YYYY-MM
        dt = pd.to_datetime(df[date_col], errors="coerce", utc=False)
        if dt.isna().all():
            raise ValueError(f"La columna de fecha '{date_col}' no se pudo parsear.")
        df["month"] = dt.dt.to_period("M").astype(str)
    else:
        if month_col != "month":
            df = df.rename(columns={month_col: "month"})
        # Normaliza month a 'YYYY-MM'
        # si viene tipo '2024-02-01' o datetime, lo convertimos
        if pd.api.types.is_datetime64_any_dtype(df["month"]):
            df["month"] = df["month"].dt.to_period("M").astype(str)
        else:
            # intenta parsear; si falla, deja tal cual
            parsed = pd.to_datetime(df["month"], errors="coerce")
            mask = parsed.notna()
            df.loc[mask, "month"] = parsed.loc[mask].dt.to_period("M").astype(str)

    return df

def _build_from_df(df: pd.DataFrame) -> pd.DataFrame:
    # Si ya existe 'count', lo suma; si no, cuenta filas
    if "count" in df.columns:
        df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0).astype(int)
        out = (
            df.groupby(["month", "Medio", "entity_canon"], as_index=False)["count"]
              .sum()
        )
    else:
        out = (
            df.groupby(["month", "Medio", "entity_canon"], as_index=False)
              .size()
              .rename(columns={"size": "count"})
        )

    # Limpieza básica
    out["Medio"] = out["Medio"].astype(str).str.strip()
    out["entity_canon"] = out["entity_canon"].astype(str).str.strip()
    out = out[out["Medio"].ne("") & out["entity_canon"].ne("")]
    out = out[out["count"] > 0]

    # Orden
    out = out.sort_values(["month", "Medio", "count"], ascending=[True, True, False])
    return out

def main():
    existing = _pick_existing(CANDIDATES)
    if not existing:
        raise FileNotFoundError(
            "No encontré archivos candidatos en data/processed/. "
            "Ajusta la lista CANDIDATES con el archivo correcto que tenga Medio+entidad+fecha/mes."
        )

    last_err = None
    for path in existing:
        try:
            df = pd.read_csv(path)
            df = _standardize_cols(df)
            out = _build_from_df(df)

            # Si sale demasiado chico, probablemente no era el archivo correcto
            if len(out) < 10:
                raise ValueError(f"Resultado muy pequeño ({len(out)} filas). Probable fuente incorrecta: {path}")

            # Backup del OUT si existe
            OUT.parent.mkdir(parents=True, exist_ok=True)
            if OUT.exists():
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup = OUT.with_name(f"{OUT.stem}.bak_{ts}{OUT.suffix}")
                OUT.replace(backup)
                print(f"[BACKUP] {OUT} -> {backup}")

            out.to_csv(OUT, index=False)
            print(f"[OK] wrote: {OUT}")
            print("Rows:", len(out))
            print(out.head(5))
            print(f"[SOURCE] {path}")
            return

        except Exception as e:
            last_err = e
            print(f"[SKIP] {path} -> {e}")

    raise RuntimeError(f"No pude reconstruir el archivo con los candidatos. Último error: {last_err}")

if __name__ == "__main__":
    main()
