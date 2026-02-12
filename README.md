# Analisis Medios - Emociones y Entidades

Proyecto de análisis computacional del discurso mediático
con enfoque en:

- Perfil emocional por medio
- Intensidad afectiva
- Ironía
- Hate / Aggression / Targeted
- Entidades nombradas (NER)

## Estructura

data/
  raw/        # Export original desde Mongo
  processed/  # Datasets derivados

src/
  build_dataset.py  # Construcción dataset base
  analysis.py       # Análisis estadístico
  utils.py          # Funciones auxiliares

figures/            # Gráficas generadas

## Flujo

1. Extraer datos desde Mongo
2. Construir dataset limpio
3. Generar dataset largo de entidades
4. Ejecutar análisis estadístico
