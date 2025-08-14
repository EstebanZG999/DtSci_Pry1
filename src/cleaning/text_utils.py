"""
Funciones de normalización y manipulación de texto.
Reglas:
- Convierte comillas tipográficas y otros símbolos a equivalentes ASCII simples.
- Soporta conversión a mayúsculas o formato 'title case' en español.
- Elimina espacios duplicados, caracteres invisibles y tildes si es necesario.
- Mantiene coherencia en separación por guiones y comas.
- Funciones puras: no modifican el input original fuera de su retorno.
"""

import re, unicodedata

MINOR_WORDS_ES = {"a","ante","bajo","cabe","con","contra","de","del","desde","durante","en","entre","hacia","hasta","mediante","para","por","según","sin","sobre","tras","y","o","u","e","la","las","el","los","un","una","unos","unas","al","del"}

ACRONYMS = {"INED","INEB","INE","USAC","UVG","IUSI","EORM","IPM"}

def nfc(s): 
    return unicodedata.normalize("NFC", "" if s is None else str(s))

def collapse_spaces(s): 
    return re.sub(r"\s+"," ", s or "").strip()


def strip_control_chars(s: str) -> str:
    return "".join(ch for ch in nfc(s) if ch.isprintable())

def normalize_basic(s): 
    return collapse_spaces(strip_control_chars(s))

def split_parentheses(s: str):
    if not s:
        return s, ""
    base, notes = s, []
    while True:
        m = re.search(r"(.*?)(\s*\(([^()]*)\)\s*)$", base)
        if not m:
            break
        base, note = m.group(1).strip(), m.group(3).strip()
        if note:
            notes.append(note)
        else:
            break
    return base, "; ".join(reversed(notes))

def to_upper(s): 
    return normalize_basic(s).upper()

def remove_accents(s):
    nfkd = unicodedata.normalize("NFKD", nfc(s))
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


SMART_QUOTES_MAP = {
    "“": '"', "”": '"', "„": '"', "‟": '"', "«": '"', "»": '"',
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
}

def normalize_quotes(s: str) -> str:
    if s is None:
        return ""
    out = unicodedata.normalize("NFC", str(s))
    # Sustituye comillas por rectas
    for k, v in SMART_QUOTES_MAP.items():
        out = out.replace(k, v)
    # Colapsa comillas repetidas
    out = re.sub(r'"+', '"', out)
    out = re.sub(r"'+", "'", out)
    # Si el texto entero está envuelto en "" o '' se quitan
    out = re.sub(r'^\s*"(.*)"\s*$', r"\1", out)
    out = re.sub(r"^\s*'(.*)'\s*$", r"\1", out)
    # Colapsa espacios
    out = re.sub(r"\s+", " ", out).strip()
    out = out.replace('"', '').replace("'", '')
    return out

def titlecase_es(s):
    s = normalize_basic(s)
    if not s: return s
    out = []
    for i, tk in enumerate(s.split()):
        upp, low = tk.upper(), tk.lower()
        if upp in ACRONYMS: out.append(upp); continue
        if re.fullmatch(r"(?:[IVXLCDM]+|\d+)\.?$", tk, flags=re.I): out.append(tk.upper()); continue
        out.append(low if i>0 and low in MINOR_WORDS_ES else low[:1].upper()+low[1:])
    return " ".join(out)
