"""
Módulo de validación de calidad de datos (Data Quality & Integrity).
Aplica aserciones rigurosas para certificar consistencia contable y estadística.
"""

import unicodedata
import pandas as pd
import numpy as np
from typing import Dict, Any


def _clean_str(s) -> str:
    """Normaliza nombres (minúsculas, sin tildes, espacios ni guiones bajos) para el cruce exacto."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(s).lower()) if unicodedata.category(c) != 'Mn'
    ).replace(' ', '').replace('_', '')


def _cross_check_vabpb(df_prov: pd.DataFrame, vabpb_dict: Dict[str, float], vab_col: str) -> int:
    """
    Compara el VAB de cada hoja provincial con su fila en la matriz VABpb.
    Falla ante cualquier discrepancia y devuelve cuántas provincias se pudieron cruzar.
    """
    vabpb_clean = {_clean_str(k): v for k, v in vabpb_dict.items()}
    n_matched = 0
    for _, row in df_prov.iterrows():
        matched = vabpb_clean.get(_clean_str(row["province_name"]))
        if matched is None:
            matched = vabpb_clean.get(_clean_str(row["sheet_name"]))
        if matched is None:
            continue
        diff = abs(row[vab_col] - matched)
        assert diff < 0.5, (
            f"Fallo: Discrepancia entre hoja {row['sheet_name']} ({row[vab_col]}) y VABpb ({matched}) en {vab_col}"
        )
        n_matched += 1
    return n_matched

def validate_pipeline_data(raw_data: Dict[str, Any], df_prov: pd.DataFrame, df_tidy: pd.DataFrame) -> bool:
    """
    Ejecuta un conjunto integral de pruebas de calidad sobre los datos procesados.
    Lanza AssertionError si alguna prueba no se satisface.
    """
    print("\n" + "="*50)
    print(" [QA] EJECUTANDO PROTOCOLO DE VALIDACIÓN DE DATOS")
    print("="*50)
    
    # 1. Validación de cardinalidad
    num_provs = len(df_prov)
    assert num_provs == 24, f"Fallo: Se esperaban 24 jurisdicciones, se encontraron {num_provs}"
    print(f" ✓ Cardinalidad provincial: 24 jurisdicciones presentes.")
    
    expected_rows_tidy = 24 * 8
    assert len(df_tidy) == expected_rows_tidy, f"Fallo: Se esperaban {expected_rows_tidy} registros en tidy, hay {len(df_tidy)}"
    print(f" ✓ Cardinalidad sectorial: {expected_rows_tidy} registros (24 provincias x 8 sectores).")
    
    # 2. Validación de completitud (sin nulos)
    assert not df_prov.isnull().any().any(), "Fallo: Se detectaron valores nulos en df_prov"
    assert not df_tidy.isnull().any().any(), "Fallo: Se detectaron valores nulos en df_tidy"
    print(f" ✓ Completitud: Cero valores nulos (NaN) detectados.")
    
    # 3. Validación de no negatividad
    assert (df_tidy["sector_vab_m"] >= 0).all(), "Fallo: Existen valores de VAB negativos"
    assert (df_tidy["sector_share_prov_pct"] >= 0).all(), "Fallo: Existen participaciones negativas"
    print(f" ✓ No negatividad: Todos los valores de VAB y participaciones son >= 0.")
    
    # 4. Validación de suma sectorial provincial (debe sumar 100% por provincia)
    sums_by_prov = df_tidy.groupby("province_name")["sector_share_prov_pct"].sum()
    for prov_name, total_pct in sums_by_prov.items():
        assert np.isclose(total_pct, 100.0, atol=0.05), (
            f"Fallo: La suma sectorial de {prov_name} es {total_pct:.4f}%, no 100%"
        )
    print(f" ✓ Cierre sectorial: Las participaciones de los 8 sectores suman exactamente 100% en las 24 provincias.")
    
    # 5. Validación cruzada de totales (Hoja individual vs Hoja VABpb)
    n_matched = _cross_check_vabpb(df_prov, raw_data["totales_provinciales_vabpb"], "prov_vab_m")
    assert n_matched == 24, f"Fallo: solo {n_matched} de 24 provincias se encontraron en la hoja VABpb (2024)"
    print(f" ✓ Consistencia cruzada: Coincidencia contable exacta entre hojas provinciales y la matriz VABpb (24/24).")
    
    # 6. Validación de suma nacional
    tot_nat = raw_data["total_nacional"]
    no_dist = raw_data["no_distribuido"]
    sum_prov_vab = df_prov["prov_vab_m"].sum()
    assert np.isclose(sum_prov_vab + no_dist, tot_nat, atol=1.0), (
        f"Fallo: Suma provincias ({sum_prov_vab}) + No Distribuido ({no_dist}) != Total Nacional ({tot_nat})"
    )
    pct_cobertura = (sum_prov_vab / tot_nat) * 100.0
    print(f" ✓ Balance macroeconómico: Suma provincial ({sum_prov_vab:,.2f} M$) + No distribuido ({no_dist:,.2f} M$) = Total Nacional ({tot_nat:,.2f} M$).")
    print(f"   (Las 24 jurisdicciones explican el {pct_cobertura:.2f}% del producto nacional).")

    # 7. Año base 2004: mismas pruebas aplicadas a las columnas _2004
    # (sostienen los callouts, la banda Buenos Aires + CABA y la comparación de las flores)
    print(" --- Año base 2004 ---")
    assert (df_tidy["sector_vab_m_2004"] >= 0).all(), "Fallo: Existen valores de VAB 2004 negativos"
    assert (df_prov["prov_vab_m_2004"] > 0).all(), "Fallo: Hay provincias sin VAB en 2004"
    print(f" ✓ No negatividad 2004: Todos los valores de VAB 2004 son >= 0 y cada provincia tiene VAB.")

    sums_2004 = df_tidy.groupby("province_name")["sector_share_prov_pct_2004"].sum()
    for prov_name, total_pct in sums_2004.items():
        assert np.isclose(total_pct, 100.0, atol=0.05), (
            f"Fallo: La suma sectorial 2004 de {prov_name} es {total_pct:.4f}%, no 100%"
        )
    print(f" ✓ Cierre sectorial 2004: Los 8 sectores suman 100% en las 24 provincias.")

    n_matched = _cross_check_vabpb(df_prov, raw_data["totales_provinciales_vabpb_2004"], "prov_vab_m_2004")
    assert n_matched == 24, f"Fallo: solo {n_matched} de 24 provincias se encontraron en la hoja VABpb (2004)"
    print(f" ✓ Consistencia cruzada 2004: Hojas provinciales = matriz VABpb (24/24).")

    tot_nat_2004 = raw_data["total_nacional_2004"]
    no_dist_2004 = raw_data["no_distribuido_2004"]
    sum_prov_2004 = df_prov["prov_vab_m_2004"].sum()
    assert np.isclose(sum_prov_2004 + no_dist_2004, tot_nat_2004, atol=1.0), (
        f"Fallo: Suma provincias 2004 ({sum_prov_2004}) + No Distribuido ({no_dist_2004}) != Total Nacional ({tot_nat_2004})"
    )
    print(f" ✓ Balance macroeconómico 2004: Suma provincial ({sum_prov_2004:,.2f} M$) + No distribuido ({no_dist_2004:,.2f} M$) = Total Nacional ({tot_nat_2004:,.2f} M$).")


    print("="*50)
    print(" [QA] TODOS LOS CHEQUEOS DE CALIDAD PASARON CON ÉXITO")
    print("="*50 + "\n")
    return True
