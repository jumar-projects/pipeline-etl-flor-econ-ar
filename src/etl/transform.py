"""
Módulo de transformación y agregación analítica de datos del VAB 2024.
Mapea las 52 ramas a los 8 macro-sectores y calcula participaciones relativas.
"""

import csv
import pandas as pd
from typing import Dict, Any, Tuple
from src.config import SECTORES, REGIONES, MAPPING_CSV_PATH
from src.etl.extract import extract_raw_vab_data

def generate_metadata_mapping_csv(raw_data: Dict[str, Any]) -> None:
    """
    Crea un archivo CSV transparente que documenta el mapeo exacto de las 52 ramas
    hacia los 8 macro-sectores para reproducibilidad científica y auditoría.
    """
    sample_sheet = list(raw_data["provincias_sectores"].keys())[0]
    raw_sectors = raw_data["provincias_sectores"][sample_sheet]["sectores"]
    
    # Crear lookup de fila a macro sector
    row_to_macro = {}
    for macro in SECTORES:
        for r in macro["excel_rows"]:
            row_to_macro[r] = {
                "macro_id": macro["id"],
                "macro_name": macro["name"],
                "macro_short": macro["short_name"],
                "macro_color": macro["color"]
            }
            
    with open(MAPPING_CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "excel_row", 
            "original_sector_name", 
            "macro_sector_id", 
            "macro_sector_name", 
            "macro_sector_short", 
            "color"
        ])
        for sec in raw_sectors:
            r = sec["row"]
            macro_info = row_to_macro.get(r, {
                "macro_id": 0, "macro_name": "No asignado", "macro_short": "NA", "macro_color": "#000000"
            })
            writer.writerow([
                r,
                sec["sector_name"],
                macro_info["macro_id"],
                macro_info["macro_name"],
                macro_info["macro_short"],
                macro_info["macro_color"]
            ])
            
    print(f"[ETL - Transform] Metadatos de mapeo guardados en: {MAPPING_CSV_PATH}")

def transform_vab_data(raw_data: Dict[str, Any] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aplica la taxonomía de los 8 sectores, agrega valores y calcula participaciones.
    
    Retorna:
    - df_provincial: Resumen por provincia (VAB total, % nacional, región)
    - df_tidy: Formato largo con detalle (provincia, región, sector, VAB, % sectorial)
    """
    if raw_data is None:
        raw_data = extract_raw_vab_data()
        
    generate_metadata_mapping_csv(raw_data)
    
    total_nacional = raw_data["total_nacional"]
    total_nacional_2004 = raw_data["total_nacional_2004"]
    provincias_raw = raw_data["provincias_sectores"]
    
    # Mapa de hoja a región
    sheet_to_region = {}
    sheet_to_prov_order = {}
    order_idx = 0
    for reg_name, reg_info in REGIONES.items():
        for prov in reg_info["provincias"]:
            sheet_to_region[prov["sheet"]] = reg_name
            sheet_to_prov_order[prov["sheet"]] = order_idx
            order_idx += 1
            
    # Lookup de fila a macro sector id
    row_to_macro_id = {}
    for macro in SECTORES:
        for r in macro["excel_rows"]:
            row_to_macro_id[r] = macro["id"]
            
    macro_id_to_meta = {m["id"]: m for m in SECTORES}
    
    # Construcción de registros
    records_tidy = []
    records_provincial = []
    
    total_provincializado = sum(p["vab_total_sheet"] for p in provincias_raw.values())
    
    for sheet_name, p_data in provincias_raw.items():
        prov_name = p_data["name"]
        prov_code = p_data["code"]
        prov_vab = p_data["vab_total_sheet"]
        region = sheet_to_region.get(sheet_name, "Otra")
        prov_order = sheet_to_prov_order.get(sheet_name, 99)
        
        # Participación provincial en el total nacional
        prov_share_nat_pct = (prov_vab / total_nacional) * 100.0
        prov_share_prov_pct = (prov_vab / total_provincializado) * 100.0
        prov_vab_2004 = p_data["vab_total_sheet_2004"]
        prov_share_nat_pct_2004 = (prov_vab_2004 / total_nacional_2004) * 100.0
        
        records_provincial.append({
            "order_idx": prov_order,
            "sheet_name": sheet_name,
            "province_name": prov_name,
            "province_code": prov_code,
            "region": region,
            "prov_vab_m": prov_vab,
            "prov_share_nat_pct": prov_share_nat_pct,
            "prov_share_provincialized_pct": prov_share_prov_pct,
            "prov_vab_m_2004": prov_vab_2004,
            "prov_share_nat_pct_2004": prov_share_nat_pct_2004
        })
        
        # Acumular por los 8 sectores
        sector_accum = {m["id"]: 0.0 for m in SECTORES}
        sector_accum_2004 = {m["id"]: 0.0 for m in SECTORES}
        for s in p_data["sectores"]:
            m_id = row_to_macro_id.get(s["row"])
            if m_id:
                sector_accum[m_id] += s["vab_2024"]
                sector_accum_2004[m_id] += s["vab_2004"]
                
        # Guardar en tidy
        for m_id, sec_vab in sector_accum.items():
            meta = macro_id_to_meta[m_id]
            sec_share_prov_pct = (sec_vab / prov_vab * 100.0) if prov_vab > 0 else 0.0
            sec_vab_2004 = sector_accum_2004[m_id]
            sec_share_prov_pct_2004 = (sec_vab_2004 / prov_vab_2004 * 100.0) if prov_vab_2004 > 0 else 0.0
            
            records_tidy.append({
                "order_idx": prov_order,
                "province_name": prov_name,
                "province_code": prov_code,
                "region": region,
                "sector_id": m_id,
                "sector_name": meta["name"],
                "sector_short": meta["short_name"],
                "sector_color": meta["color"],
                "sector_vab_m": sec_vab,
                "sector_share_prov_pct": sec_share_prov_pct,
                "prov_share_nat_pct": prov_share_nat_pct,
                "sector_vab_m_2004": sec_vab_2004,
                "sector_share_prov_pct_2004": sec_share_prov_pct_2004,
                "prov_share_nat_pct_2004": prov_share_nat_pct_2004
            })
            
    df_prov = pd.DataFrame(records_provincial).sort_values("order_idx").reset_index(drop=True)
    df_tidy = pd.DataFrame(records_tidy).sort_values(["order_idx", "sector_id"]).reset_index(drop=True)
    
    return df_prov, df_tidy

if __name__ == "__main__":
    df_prov, df_tidy = transform_vab_data()
    print("--- Resumen provincial (primeras 5) ---")
    print(df_prov[["province_name", "region", "prov_vab_m", "prov_share_nat_pct"]].head())
