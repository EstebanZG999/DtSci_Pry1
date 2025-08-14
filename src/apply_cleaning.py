"""
Aplicación de limpieza variable por variable (Paso 4).
- Mantiene columnas originales.
- Crea columnas *_nota, *_norm, *_canon y telefonos_list/telefono_norm.
- Usa helpers puros de cleaning/* (misma lógica que el notebook).
Ejemplo:
    python -m src.apply_cleaning \
      --in data/provisional/establecimientos_diversificado_raw_concat.csv \
      --out data/processed/establecimientos_diversificado_clean.csv
"""
import argparse
import sys
from pathlib import Path
import pandas as pd

from cleaning.text_utils import to_upper, titlecase_es, normalize_quotes, split_parentheses
from cleaning.abbrev import standardize_address_abbrev
from cleaning.phones_gt import parse_phones, primary_phone
from cleaning.validators import is_valid_codigo, is_valid_distrito
from cleaning.canonical import canonical_key

COLS_EXPECTED = [
    "codigo","distrito","departamento","municipio","establecimiento",
    "direccion","telefono","supervisor","director","nivel","sector",
    "area","status","modalidad","jornada","plan","departamental","departamento_origen"
]

def add_if_absent(df: pd.DataFrame, col: str):
    if col not in df.columns:
        df[col] = ""

def read_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", required=True, help="Ruta al master crudo concatenado (CSV/Parquet).")
    ap.add_argument("--out", dest="out_path", required=True, help="Ruta de salida del CSV limpio.")
    args = ap.parse_args()

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = read_any(in_path).astype(str)

    # Garantizar columnas requeridas
    for c in COLS_EXPECTED:
        add_if_absent(df, c)

    # Códigos y distrito
    df["codigo_norm"] = df["codigo"].str.strip()
    df["codigo_flag_valido"] = df["codigo_norm"].apply(is_valid_codigo)

    df["distrito_norm"] = df["distrito"].str.strip()
    df["distrito_flag_valido"] = df["distrito_norm"].apply(is_valid_distrito)

    # Geografía
    df["departamento_norm"] = df["departamento"].apply(to_upper)
    df["municipio_norm"]    = df["municipio"].apply(to_upper)

    # Establecimiento: comillas -> titlecase -> paréntesis (nota) -> canónica
    est_with_paren = df["establecimiento"].apply(lambda s: titlecase_es(normalize_quotes(s)))
    est_base, est_nota = zip(*est_with_paren.apply(split_parentheses))
    df["establecimiento_norm"] = list(est_base)
    df["establecimiento_nota"] = list(est_nota)
    df["establecimiento_canon"] = df["establecimiento_norm"].apply(canonical_key)

    # Dirección: comillas -> abreviaturas -> paréntesis (nota) -> canónica
    dir_with_paren = df["direccion"].apply(lambda s: standardize_address_abbrev(normalize_quotes(s)))
    dir_base, dir_nota = zip(*dir_with_paren.apply(split_parentheses))
    df["direccion_norm"] = list(dir_base)
    df["direccion_nota"] = list(dir_nota)
    df["direccion_canon"] = df["direccion_norm"].apply(canonical_key)

    # Teléfonos
    df["telefonos_list"] = df["telefono"].apply(parse_phones)
    df["telefono_norm"]  = df["telefonos_list"].apply(primary_phone)

    # Personas
    df["supervisor_norm"] = df["supervisor"].apply(lambda s: titlecase_es(normalize_quotes(s)))
    df["director_norm"]   = df["director"].apply(lambda s: titlecase_es(normalize_quotes(s)))

    # Otras categorías
    for c in ["nivel","sector","area","status","modalidad","jornada","plan","departamental","departamento_origen"]:
        df[f"{c}_norm"] = df[c].apply(to_upper)

    # Llave canónica final (base sin paréntesis)
    df["id_establecimiento_canon"] = df.apply(
        lambda r: canonical_key(r["establecimiento_norm"], r["direccion_norm"], r["municipio_norm"]),
        axis=1
    )

    # Orden de columnas: originales -> *_nota -> *_norm -> *_canon -> listas/flags
    orig  = [c for c in COLS_EXPECTED if c in df.columns]
    notas = [c for c in df.columns if c.endswith("_nota")]
    norms = [c for c in df.columns if c.endswith("_norm")]
    canon = [c for c in df.columns if c.endswith("_canon")]
    aux   = [c for c in df.columns if c.endswith("_list") or c.endswith("_flag_valido")]

    seen, ordered = set(), []
    for group in [orig, notas, norms, canon, aux]:
        for c in group:
            if c not in seen:
                seen.add(c); ordered.append(c)
    for c in df.columns: 
        if c not in seen:
            ordered.append(c)

    df = df[ordered]

    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"[OK] Guardado: {out_path}  (filas={len(df)}, cols={len(df.columns)})")

if __name__ == "__main__":
    sys.exit(main())
