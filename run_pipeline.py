"""
Orquestador del pipeline ETL del proyecto VAB Flower Chart (Argentina 2024).
1. Extract: lectura del Excel de CEPAL (52 ramas, 24 jurisdicciones)
2. Transform: agregación a 8 macro-sectores y cálculo de participaciones
3. Load: protocolo de validación contable y exportación del CSV analítico
"""

import sys
import time
from pathlib import Path

# Asegurar importación del paquete src
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.etl.extract import extract_raw_vab_data
from src.etl.transform import transform_vab_data
from src.etl.load import load_vab_data

def run_full_pipeline():
    start_time = time.time()
    print("=" * 65)
    print(" PIPELINE ETL INICIADO: VAB FLOWER CHART (ARGENTINA 2024)")
    print("=" * 65)
    
    # PASO 1: EXTRACCIÓN
    print("\n[Paso 1/3] Extrayendo datos desde Excel...")
    raw_data = extract_raw_vab_data()
    
    # PASO 2: TRANSFORMACIÓN
    print("\n[Paso 2/3] Agregando a 8 macro-sectores y calculando participaciones...")
    df_prov, df_tidy = transform_vab_data(raw_data)
    
    # PASO 3: CARGA (validación + exportación del CSV)
    print("\n[Paso 3/3] Validando y exportando el dataset analítico...")
    csv_path = load_vab_data(raw_data, df_prov, df_tidy)
    
    elapsed = time.time() - start_time
    print("=" * 65)
    print(f" PIPELINE ETL COMPLETADO CON ÉXITO EN {elapsed:.2f} SEGUNDOS")
    print(f" • Datos analíticos: {csv_path}")
    print("=" * 65)

if __name__ == "__main__":
    run_full_pipeline()
