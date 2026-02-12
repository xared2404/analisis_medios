import os
import ast
from typing import Any, List, Tuple
from dotenv import load_dotenv

def load_env() -> None:
    load_dotenv()

def must_getenv(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Missing required env var: {key}")
    return val

def safe_literal_list(x: Any):
    """
    Parse strings like:
      "['a','b']" -> ['a','b']
      '[["Loret","PER"], ["INE","ORG"]]' -> list
    Returns [] if empty/invalid.
    """
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if not isinstance(x, str):
        return []
    s = x.strip()
    if s in ("", "[]", "NaN", "nan", "None", "null"):
        return []
    try:
        return ast.literal_eval(s)
    except Exception:
        return []

def is_probably_landing_url(url: str) -> bool:
    """
    Filters obvious landing pages we already saw:
    - https://animalpolitico.com/analisis
    - https://animalpolitico.com/analisis/autores
    Extendable later.
    """
    if not isinstance(url, str):
        return True
    u = url.rstrip("/")
    if u.endswith("/analisis") or u.endswith("/analisis/autores"):
        return True
    return False

def normalize_entity_item(ent: Any) -> Tuple[str, str]:
    """
    Expected entity format: ["Debates", "MISC"] or ("Debates","MISC").
    Returns (entity, entity_type). If invalid -> ("","")
    """
    if isinstance(ent, (list, tuple)) and len(ent) >= 2:
        name = str(ent[0]).strip()
        etype = str(ent[1]).strip()
        return name, etype
    return "", ""
