# Text-to-SQL con LoRA

## Autor
**Hansel López**  
Carnet: 19026  
Universidad del Valle - Deep Learning 2026

## Descripción
Sistema de Text-to-SQL basado en fine-tuning de LLM con LoRA que genera consultas MySQL a partir de preguntas en español y esquemas de bases de datos.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

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

## Evaluación

```bash
# Evaluar en validación propia
python evaluar.py

# Ver resultados
cat resultados/validacion_propia.csv
```

## Licencia
Uso académico - Proyecto de curso Deep Learning 2026

## Uso de IA
- Modelo base: Qwen/Qwen2.5-Coder-1.5B-Instruct (Hugging Face)
- Generación de datos: Asistida con LLM para pares pregunta-SQL
- Fine-tuning: LoRA/QLoRA con PEFT

## Estructura del proyecto

```
├── solucion.py              # Función principal generar_sql()
├── config.json              # Configuración del modelo
├── requirements.txt         # Dependencias
├── adapter/                 # Adapter LoRA entrenado
├── datos/
│   ├── entrenamiento/       # ≥2,000 pares pregunta-SQL
│   ├── validacion/          # 2 esquemas, 40 preguntas
│   └── descartes/           # Pares descartados + razones
├── notebooks/
│   ├── 01_exploracion_datos.ipynb
│   ├── 02_generacion_datos.ipynb
│   ├── 03_entrenamiento.ipynb
│   └── 04_evaluacion.ipynb
└── resultados/
    └── validacion_propia.csv
```

## Requisitos técnicos
- MySQL 8.4.10
- Python 3.10+
- GPU para entrenamiento (T4 o superior)
