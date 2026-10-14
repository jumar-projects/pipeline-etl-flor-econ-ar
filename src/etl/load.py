"""
Etapa de carga (Load) del pipeline ETL.
Valida los datos transformados y, solo si pasan todos los chequeos, exporta el
CSV analítico final del pipeline.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any

from src.config import PROCESSED_DATA_PATH
from src.etl.validate import validate_pipeline_data


def load_vab_data(
    raw_data: Dict[str, Any],
    df_prov: pd.DataFrame,
    df_tidy: pd.DataFrame,
    output_path: Path = PROCESSED_DATA_PATH,
) -> Path:
    """
    Ejecuta el protocolo de validación y escribe el dataset en formato largo
    (24 provincias x 8 sectores). Devuelve la ruta del CSV generado.
    """
    validate_pipeline_data(raw_data, df_prov, df_tidy)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_tidy.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[ETL - Load] Dataset analítico guardado en: {output_path}")
    return output_path
