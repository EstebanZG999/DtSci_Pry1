"""
Limpieza y validación de teléfonos en Guatemala.
Reglas:
- Números válidos: 8 dígitos locales; opcional prefijo +502 o 502.
- Separadores aceptados: coma, punto y coma, slash, barra vertical, espacio.
- Detecta 16 dígitos pegados (8+8) y los separa.
"""
from typing import List, Tuple
import re

SEP = r"[,\;/\|\s]+"
DIGITS = re.compile(r"\d+")
EXT_PAT = re.compile(r"\b(ext|ext\.|extensión|pbx)\b[:.\s]*\d*", flags=re.I)

def _split_candidates(raw: str) -> List[str]:
    # Usa separadores comunes
    parts = re.split(SEP, raw)
    parts = [p for p in parts if p.strip()]
    return parts if parts else [raw]

def _explode_digits_block(s: str) -> List[str]:
    # Si hay exactamente 16 dígitos, intenta separarlo en 8+8
    digits = re.sub(r"\D", "", s or "")
    if len(digits) == 16:
        return [digits[:8], digits[8:]]
    return [digits]

def strip_extensions(s: str) -> str:
    return EXT_PAT.sub("", s or "")

def _normalize_one(digits: str) -> str:
    # Quita prefijos 502 redundantes
    if digits.startswith("502") and len(digits) in (11, 13):
        digits = digits[-8:]
    # Si ya son 8 dígitos, ok
    if len(digits) == 8:
        return f"+502 {digits[:4]} {digits[4:]}"
    return ""

def parse_phones(raw: str) -> List[str]:
    if not raw:
        return []
    raw = strip_extensions(raw)  
    items = []
    for chunk in _split_candidates(raw):
        for block in _explode_digits_block(chunk):
            norm = _normalize_one(block)
            if norm:
                items.append(norm)
    # quitar duplicados preservando orden
    seen, out = set(), []
    for n in items:
        if n not in seen:
            seen.add(n); out.append(n)
    return out

def primary_phone(phones: List[str]) -> str:
    return phones[0] if phones else ""

def is_valid_gt_phone(raw: str) -> bool:
    return bool(parse_phones(raw))
