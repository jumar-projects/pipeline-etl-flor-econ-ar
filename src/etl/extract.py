"""
Módulo de extracción de datos del archivo Excel Jurisdiccion_52sectores.xlsx.
Extrae los valores correspondientes al año 2024 (columna '2024 (2)').
"""

import openpyxl
from typing import Dict, Any, List
from src.config import RAW_DATA_PATH, REGIONES

def get_year_col_index(sheet, year: int) -> int:
    """
    Localiza dinámicamente la columna de un año en la fila 6 de cabecera.
    Acepta encabezados numéricos (2004) o con nota al pie ('2024 (2)').
    """
    for col in range(1, sheet.max_column + 1):
        val = sheet.cell(6, col).value
        if val is not None and str(val).split(" ")[0] == str(year):
            return col
    raise ValueError(f"No se encontró la columna de {year} en la hoja {sheet.title}")

def get_2024_col_index(sheet) -> int:
    return get_year_col_index(sheet, 2024)

def extract_raw_vab_data() -> Dict[str, Any]:
    """
    Extrae la información cruda del año 2024 desde el Excel.
    
    Retorna un diccionario con:
    - 'total_nacional': VAB total nacional 2024 (fila 32 de VABpb)
    - 'no_distribuido': VAB del sector no distribuido (fila 31 de VABpb)
    - 'totales_provinciales_vabpb': {nombre_provincia: vab_2024} extraído de VABpb
    - 'provincias_sectores': {sheet_name: [{'row': r, 'sector_name': str, 'vab_2024': float, ...}, ...]}
    """
    print(f"[ETL - Extract] Abriendo libro Excel: {RAW_DATA_PATH.name}...")
    wb = openpyxl.load_workbook(RAW_DATA_PATH, data_only=True, read_only=True)
    
    # 1. Extracción de totales desde la hoja VABpb
    ws_vabpb = wb["VABpb"]
    col_2024_vabpb = get_2024_col_index(ws_vabpb)
    col_2004_vabpb = get_year_col_index(ws_vabpb, 2004)
    
    totales_provinciales = {}
    totales_provinciales_2004 = {}
    total_nacional_2004 = None
    no_distribuido_2004 = None
    no_distribuido = None
    total_nacional = None
    
    for r in range(7, ws_vabpb.max_row + 1):
        nombre = ws_vabpb.cell(r, 2).value
        val = ws_vabpb.cell(r, col_2024_vabpb).value
        val_2004 = ws_vabpb.cell(r, col_2004_vabpb).value
        if not nombre or val is None:
            continue
        nombre_clean = str(nombre).strip()
        if nombre_clean == "Total":
            total_nacional = float(val)
            total_nacional_2004 = float(val_2004)
        elif nombre_clean == "No distribuido":
            no_distribuido = float(val)
            no_distribuido_2004 = float(val_2004 or 0.0)
        else:
            totales_provinciales[nombre_clean] = float(val)
            totales_provinciales_2004[nombre_clean] = float(val_2004 or 0.0)
            
    print(f"[ETL - Extract] VABpb procesado. Total Nacional: {total_nacional:,.2f} M$")

    # 2. Extracción de las 24 hojas provinciales
    provincias_sectores = {}
    
    # Recorremos todas las provincias definidas en la configuración regional
    all_provinces = []
    for reg_info in REGIONES.values():
        all_provinces.extend(reg_info["provincias"])
        
    for prov in all_provinces:
        sheet_name = prov["sheet"]
        if sheet_name not in wb.sheetnames:
            raise KeyError(f"La hoja '{sheet_name}' no existe en el archivo Excel.")
            
        ws = wb[sheet_name]
        col_2024 = get_2024_col_index(ws)
        col_2004 = get_year_col_index(ws, 2004)
        
        sectores_data = []
        for r in range(7, 59):  # Filas 7 a 58 son las 52 ramas de actividad
            sec_name = ws.cell(r, 2).value
            val = ws.cell(r, col_2024).value or 0.0
            sectores_data.append({
                "row": r,
                "sector_name": str(sec_name).strip() if sec_name else f"Sector_Fila_{r}",
                "vab_2024": float(val),
                "vab_2004": float(ws.cell(r, col_2004).value or 0.0)
            })
            
        vab_total_sheet = ws.cell(59, col_2024).value or 0.0
        vab_total_sheet_2004 = ws.cell(59, col_2004).value or 0.0
        
        provincias_sectores[sheet_name] = {
            "name": prov["name"],
            "code": prov["code"],
            "vab_total_sheet": float(vab_total_sheet),
            "vab_total_sheet_2004": float(vab_total_sheet_2004),
            "sectores": sectores_data
        }
        
    print(f"[ETL - Extract] Extracción completada exitosamente para las {len(provincias_sectores)} jurisdicciones.")
    
    return {
        "total_nacional": total_nacional,
        "no_distribuido": no_distribuido,
        "totales_provinciales_vabpb": totales_provinciales,
        "total_nacional_2004": total_nacional_2004,
        "no_distribuido_2004": no_distribuido_2004,
        "totales_provinciales_vabpb_2004": totales_provinciales_2004,
        "provincias_sectores": provincias_sectores
    }

if __name__ == "__main__":
    data = extract_raw_vab_data()
    print("Muestra extraída:", list(data["provincias_sectores"].keys())[:3])
