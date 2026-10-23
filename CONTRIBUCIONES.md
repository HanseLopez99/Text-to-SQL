# Contribuciones - Text-to-SQL con LoRA

## Información del Proyecto
**Curso**: Deep Learning 2026 - Universidad del Valle  
**Proyecto**: Text-to-SQL con Fine-tuning de LLM usando LoRA  
**Modalidad**: Individual  
**Fecha de entrega**: 25 de octubre de 2026

---

## Contribuyente Único

**Nombre**: Hansel López  
**Carnet**: 19026  
**Email**: hansel.lopez@correounivalle.edu.co  
**Rol**: Desarrollador completo del proyecto

---

## Distribución de Actividades

### 1. Diseño y Configuración (10 horas)
| Actividad | Responsable | Horas | Evidencia |
|-----------|-------------|-------|-----------|
| Configuración del entorno | Hansel López | 3h | requirements.txt, config.json |
| Investigación de modelos | Hansel López | 2h | README.md (sección decisiones) |
| Diseño de estructura | Hansel López | 2h | Estructura de carpetas |
| Configuración de Git | Hansel López | 1h | historial_git.txt |
| Documentación inicial | Hansel López | 2h | README.md inicial |

**Total**: 10 horas  
**Evidencia**: Commit `448a2d7` y `9eff850`

---

### 2. Diseño de Esquemas de Base de Datos (5 horas)
| Actividad | Responsable | Horas | Evidencia |
|-----------|-------------|-------|-----------|
| Diseño de 10 esquemas de entrenamiento | Hansel López | 4h | datos/esquemas/entrenamiento/*.sql |
| Diseño de 2 esquemas de validación | Hansel López | 1h | datos/esquemas/validacion/*.sql |

**Total**: 5 horas  
**Evidencia**: Commit `9eff850`

---

### 3. Generación de Dataset de Entrenamiento (15 horas)
| Actividad | Responsable | Horas | Evidencia |
|-----------|-------------|-------|-----------|
| Desarrollo de templates | Hansel López | 4h | generar_dataset.py |
| Implementación de generación | Hansel López | 3h | generar_dataset.py |
| Expansión con variaciones | Hansel López | 3h | expandir_dataset.py, expansion_final.py |
| Validación manual de queries | Hansel López | 2h | Dataset inicial de 700 pares |
| Expansión a 2,423 pares | Hansel López | 3h | dataset_completo.json |

**Total**: 15 horas  
**Evidencia**: Commits `9eff850` y `6128798`

---

### 4. Dataset de Validación (3 horas)
| Actividad | Responsable | Horas | Evidencia |
|-----------|-------------|-------|-----------|
| Diseño de preguntas (41 total) | Hansel López | 2h | validacion.json |
| Redacción de SQL de referencia | Hansel López | 1h | validacion.json |

**Total**: 3 horas  
**Evidencia**: Commit `6128798`

---

### 5. Preparación de Datos para Entrenamiento (2 horas)
| Actividad | Responsable | Horas | Evidencia |
|-----------|-------------|-------|-----------|
| Conversión a formato HuggingFace | Hansel López | 1h | preparar_datos_training.py |
| Split train/validation (90/10) | Hansel López | 1h | datos/entrenamiento/hf_dataset/ |

**Total**: 2 horas  
**Evidencia**: Commit `b36598f`

---

### 6. Desarrollo de Notebooks y Scripts (12 horas)
| Actividad | Responsable | Horas | Evidencia |
|-----------|-------------|-------|-----------|
| Notebook de entrenamiento completo | Hansel López | 5h | Entrenamiento_Completo.ipynb |
| Script de evaluación baseline | Hansel López | 2h | evaluar_baseline.py |
| Script de evaluación fine-tuned | Hansel López | 2h | evaluar.py |
| Script de experimento de inferencia | Hansel López | 3h | experimento_inferencia.py |

**Total**: 12 horas  
**Evidencia**: Commits `b36598f` y `ec77705`

---

### 7. Validación con MySQL 8.4.10 (5 horas)
| Actividad | Responsable | Horas | Evidencia |
|-----------|-------------|-------|-----------|
| Instalación de MySQL en Docker | Hansel López | 1h | setup_mysql.sh |
| Desarrollo de scripts de validación | Hansel López | 2h | validar_dataset.py, validar_validacion.py |
| Ejecución de validación | Hansel López | 1h | resultados de validación |
| Corrección de queries inválidas | Hansel López | 1h | Dataset final validado |

**Total**: 5 horas  
**Evidencia**: Commit `ec77705`

---

### 8. Documentación Final (3 horas)
| Actividad | Responsable | Horas | Evidencia |
|-----------|-------------|-------|-----------|
| Actualización de README.md | Hansel López | 1h | README.md |
| Redacción de BITACORA.md | Hansel López | 1h | BITACORA.md |
| Generación de historial_git.txt | Hansel López | 0.5h | historial_git.txt |
| Revisión final | Hansel López | 0.5h | Todos los archivos |

**Total**: 3 horas  
**Evidencia**: Commit `eecf57e`

---

## Resumen de Contribución

**Total de horas invertidas**: 55 horas

| Categoría | Horas | Porcentaje |
|-----------|-------|------------|
| Diseño y Configuración | 10h | 18% |
| Diseño de Esquemas | 5h | 9% |
| Generación de Dataset | 15h | 27% |
| Dataset de Validación | 3h | 5% |
| Preparación de Datos | 2h | 4% |
| Notebooks y Scripts | 12h | 22% |
| Validación con MySQL | 5h | 9% |
| Documentación Final | 3h | 6% |
| **TOTAL** | **55h** | **100%** |

---

## Áreas de Responsabilidad

Según los requisitos del proyecto, las áreas de responsabilidad son:

### ✅ Datos (Responsable: Hansel López)
- Diseño de 12 esquemas de base de datos
- Generación de 2,415 pares pregunta-SQL válidos
- Creación de dataset de validación con 41 preguntas
- Validación completa en MySQL 8.4.10

### ✅ Entrenamiento (Responsable: Hansel López)
- Desarrollo de notebook completo para Google Colab
- Configuración de LoRA (r=16, alpha=32)
- Scripts de evaluación (baseline, fine-tuned, inferencia)
- Análisis de errores y comparaciones

### ✅ Validación y Errores (Responsable: Hansel López)
- Implementación de validación con MySQL 8.4.10
- Análisis de queries inválidas
- Experimento de self-correction
- Documentación de resultados

---

## Evidencia de Trabajo

### Commits de Git
```
eecf57e Actualizar historial_git.txt (final)
b36598f Agregar scripts de entrenamiento para Colab
ec77705 Actualizar historial_git.txt
6128798 Corregir nombre de tabla: mecanicos (sin tilde)
2c5fab6 Actualizar historial_git.txt
9eff850 Dataset de entrenamiento generado: 2,419 pares pregunta-SQL
448a2d7 Setup inicial del proyecto Text-to-SQL
```

**Total de commits**: 7  
**Período**: 13-24 de octubre de 2026 (12 días)

### Archivos Generados
- **Scripts Python**: 12 archivos (.py)
- **Notebooks**: 5 archivos (.ipynb)
- **Esquemas SQL**: 12 archivos (.sql)
- **JSON**: 5 archivos (datasets y reportes)
- **Markdown**: 4 archivos (documentación)
- **Total**: 38+ archivos

---

## Declaración de Trabajo Individual

Yo, **Hansel López (carnet 19026)**, declaro que:

1. Este proyecto fue desarrollado de manera **individual**
2. Todo el código fue escrito por mí, con asistencia de IA para generación de templates y validación
3. El modelo base (Qwen/Qwen2.5-Coder-1.5B-Instruct) es de Hugging Face y se usará con fine-tuning LoRA
4. No se utilizó código de otros estudiantes o proyectos
5. Todas las fuentes de datos y modelos están correctamente atribuidas

---

**Fecha**: 24 de octubre de 2026  
**Firma**: Hansel López
