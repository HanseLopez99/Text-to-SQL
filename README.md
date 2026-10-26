# Text-to-SQL con LoRA

## Autor
**Hansel López**  
Carnet: 19026  
Universidad del Valle - Deep Learning 2026

## Descripción
Sistema de Text-to-SQL basado en fine-tuning de LLM con LoRA que genera consultas MySQL a partir de preguntas en español y esquemas de bases de datos.

**Modelo base**: Qwen/Qwen2.5-Coder-1.5B-Instruct  
**Dataset**: 2,415 pares pregunta-SQL válidos (validados en MySQL 8.4.10)  
**Validación**: 41 preguntas sobre 2 esquemas no vistos en entrenamiento

## Estado del Proyecto
✅ **Completado localmente** (al 25 de octubre de 2026, 11:57 PM):
- Dataset de entrenamiento: 2,415 pares válidos
- Dataset de validación: 41 preguntas (100% válidas)
- 12 esquemas SQL (10 entrenamiento + 2 validación)
- Entrenamiento LoRA completado en MacBook Air M3 (24 GB RAM)
- Evaluación baseline y modelo fine-tuned completadas
- EX Score: 0.1806 (baseline) → **0.7222** (LoRA), mejora de **+0.5417**
- 30 de 41 preguntas respondidas correctamente en esquemas no vistos
- Análisis de errores por categoría completado
- Presentación final incluida en formato PowerPoint y PDF
- Documentación y resultados finales completos

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Generar SQL
```python
import json
from solucion import generar_sql

# Cargar configuración
with open('config.json', 'r') as f:
    config = json.load(f)

# Generar SQL
esquema = """
CREATE TABLE clientes (
    id INT PRIMARY KEY,
    nombre VARCHAR(100)
);
"""
pregunta = "¿Cuántos clientes hay registrados?"

sql = generar_sql(esquema, pregunta)
print(sql)
```

### Evaluación Baseline (modelo sin adapter)
```bash
python evaluar_baseline.py
```
Genera:
- `resultados/baseline_results.csv` - Resultados detallados
- `resultados/baseline_report.json` - Reporte con métricas

### Entrenamiento con LoRA
Abrir `Entrenamiento_Completo.ipynb` en Google Colab y ejecutar todas las celdas.

El notebook incluye:
1. Configuración del entorno
2. Preparación de datos
3. Evaluación del baseline
4. Entrenamiento con LoRA (configuración óptima)
5. Evaluación del modelo fine-tuneado
6. Comparación y análisis de errores

### Evaluación del Modelo Fine-Tuneado
```bash
# Evaluar en validación propia
python evaluar.py

# Ver resultados
cat resultados/validacion_propia.csv
```

### Experimento de Inferencia (Self-Correction)
```bash
python experimento_inferencia.py
```
Compara generación con 1 intento vs. hasta 3 intentos con corrección basada en errores de MySQL.

Genera:
- `resultados/inferencia_sin_correccion.csv`
- `resultados/inferencia_con_correccion.csv`
- `resultados/experimento_inferencia.json`

## Scripts de Generación y Validación

### Generación de Dataset
```bash
# Generación inicial con templates
python generar_dataset.py

# Expansión con variaciones
python expandir_dataset.py

# Expansión final
python expansion_final.py
```

### Validación con MySQL
```bash
# Validar dataset de entrenamiento
python validar_dataset.py

# Validar dataset de validación
python validar_validacion.py
```

## Licencia
Uso académico - Proyecto de curso Deep Learning 2026

## Uso de IA
- **Modelo base**: Qwen/Qwen2.5-Coder-1.5B-Instruct (Hugging Face)
- **Generación de datos**: Templates + variaciones automáticas
- **Fine-tuning**: LoRA (Low-Rank Adaptation) con PEFT
- **Validación**: Todas las queries validadas en MySQL 8.4.10

## Estructura del Proyecto

```
Text-to-SQL/
├── solucion.py                    # Función principal generar_sql()
├── config.json                    # Configuración del modelo
├── requirements.txt               # Dependencias Python
├── setup_mysql.sh                 # Script de instalación MySQL
│
├── evaluar.py                     # Evaluación modelo fine-tuneado
├── evaluar_baseline.py            # Evaluación baseline (sin adapter)
├── experimento_inferencia.py      # Experimento self-correction
│
├── generar_dataset.py             # Generación inicial de datos
├── expandir_dataset.py            # Expansión con variaciones
├── expansion_final.py             # Expansión final
├── preparar_datos_training.py     # Conversión a formato HuggingFace
│
├── validar_dataset.py             # Validación dataset entrenamiento
├── validar_validacion.py          # Validación dataset validación
│
├── Entrenamiento_Completo.ipynb   # Notebook completo para Colab
│
├── adapter/                       # Adapter LoRA entrenado (se genera)
├── datos/
│   ├── esquemas/
│   │   ├── entrenamiento/         # 10 esquemas SQL
│   │   └── validacion/            # 2 esquemas SQL
│   ├── entrenamiento/
│   │   ├── dataset_completo.json  # 2,415 pares válidos
│   │   └── hf_dataset/            # Formato HuggingFace
│   ├── validacion/
│   │   └── validacion.json        # 41 preguntas
│   └── descartes/
│       ├── reporte_descartes.json
│       └── queries_invalidas.json
│
├── notebooks/
│   ├── 01_exploracion_datos.ipynb
│   ├── 02_generacion_datos.ipynb
│   ├── 03_entrenamiento.ipynb
│   └── 04_evaluacion.ipynb
│
├── resultados/                    # Resultados de evaluación (se genera)
│
├── README.md                      # Este archivo
├── BITACORA.md                    # Bitácora de desarrollo
├── CONTRIBUCIONES.md              # Tabla de contribuciones
└── historial_git.txt              # Log de commits
```

## Requisitos Técnicos
- **MySQL**: 8.4.10 (con ONLY_FULL_GROUP_BY habilitado)
- **Python**: 3.10+
- **GPU**: T4 o superior (para entrenamiento)
- **VRAM**: ~16GB mínimo

## Resultados Finales
- **Baseline** (sin adapter): EX Score de **0.1806**
- **Fine-tuned con LoRA**: EX Score de **0.7222**
- **Mejora absoluta**: **+0.5417** puntos de EX Score
- **Exactitud por ejecución**: 30 de 41 preguntas correctas
- **Configuración LoRA**: rank 16, alpha 32; 2,179,072 parámetros entrenables (0.14% del modelo)
- **Tiempo de entrenamiento**: 28.77 horas en MacBook Air M3

## Próximos Pasos
1. Comparar la configuración actual con LoRA rank 32.
2. Ejecutar y documentar el experimento de inferencia con self-correction.
3. Evaluar la generalización con esquemas y datasets más grandes.

