# La Flor de la Economía Argentina (VAB provincial, 2004–2024)
**Análisis Territorial de la Estructura Productiva y Disparidad Regional**  
*Proyecto para el Concurso «Contar con Datos»*

---

## 1. Resumen

Pipeline ETL en Python que procesa el **Valor Agregado Bruto (VAB) de las 24 jurisdicciones de Argentina** a partir de la serie publicada por la CEPAL, para dos cortes: **2004** (año base) y **2024**.

1. **Extract:** lee el Excel original (52 ramas de actividad por provincia).
2. **Transform:** agrupa las 52 ramas en 8 macro-sectores y calcula la participación de cada sector en la economía provincial y de cada provincia en el VAB nacional.
3. **Load:** valida la consistencia contable de los resultados y exporta un único CSV analítico en formato largo (*tidy*).

**Hallazgo central:** Buenos Aires y CABA generan el **51,7%** del VAB nacional en 2024, prácticamente lo mismo que en 2004 (**52,8%**). En dos décadas la concentración territorial casi no se movió; los cambios ocurrieron en los márgenes: Neuquén creció con Vaca Muerta (3,2% → 4,4% del país) y Catamarca perdió su minería (43% → 10% de su economía).

---

## 2. Taxonomía Sectorial y Metodología Económica

**Fuente:** CEPAL (2022). *Desagregación provincial del valor agregado bruto de la Argentina, base 2004* (LC/TS.2022/196). Documentos de Proyectos, Comisión Económica para América Latina y el Caribe, elaborado en colaboración con el Ministerio de Economía de la Argentina y el Centro de Estudios para la Producción (CEP XXI). Datos abiertos disponibles en [cepal.org/es/publicaciones/47900](https://www.cepal.org/es/publicaciones/47900-desagregacion-provincial-valor-agregado-bruto-la-argentina-base-2004) (anexo Excel `Jurisdiccion_52sectores.xlsx`).

Los valores están a precios básicos, en millones de pesos a **precios constantes de 2004**, con valores preliminares para 2024. Se utilizan dos cortes de la serie: **2004** (año base) y **2024**.

> **Nota sobre precios constantes.** Las participaciones (de cada provincia en el total nacional y de cada sector en la economía provincial) se calculan a precios constantes de 2004, por lo que reflejan cambios en el **volumen** de producción y no en los **precios relativos**. Medidas a precios corrientes, las participaciones de 2024 podrían diferir; por ejemplo, en sectores cuyos precios evolucionaron muy distinto del promedio, como la minería y los hidrocarburos. El dataset publicado solo ofrece la serie a precios constantes, por lo que esa diferencia no se puede cuantificar con esta fuente.

El dataset original desagrega **52 ramas de actividad**. Para facilitar el análisis, se consolidaron en **8 Macro-Sectores** alineados con la Clasificación Industrial Internacional Uniforme (**CIIU Rev. 3.1**):

| # | Macro-Sector | Color (`sector_color`) | Ramas CIIU Originales (Filas Excel) |
|---|:---|:---:|:---|
| **1** | **Agropecuario y Pesca** | `#16A34A` | Fila 7 (Agro y ganadería), Fila 8 (Silvicultura), Fila 9 (Pesca). |
| **2** | **Minería, Petróleo y Gas** | `#7F1D1D` | Fila 10 (Petróleo, gas, carbón), Fila 11 (Minerales y canteras). |
| **3** | **Industria Manufacturera** | `#1D4ED8` | Filas 12 a 35 (24 ramas: alimentos, químicos, automotriz, etc.). |
| **4** | **Construcción y Serv. Públicos** | `#C2410C` | Filas 36-38 (Electricidad, gas, agua) y Fila 39 (Construcción). |
| **5** | **Comercio, Hoteles y Rest.** | `#EAB308` | Fila 40 (Comercio), Filas 41-42 (Hotelería y gastronomía). |
| **6** | **Transporte y Comunicaciones** | `#A78BFA` | Fila 43 (Transporte), Fila 44 (Comunicaciones). |
| **7** | **Finanzas e Inmobiliarias** | `#2DD4BF` | Filas 45-47 (Finanzas, seguros), Filas 48-49 (Inmobiliarias/alquiler). |
| **8** | **Serv. Sociales y Adm. Pública** | `#BE185D` | Fila 50 (Adm. pública), 51-54 (Educación/Salud), 55-58 (Comunitarios/doméstico). |

> El detalle fila por fila se encuentra registrado y versionado en [`data/metadata/mapping_52_to_8.csv`](data/metadata/mapping_52_to_8.csv).

---

## 3. Agrupamiento Territorial

Las 24 jurisdicciones se encuentran agrupadas por **Regiones Geográficas Oficiales** para facilitar el análisis comparativo intra e interregional (columna `region` del CSV):
1. **Región Pampeana (6):** Buenos Aires, Ciudad de Bs. As. (CABA), Córdoba, Santa Fe, Entre Ríos, La Pampa.
2. **Región Cuyo (3):** Mendoza, San Juan, San Luis.
3. **Región NOA (6):** Tucumán, Salta, Santiago del Estero, Jujuy, Catamarca, La Rioja.
4. **Región NEA (4):** Chaco, Misiones, Corrientes, Formosa.
5. **Región Patagonia (5):** Neuquén, Chubut, Río Negro, Santa Cruz, Tierra del Fuego.

---

## 4. Arquitectura del Pipeline ETL

```
├── Dataset/                           # Archivos originales inmutables (Excel y PDF metodológico)
│   ├── Jurisdiccion_52sectores.xlsx
│   └── S2200369_es.pdf
├── data/
│   ├── metadata/
│   │   └── mapping_52_to_8.csv        # Diccionario de equivalencias 52 -> 8 sectores
│   └── processed/
│       └── vab_2024_analitico.csv     # SALIDA: dataset analítico (tidy)
├── src/
│   ├── config.py                      # Taxonomía sectorial, paleta, rutas y regiones
│   └── etl/
│       ├── extract.py                 # Extracción de 2004 y 2024 (columnas localizadas por año)
│       ├── transform.py               # Agregación sectorial y participaciones (2024 y columnas _2004)
│       ├── validate.py                # Protocolo de QA (aserciones contables, balance de sumas = 100%)
│       └── load.py                    # Valida y exporta el CSV analítico
├── requirements.md                    # Versiones de dependencias e instrucciones de instalación
└── run_pipeline.py                    # Orquestador: extract → transform → load
```

### Contrato de salida: `vab_2024_analitico.csv`

Formato largo, 192 filas (24 provincias × 8 sectores), UTF-8, separador coma. Columnas:

| Columna | Descripción |
|---|---|
| `order_idx` | Orden de la provincia (por región y VAB 2024) |
| `province_name`, `province_code`, `region` | Identificación de la jurisdicción |
| `sector_id`, `sector_name`, `sector_short`, `sector_color` | Macro-sector (1 a 8) |
| `sector_vab_m`, `sector_vab_m_2004` | VAB del sector en la provincia (M$ constantes de 2004) |
| `sector_share_prov_pct`, `sector_share_prov_pct_2004` | Peso del sector en la economía provincial (%) |
| `prov_share_nat_pct`, `prov_share_nat_pct_2004` | Peso de la provincia en el VAB nacional (%, repetido por sector) |

---

## 5. Protocolo de Calidad de Datos (QA & Validations)

> Las pruebas 2 a 5 se aplican **a 2024 y a 2004**: así la comparación entre ambos años se apoya en datos verificados con el mismo rigor. La consistencia cruzada exige que las 24 provincias se encuentren en la matriz `VABpb` (si alguna no se encuentra, la prueba falla en lugar de omitirla).

El módulo `src/etl/validate.py` se ejecuta dentro de la etapa **load** (`src/etl/load.py`): el CSV solo se escribe si todas las pruebas pasan.
1. **Cardinalidad:** Certifica la presencia de las 24 jurisdicciones y los 8 sectores ($24 \times 8 = 192$ registros analíticos).
2. **Completitud y No Negatividad:** Cero valores nulos (`NaN`) y valores estrictamente mayores o iguales a cero.
3. **Cierre Sectorial Provincial:** Verifica que $\sum_{s=1}^8 \text{participación sectorial}_{p, s} = 100.0\% \pm 0.01\%$ para cada una de las 24 provincias.
4. **Consistencia Cruzada:** Comprueba que la suma de sectores de cada hoja coincida exactamente con la cifra reportada en la matriz consolidada `VABpb`.
5. **Balance Macroeconómico Nacional:** Valida que la suma de las 24 provincias ($586,860.62$ M\$) más el sector *No Distribuido* ($354.44$ M\$) iguale al Total Nacional ($587,215.05$ M\$). En 2004: $412,133.35$ M\$ + $294.11$ M\$ = $412,427.46$ M\$.

---

## 6. Cómo Reproducir el Pipeline

Requiere Python 3.12. Las versiones de las dependencias están en [`requirements.md`](requirements.md).

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install numpy==2.5.4 openpyxl==3.1.5 pandas==3.0.6
.venv\Scripts\python.exe run_pipeline.py
```

### Salida Generada:
* **Dataset listo para análisis:** [`data/processed/vab_2024_analitico.csv`](data/processed/vab_2024_analitico.csv)
