"""
Estandarización de abreviaturas comunes en direcciones de Guatemala.
Reglas bidireccionales simples, con límites de palabra.
"""
import re
from .text_utils import normalize_basic, to_upper

# Define tu estándar:
ABBREV_MAP = {
    r"\bAV[.]?\b": "AVENIDA",
    r"\bAVDA[.]?\b": "AVENIDA",
    r"\bAVEN[.]?\b": "AVENIDA",
    r"\bCL[.]?\b": "CALLE",
    r"\bCALZ[.]?\b": "CALZADA",
    r"\bCARR[.]?\b": "CARRETERA",
    r"\bDIAG[.]?\b": "DIAGONAL",
    r"\bBLVD[.]?\b": "BULEVAR",
    r"\bBLVR[.]?\b": "BULEVAR",
    r"\bBV[.]?\b":   "BULEVAR",
    r"\bRES[.]?\b": "RESIDENCIAL",
    r"\bZ[.]?\b":   "ZONA",
    r"\bKM[.]?\b":  "KM",
    r"\bNO[.]?\b":  "NO",
    r"\bNRO[.]?\b": "NO",
}

def standardize_address_abbrev(s: str) -> str:
    s = to_upper(normalize_basic(s))
    for pat, repl in ABBREV_MAP.items():
        s = re.sub(pat, repl, s, flags=re.IGNORECASE)
    # Espacios consistentes alrededor de guiones y comas
    s = re.sub(r"\s*-\s*", " - ", s)
    s = re.sub(r"\s*,\s*", ", ", s)
    # Quitar punto residual después de tokens ya expandidos
    s = re.sub(r"\b(AVENIDA|CALLE|CALZADA|CARRETERA|DIAGONAL|BULEVAR|BOULEVARD)\.(?=\s|$|[\d-])", r"\1", s)

    return " ".join(s.split())

