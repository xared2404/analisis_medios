# src/hygiene.py
from __future__ import annotations

import ast
import json
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

LIST_FIELDS = ["Adjetivos", "Autor", "Entidades", "PalabrasClave", "Verbos"]
TEXT_FIELDS = ["Texto", "Titulo", "Descripcion", "Observaciones"]
KEEP_AS_STRING_FIELDS = ["Medio", "Seccion", "URL", "Imagen"]  # típicos

def _is_nan(x: Any) -> bool:
    return isinstance(x, float) and math.isnan(x)

def _coerce_none(v: Any) -> Optional[Any]:
    if v is None or _is_nan(v):
        return None
    if isinstance(v, str):
        s = v.strip()
        if s == "" or s.lower() == "nan" or s.lower() == "none":
            return None
    return v

def _parse_stringified_list(s: str) -> Optional[List[Any]]:
    s = s.strip()
    if s == "" or s.lower() == "nan":
        return []
    # JSON list
    if s.startswith("[") and s.endswith("]"):
        try:
            v = json.loads(s)
            if isinstance(v, list):
                return v
        except Exception:
            pass
        # Python literal list: "['a','b']"
        try:
            v = ast.literal_eval(s)
            if isinstance(v, list):
                return v
        except Exception:
            return None
    return None

def ensure_list(v: Any) -> List[Any]:
    v = _coerce_none(v)
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        parsed = _parse_stringified_list(v)
        if parsed is not None:
            return parsed
        # si viene un string suelto que NO es lista, lo tratamos como item único
        return [v.strip()] if v.strip() else []
    # cualquier otra cosa: lo envolvemos
    return [v]

def ensure_text(v: Any) -> Optional[str]:
    v = _coerce_none(v)
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        return s if s else None
    # otros tipos: stringify conservador
    return str(v)

@dataclass
class HygieneReport:
    had_stringified_lists: bool = False
    missing_text: bool = False
    fixes: List[str] = None

    def __post_init__(self):
        if self.fixes is None:
            self.fixes = []

def sanitize_doc(doc: Dict[str, Any]) -> Tuple[Dict[str, Any], HygieneReport]:
    out = dict(doc)
    rep = HygieneReport()

    # listas
    for f in LIST_FIELDS:
        if f in out:
            before = out.get(f)
            after = ensure_list(before)
            if isinstance(before, str) and before.strip().startswith("["):
                rep.had_stringified_lists = True
                rep.fixes.append(f"{f}: string->list")
            out[f] = after
        else:
            out[f] = []

    # texto
    for f in TEXT_FIELDS:
        if f in out:
            before = out.get(f)
            after = ensure_text(before)
            if before is not None and after is None:
                rep.fixes.append(f"{f}: blank->None")
            out[f] = after
        else:
            out[f] = None

    # check mínimo
    if not out.get("Texto") and not out.get("Titulo"):
        rep.missing_text = True

    return out, rep
