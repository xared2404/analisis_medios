# BI Layer – Analisis de Medios (Stage 3)

## Objetivo

Esta capa BI está diseñada para alimentar dashboards en Looker Studio.
Se enfoca en:

- D) Medir agenda nacional vs internacional
- C) Medir cohesión / distancia entre bloques MX vs US
- Seguimiento temático específico: T-MEC

Los archivos grandes (agenda_counts / agenda_share completos) NO se versionan.
El dashboard debe priorizar las tablas agregadas y compactas.

---

## Convenciones de llaves

Llaves principales:

- month (YYYY-MM)
- Medio
- entity_canon

Metadatos de medios:

- media_metadata.csv
    - Medio
    - country_group (MX / US)

---

## Tablas principales (Looker-ready)

### 1) scope_stage3_top500_monthly.csv
Nivel: month + Medio  
Columnas:
- month
- Medio
- share_national
- share_international

Uso:
Medición de agenda nacional vs internacional.

---

### 2) bloc_distance_stage3_top500_monthly.csv
Nivel: month  
Columnas:
- month
- mx_mx_mean
- us_us_mean
- mx_us_mean
- mx_mx_n
- us_us_n
- mx_us_n

Uso:
Cohesión intra-bloque vs distancia inter-bloque.

---

### 3) hhi_stage3_monthly.csv
Nivel: month + Medio  
Columnas:
- month
- Medio
- hhi
- n_entities

Uso:
Concentración temática.

---

### 4) distance_stage3_monthly.csv
Nivel: month + Medio  
Columnas:
- month
- Medio
- dist_to_global_mean
- dist_to_mx_mean
- dist_to_us_mean

Uso:
Desalineación respecto al promedio global o por bloque.

---

### 5) T-MEC

- t_mec_share_stage3_top500_monthly.csv
- t_mec_emotion_stage3_top500_monthly.csv
- t_mec_distance_stage3_top500_monthly.csv

Uso:
Seguimiento estratégico del tema T-MEC.

---

### 6) month_completeness.csv
Nivel: month  
Columnas:
- month
- unique_days_observed
- is_complete_month

Uso:
Control de calidad temporal.

---

## Notas metodológicas

- Distancias: 1 - cosine similarity.
- HHI: suma de shares^2.
- scope: clasificación nacional/internacional basada en taxonomy.
- Top500 reduce dimensionalidad y ruido.

---

## Importante

NO subir a GitHub:
- agenda_counts_stage3_monthly.csv
- agenda_share_stage3_monthly.csv

Son archivos >100MB.

