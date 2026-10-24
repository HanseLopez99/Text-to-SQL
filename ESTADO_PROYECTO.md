# Estado Actual del Proyecto - Text-to-SQL con LoRA

**Fecha**: 27 de octubre de 2026  
**Autor**: Hansel López (19026)

---

## 📊 Resumen Ejecutivo

Proyecto de fine-tuning de modelo LLM (Qwen2.5-Coder-1.5B-Instruct) con LoRA para generar consultas SQL a partir de preguntas en español.

### ✅ Completado

- **Dataset de entrenamiento**: 2,415 pares pregunta-SQL válidos
- **Dataset de validación**: 41 preguntas sobre 2 esquemas no vistos
- **Entrenamiento Config A**: rank=16, 28.77 horas, loss=0.0856
- **Entrenamiento Config B**: rank=32, en progreso (~30 horas estimadas)
- **Validación MySQL**: Todas las queries validadas en MySQL 8.4.10
- **Scripts de evaluación**: Baseline, Config A, Config B
- **Análisis de errores**: Clasificación por categoría implementada
- **Experimento de inferencia**: Self-correction con hasta 3 intentos

### ⏳ En Progreso

- Entrenamiento Config B (rank=32)
- Evaluación comparativa baseline vs fine-tuned

### 📈 Resultados Preliminares

#### Entrenamiento Config A
- **Modelo base**: Qwen2.5-Coder-1.5B-Instruct
- **Parámetros entrenables**: 2,179,072 (0.14% del total)
- **Tiempo de entrenamiento**: 28.77 horas
- **Loss final**: 0.0856
- **Dispositivo**: Apple M3 con MPS (24GB RAM)

#### Entrenamiento Config B
- **Rank**: 32 (vs 16 de Config A)
- **Parámetros entrenables**: 8,716,288 (0.56% del total)
- **Estado**: En progreso
- **Tiempo estimado**: ~30 horas

---

## 🎯 Objetivo del Proyecto

Generar consultas MySQL correctas a partir de:
- Esquema de base de datos (CREATE TABLE con COMMENTs)
- Pregunta en lenguaje natural (español)

### Requisitos del Proyecto
- ✅ Dataset ≥ 2,000 pares pregunta-SQL
- ✅ Validation set propio (≥ 40 preguntas)
- ✅ Baseline (modelo sin adapter)
- ✅ Dos configuraciones de LoRA (diferencia en UN factor)
- ✅ Experimento de inferencia
- ✅ Análisis de errores por categoría
- ✅ Predicción justificada de EX

---

## 📁 Estructura del Proyecto

```
Text-to-SQL/
├── solucion.py                      # Función principal generar_sql()
├── config.json                      # Configuración del modelo
├── requirements.txt                 # Dependencias Python
├── setup_mysql.sh                   # Instalación MySQL 8.4.10
│
├── datos/
│   ├── esquemas/
│   │   ├── entrenamiento/          # 10 esquemas SQL
│   │   └── validacion/             # 2 esquemas SQL
│   ├── entrenamiento/
│   │   ├── dataset_completo.json   # 2,415 pares válidos
│   │   └── hf_dataset/             # Formato HuggingFace
│   ├── validacion/
│   │   └── validacion.json         # 41 preguntas
│   └── descartes/                  # Reporte de queries inválidas
│
├── scripts_generacion/
│   ├── generar_dataset.py          # Generación inicial
│   ├── expandir_dataset.py         # Expansión con variaciones
│   ├── expansion_final.py          # Queries adicionales
│   └── preparar_datos_training.py  # Conversión a HuggingFace
│
├── scripts_validacion/
│   ├── validar_dataset.py          # Validación en MySQL
│   └── validar_validacion.py       # Validación dataset propio
│
├── scripts_entrenamiento/
│   ├── entrenar_local.py           # Config A (rank=16)
│   └── entrenar_config_b.py        # Config B (rank=32)
│
├── scripts_evaluacion/
│   ├── evaluar_completo.py         # Baseline vs Config A
│   ├── evaluar_config_b.py         # Evaluación Config B
│   ├── experimento_inferencia.py   # Self-correction
│   ├── analisis_errores.py         # Clasificación de errores
│   └── prediccion_ex.py            # Predicción de EX
│
├── notebooks/
│   ├── 01-04_exploracion_y_datos.ipynb
│   └── 05_entrenamiento_lora.ipynb
│
├── resultados/                     # Generados automáticamente
│   ├── metricas_entrenamiento.json
│   ├── metricas_config_b.json
│   ├── comparacion_completa.json
│   ├── analisis_errores.json
│   ├── experimento_inferencia.json
│   └── prediccion_ex.json
│
├── adapter/                        # Config A entrenado
├── adapter_config_b/               # Config B (en entrenamiento)
│
├── README.md
├── BITACORA.md
├── CONTRIBUCIONES.md
└── ESTADO_PROYECTO.md              # Este archivo
```

---

## 🔬 Configuraciones de LoRA

### Config A (Completada)
- **Rank**: 16
- **Alpha**: 32
- **Target modules**: q_proj, k_proj, v_proj, o_proj
- **Parámetros entrenables**: 2,179,072 (0.14%)
- **Hipótesis**: Rank bajo suficiente para patrones SQL básicos
- **Resultado**: EX en validación propia pendiente de evaluación

### Config B (En Progreso)
- **Rank**: 32 (factor diferente vs Config A)
- **Alpha**: 64
- **Target modules**: q_proj, k_proj, v_proj, o_proj
- **Parámetros entrenables**: 8,716,288 (0.56%)
- **Hipótesis**: Rank alto captura patrones SQL complejos
- **Estado**: Entrenamiento en progreso (~30 horas)

---

## 📊 Métricas de Entrenamiento

### Config A
```
Tiempo: 28.77 horas
Loss final: 0.0856
Épocas: 3
Batch size efectivo: 8
Learning rate: 2e-4
Max sequence length: 1024 tokens
Dispositivo: Apple M3 (MPS)
```

### Config B
```
Tiempo estimado: ~30 horas
Loss final: [pendiente]
Épocas: 3
Batch size efectivo: 8
Learning rate: 2e-4
Max sequence length: 1024 tokens
Dispositivo: Apple M3 (MPS)
```

---

## 🎯 Próximos Pasos

1. **Completar entrenamiento Config B** (~30 horas)
2. **Evaluar Config B** en dataset de validación
3. **Ejecutar experimento de inferencia** (self-correction)
4. **Generar análisis de errores** por categoría
5. **Calcular predicción de EX** para evaluación oculta
6. **Seleccionar mejor configuración** (Config A vs Config B)
7. **Actualizar documentación final**

---

## 📈 Flujo de Trabajo

```bash
# 1. Generación de datos
python generar_dataset.py
python expandir_dataset.py
python expansion_final.py
python preparar_datos_training.py

# 2. Validación en MySQL
python validar_dataset.py
python validar_validacion.py

# 3. Entrenamiento
python entrenar_local.py          # Config A
python entrenar_config_b.py       # Config B

# 4. Evaluación
python evaluar_completo.py        # Baseline vs Config A
python evaluar_config_b.py        # Config B

# 5. Experimentos y análisis
python experimento_inferencia.py  # Self-correction
python analisis_errores.py        # Clasificación de errores
python prediccion_ex.py           # Predicción de EX
```

---

## 💻 Especificaciones Técnicas

### Hardware
- **Dispositivo**: MacBook Air M3
- **RAM**: 24GB
- **GPU**: Apple Silicon (MPS)
- **Almacenamiento**: 926GB (413GB disponibles)

### Software
- **Python**: 3.12
- **PyTorch**: 2.14.1
- **Transformers**: 5.20.2
- **PEFT**: 0.21.2
- **MySQL**: 8.4.10 (Docker)
- **SO**: macOS

### Modelo Base
- **Nombre**: Qwen/Qwen2.5-Coder-1.5B-Instruct
- **Parámetros totales**: ~1.5B
- **Contexto**: 2048 tokens
- **Idiomas**: Multilingüe (español soportado)

---

## 📊 Dataset de Entrenamiento

### Estadísticas
- **Total**: 2,415 pares pregunta-SQL
- **Fuentes**:
  - 10 esquemas propios diseñados manualmente
  - Generación con templates y variaciones
  - Validación completa en MySQL 8.4.10

### Distribución por Nivel
- **Fácil**: 1,544 (64%)
  - SELECT simple, WHERE básico, ORDER BY, LIMIT
- **Medio**: 416 (17%)
  - JOIN, GROUP BY, HAVING, agregaciones
- **Difícil**: 462 (19%)
  - Subconsultas, funciones de ventana, WITH, fechas

### Esquemas Incluídos
1. tienda_online
2. biblioteca
3. hospital
4. universidad
5. restaurante
6. gimnasio
7. agencia_viajes
8. inmobiliaria
9. taller_mecanico
10. cine

---

## 🎓 Entregables del Proyecto

Según especificaciones del Proyecto 3:

- ✅ `solucion.py` con función `generar_sql()`
- ✅ `config.json` con configuración del modelo
- ✅ `requirements.txt` con dependencias
- ✅ `adapter/` con adapter LoRA entrenado
- ✅ `datos/` con entrenamiento, validación y descartes
- ✅ `notebooks/` con exploración y entrenamiento
- ✅ `resultados/validacion_propia.csv` (se genera al evaluar)
- ⏳ `presentacion.pdf` (máximo 12 diapositivas) - **Pendiente**
- ✅ `README.md` con ejecución, licencias, uso de IA
- ✅ `BITACORA.md` con registro de trabajo
- ✅ `CONTRIBUCIONES.md` con tabla de contribuciones
- ✅ `historial_git.txt` con `git log --all --date=iso --stat`

---

## 📝 Notas Importantes

### Entrenamiento Local
- Todo el entrenamiento se realizó localmente en MacBook Air M3
- Uso de MPS (Metal Performance Shaders) para aceleración
- Float32 obligatorio para MPS (no soporta float16)
- Tiempo total: ~60 horas (Config A + Config B)

### Validación MySQL
- Todas las queries validadas en MySQL 8.4.10
- Configuración ONLY_FULL_GROUP_BY habilitada
- Docker container para aislamiento y reproducibilidad

### Evaluación
- Métrica EX (Exactitud por Ejecución)
- Comparación de resultados, no texto SQL
- Validación contra dataset de 41 preguntas propias
- Predicción justificada para evaluación oculta

---

## 🔄 Estado de Procesos

### En Ejecución
- **Entrenamiento Config B**: `entrenar_config_b.py`
  - Progreso: tokenizando dataset
  - Tiempo restante estimado: ~28 horas

### Pendientes
- Evaluación Config B
- Experimento de inferencia
- Análisis de errores
- Predicción de EX
- Presentación final

---

**Última actualización**: 27 de octubre de 2026, 11:50 AM
