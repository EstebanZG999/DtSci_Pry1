import pandas as pd
import re
from pathlib import Path

# Configuracion
BASE_DIR = Path(__file__).resolve().parent
PROJ_ROOT = BASE_DIR.parent

INPUT_FILE = PROJ_ROOT / "data" / "provisional" / "establecimientos_diversificado_raw_concat.csv"
OUTPUT_DIR = PROJ_ROOT / "data" / "muestras_problemas"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Comprobación de coherencia
if not INPUT_FILE.exists():
    raise FileNotFoundError(f"No encuentro el CSV en: {INPUT_FILE}")

# Carga
df = pd.read_csv(INPUT_FILE)

# Variables clave
variables = ["codigo", "telefono", "distrito", "direccion", "establecimiento"]

# Diccionario para guardar resumen
resumen_problemas = []

def extraer_muestras(col, patron, descripcion):
    """
    Busca el patrón en la columna, guarda ejemplos y retorna conteo.
    """
    mask = df[col].astype(str).str.contains(patron, na=False, regex=True)
    muestras = df.loc[mask, col].drop_duplicates().head(50)
    
    if not muestras.empty:
        # Guardar CSV por problema detectado
        file_path = OUTPUT_DIR / f"{col}_{descripcion}.csv"
        muestras.to_csv(file_path, index=False, encoding="utf-8")
    
    return mask.sum(), file_path if not muestras.empty else None

# Reglas por variable
for col in variables:
    if col not in df.columns:
        continue
    
    # Lista de problemas y patrones
    reglas = [
        (r"\s{2,}", "doble_espacio"),
        (r"[()]", "parentesis"),
        (r'"+', "comillas_multiples"),
        (r"[^\x00-\x7F]", "caracteres_no_ascii"),
    ]
    
    if col in ["codigo", "telefono"]:
        reglas.append((r"[^0-9-]", "caracteres_no_numericos"))
    
    for patron, desc in reglas:
        conteo, archivo = extraer_muestras(col, patron, desc)
        resumen_problemas.append({
            "columna": col,
            "problema": desc,
            "patron": patron,
            "conteo": conteo,
            "porcentaje": round((conteo / len(df)) * 100, 2),
            "archivo_muestras": archivo.name if archivo else None
        })

# Guardar resumen
resumen_df = pd.DataFrame(resumen_problemas)
resumen_df.to_csv(OUTPUT_DIR / "resumen_problemas.csv", index=False, encoding="utf-8")

print(f"Auditoría completada. Resultados guardados en: {OUTPUT_DIR}")
print(resumen_df)
