"""
Claves canónicas para comparar y desduplicar entidades por nombre+dirección+municipio.
"""
import re
import unicodedata
from typing import Iterable
from .text_utils import normalize_basic, remove_accents

_rm_punct = re.compile(r"[^\w\s]") 

def canonical_key(*parts: Iterable[str]) -> str:
    """
    Crea una clave robusta:
    - concatena partes no vacías,
    - normaliza espacios,
    - quita acentos,
    - elimina puntuación,
    - mayúsculas.
    """
    tokens = [normalize_basic(p) for p in parts if p]
    s = " ".join(tokens)
    s = remove_accents(s)
    s = _rm_punct.sub(" ", s)
    s = " ".join(s.split()).upper()
    return s
