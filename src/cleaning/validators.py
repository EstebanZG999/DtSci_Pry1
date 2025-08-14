"""
Validadores de formatos específicos para datos de establecimientos.
Reglas:
- Código de establecimiento válido: exactamente 6 dígitos numéricos.
- Código de distrito válido: formato NN-NN (dos dígitos, guion, dos dígitos).
- Expresiones regulares optimizadas para coincidencias exactas.
- Retorna True si cumple el formato, False en caso contrario.
"""

import re
# Acepta código con guiones (2-2-4-2) o, opcionalmente, solo dígitos de 6 a 12 
RE_CODIGO = re.compile(r"^(?:\d{2}-\d{2}-\d{4}-\d{2}|\d{6,12})$")

# Distrito: 1–2 dígitos, guion, 1–3 dígitos 
RE_DISTRITO = re.compile(r"^\d{1,2}-\d{1,3}$")

def is_valid_codigo(s): 
    return bool(s) and bool(RE_CODIGO.fullmatch(str(s).strip()))

def is_valid_distrito(s): 
    return bool(s) and bool(RE_DISTRITO.fullmatch(str(s).strip()))