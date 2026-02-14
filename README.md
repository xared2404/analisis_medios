# Análisis de Agenda Mediática México–Estados Unidos  
## Infraestructura cuantitativa para el estudio de convergencia, polarización y alcance temático

---

## 1. ¿Qué es este proyecto?

Este repositorio construye una infraestructura reproducible para analizar la **agenda temática de medios de comunicación mexicanos y estadounidenses** a partir de millones de menciones de entidades en artículos periodísticos.

El proyecto mide:

- Similitud entre medios (coseno)
- Formación de bloques (México vs EE.UU.)
- Alcance nacional vs internacional
- Concentración temática (HHI)
- Distancia respecto a promedios globales y por país
- Seguimiento específico de temas estratégicos (ej. T-MEC / USMCA)
- Intensidad emocional asociada a temas

Todo el pipeline está diseñado para producir **dataframes listos para BI (Looker Studio)** sin perder trazabilidad metodológica.

---

## 2. Pregunta central

¿Cómo se estructuran, alinean o divergen las agendas mediáticas entre México y Estados Unidos en el tiempo?

Subpreguntas:

- ¿Existe convergencia temática transnacional?
- ¿Se forman bloques mediáticos?
- ¿Qué tan concentrada está la agenda?
- ¿Predomina lo nacional o lo internacional?
- ¿Qué ocurre cuando analizamos un tema estratégico como el T-MEC?

---

## 3. Unidad de análisis

Nivel principal:  
**(month, Medio, entity_canon)**

Derivaciones:

- Share dentro del medio-mes
- Matrices medio × entidad
- Similitud coseno
- Distancias estructurales
- Métricas de concentración

---

## 4. Estructura metodológica

### Stage 1 — Extracción léxica
Tokenización y normalización de entidades (entity_canon).

### Stage 2 — Conteos
Construcción de matrices de menciones:
- mentions_counts_by_medio
- agenda_counts_stage2_mentions

### Stage 3 — Canonical agenda
Conteos agregados por entidad canónica:
- agenda_counts_stage3
- agenda_counts_stage3_monthly

---

## 5. Capa BI (Looker-ready)

Tablas principales en `data/bi/`:

- agenda_counts_stage3_monthly
- agenda_share_stage3_monthly
- agenda_counts_stage3_top500_monthly
- agenda_share_stage3_top500_monthly
- hhi_stage3_monthly
- hhi_stage3_top500_monthly
- distance_stage3_monthly
- distance_stage3_top500_monthly
- bloc_distance_stage3_top500_monthly
- scope_stage3_top500_monthly
- t_mec_share_stage3_top500_monthly
- t_mec_emotion_stage3_top500_monthly
- t_mec_distance_stage3_top500_monthly
- month_completeness
- media_metadata

Todas las tablas cumplen:

- month formato YYYY-MM
- claves únicas verificadas
- valores en rangos válidos
- duplicados eliminados
- sanity checks implementados

---

## 6. Métricas implementadas

### 6.1 Similitud coseno
Medida de alineación entre agendas de medios.

Rango: 0 a 1  
1 = agendas idénticas

---

### 6.2 HHI (Herfindahl-Hirschman Index)
Mide concentración temática.

HHI alto → agenda concentrada  
HHI bajo → agenda diversificada

---

### 6.3 Distancias estructurales

- Distancia a promedio global
- Distancia a promedio MX
- Distancia a promedio US

Permite detectar divergencia sistémica.

---

### 6.4 Bloques MX–US

Se calcula:

- Similaridad MX–MX
- Similaridad US–US
- Similaridad MX–US

Si MX–MX y US–US >> MX–US → polarización transnacional.

---

### 6.5 Scope nacional vs internacional

Clasificación basada en top500 entidades.

Produce:

- share_national
- share_international

share_national + share_international ≈ 1

---

### 6.6 Seguimiento temático (ej. T-MEC)

Se mide:

- Share del tema
- Intensidad emocional promedio
- Distancia estructural MX–US específica del tema

---

## 7. Control de calidad

Scripts implementados:

- bi_sanity_check.py
- bi_range_check.py
- bi_month_format_check.py
- fix_stage3_monthly_duplicates.py

Verificaciones:

- Duplicados
- Rango de valores
- Nulls
- Formato temporal
- Integridad de claves

---

## 8. Marco conceptual

Este proyecto se inscribe en:

- Ciencia de Frontera
- Análisis computacional de discurso
- Polarización mediática
- Agenda-setting cuantitativo
- Sistemas complejos
- Infraestructura pública de datos

Se diseñó para ser compatible con enfoques PRONACES y estudios de democracia digital.

---

## 9. Reproducibilidad

Entorno:

- Python 3.11
- pandas
- numpy
- scikit-learn
- networkx
- python-louvain

Instalación:  python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt                                                                                                                                 ---

## 10. Estado actual

✔ Pipeline mensual estable  
✔ Duplicados corregidos  
✔ Tablas BI optimizadas  
✔ Tema T-MEC integrado  
✔ Metadata MX–US validada  
✔ Listo para implementación en Looker Studio  

---

## 11. Próximos pasos

- Dashboard Looker Studio (D principal + C apoyo)
- Visualización de convergencia mensual
- Análisis de rupturas estructurales
- Publicación académica

---

## 12. Licencia y uso

Este repositorio forma parte de un proyecto académico de investigación.  
El uso de datos debe respetar principios éticos y normativos.

---

Autor:  
Carlos Jared Guerra Rojas  
Proyecto de análisis de agenda mediática México–Estados Unidos  
2026

