"""
Configuración central del proyecto VAB Flower Chart (Argentina 2024).
Define rutas, paletas de colores, taxonomía sectorial y regiones del pipeline ETL.
"""

from pathlib import Path

# --- RUTAS DE DIRECTORIOS ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = BASE_DIR / "Dataset" / "Jurisdiccion_52sectores.xlsx"
METADATA_DIR = DATA_DIR / "metadata"
PROCESSED_DIR = DATA_DIR / "processed"

# Asegurar que existan los directorios
for directory in [METADATA_DIR, PROCESSED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Archivos de salida
MAPPING_CSV_PATH = METADATA_DIR / "mapping_52_to_8.csv"
# CSV final del pipeline (salida de la etapa load)
PROCESSED_DATA_PATH = PROCESSED_DIR / "vab_2024_analitico.csv"

# --- PALETA Y DEFINICIÓN DE LOS 8 MACRO-SECTORES ---
# Paleta validada con simulación de deuteranopía y protanopía
# (distancia CIELAB mínima entre sectores: 23; antes Industria y Transporte quedaban en 6)
# Orden angular: pétalo 0 (Norte, 0°), 1 (45°), ..., 7 (315°)
SECTORES = [
    {
        "id": 1,
        "name": "Agropecuario y Pesca",
        "short_name": "Agro y Pesca",
        "color": "#16A34A",  # Verde
        "excel_rows": [7, 8, 9],
        "description": "Agricultura, ganadería, caza, silvicultura y pesca"
    },
    {
        "id": 2,
        "name": "Minería, Petróleo y Gas",
        "short_name": "Minería y Energía",
        "color": "#7F1D1D",  # Bordó (se distingue del naranja y el frambuesa con daltonismo)
        "excel_rows": [10, 11],
        "description": "Extracción de hidrocarburos, carbón y minerales metalíferos y no metalíferos"
    },
    {
        "id": 3,
        "name": "Industria Manufacturera",
        "short_name": "Industria",
        "color": "#1D4ED8",  # Azul zafiro profundo / Navy
        "excel_rows": list(range(12, 36)),  # Filas 12 a 35 (24 ramas fabriles)
        "description": "Alimentos, bebidas, química, metalmecánica, automotriz, textil, etc."
    },
    {
        "id": 4,
        "name": "Construcción y Serv. Públicos",
        "short_name": "Construcción y Serv.",
        "color": "#C2410C",  # Terracota
        "excel_rows": [36, 37, 38, 39],
        "description": "Electricidad, gas por redes, agua y construcción"
    },
    {
        "id": 5,
        "name": "Comercio, Hoteles y Rest.",
        "short_name": "Comercio y Turismo",
        "color": "#EAB308",  # Amarillo oro (contraste suficiente con el fondo papel)
        "excel_rows": [40, 41, 42],
        "description": "Comercio mayorista y minorista, hotelería y gastronomía"
    },
    {
        "id": 6,
        "name": "Transporte y Comunicaciones",
        "short_name": "Transporte y Com.",
        "color": "#A78BFA",  # Lavanda (clara, para separarse del azul de Industria con daltonismo)
        "excel_rows": [43, 44],
        "description": "Transporte de carga y pasajeros, correos y telecomunicaciones"
    },
    {
        "id": 7,
        "name": "Finanzas e Inmobiliarias",
        "short_name": "Finanzas e Inm.",
        "color": "#2DD4BF",  # Turquesa claro (se separa del azul de Industria)
        "excel_rows": [45, 46, 47, 48, 49],
        "description": "Intermediación financiera, seguros, vivienda y actividades empresariales"
    },
    {
        "id": 8,
        "name": "Serv. Sociales y Adm. Pública",
        "short_name": "Sociales y Pública",
        "color": "#BE185D",  # Frambuesa
        "excel_rows": list(range(50, 59)),  # Filas 50 a 58
        "description": "Adm. pública, defensa, educación, salud y servicios personales/domésticos"
    }
]

# --- REGIONES GEOGRÁFICAS Y JURISDICCIONES ---
# Ordenadas por región geográfica (Opción B) y dentro de cada región por VAB 2024 descendente
REGIONES = {
    "Pampeana": {
        "color": "#1E3A8A",
        "provincias": [
            {"sheet": "Buenos_Aires", "name": "Buenos Aires", "code": "BUE"},
            {"sheet": "Ciudad_de_Buenos_Aires", "name": "Ciudad de Bs. As.", "code": "CABA"},
            {"sheet": "Cordoba", "name": "Córdoba", "code": "CBA"},
            {"sheet": "Santa_Fe", "name": "Santa Fe", "code": "SFE"},
            {"sheet": "Entre_Rios", "name": "Entre Ríos", "code": "ERO"},
            {"sheet": "La_Pampa", "name": "La Pampa", "code": "LPA"},
        ]
    },
    "Cuyo": {
        "color": "#9A3412",
        "provincias": [
            {"sheet": "Mendoza", "name": "Mendoza", "code": "MDZ"},
            {"sheet": "San_Juan", "name": "San Juan", "code": "SJU"},
            {"sheet": "San_Luis", "name": "San Luis", "code": "SLU"},
        ]
    },
    "NOA": {
        "color": "#065F46",
        "provincias": [
            {"sheet": "Tucuman", "name": "Tucumán", "code": "TUC"},
            {"sheet": "Salta", "name": "Salta", "code": "SLA"},
            {"sheet": "Santiago_del_Estero", "name": "Sgo. del Estero", "code": "SGO"},
            {"sheet": "Jujuy", "name": "Jujuy", "code": "JUJ"},
            {"sheet": "Catamarca", "name": "Catamarca", "code": "CAT"},
            {"sheet": "La_Rioja", "name": "La Rioja", "code": "LRJ"},
        ]
    },
    "NEA": {
        "color": "#0F766E",
        "provincias": [
            {"sheet": "Chaco", "name": "Chaco", "code": "CHA"},
            {"sheet": "Misiones", "name": "Misiones", "code": "MIS"},
            {"sheet": "Corrientes", "name": "Corrientes", "code": "CTE"},
            {"sheet": "Formosa", "name": "Formosa", "code": "FOR"},
        ]
    },
    "Patagonia": {
        "color": "#374151",
        "provincias": [
            {"sheet": "Neuquen", "name": "Neuquén", "code": "NQN"},
            {"sheet": "Chubut", "name": "Chubut", "code": "CHU"},
            {"sheet": "Rio_Negro", "name": "Río Negro", "code": "RNG"},
            {"sheet": "Santa_Cruz", "name": "Santa Cruz", "code": "SCR"},
            {"sheet": "Tierra_del_Fuego", "name": "T. del Fuego", "code": "TDF"},
        ]
    }
}
