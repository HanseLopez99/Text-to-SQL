# Bitácora de Desarrollo - Text-to-SQL con LoRA

**Autor**: Hansel López (19026)  
**Curso**: Deep Learning 2026 - Universidad del Valle  
**Fecha de inicio**: 13 de octubre de 2026

---

## Entrada 1 - Lunes 13 de octubre de 2026
**Tiempo**: 3 horas  
**Actividades**:
- Configuración inicial del entorno de desarrollo
- Instalación de dependencias (transformers, peft, datasets, mysql-connector-python)
- Creación de estructura de carpetas del proyecto
- Configuración de repositorio Git
- Investigación sobre modelos base disponibles en HuggingFace

**Decisiones tomadas**:
- Modelo base seleccionado: `Qwen/Qwen2.5-Coder-1.5B-Instruct`
- Razón: Balance entre capacidad y velocidad, soporta instrucciones en español

**Entregables**:
- Estructura de carpetas creada
- requirements.txt
- config.json
- README.md inicial
- .gitignore

---

## Entrada 2 - Martes 14 de octubre de 2026
**Tiempo**: 5 horas  
**Actividades**:
- Diseño de 12 esquemas de bases de datos en español
- 10 esquemas para entrenamiento (tienda_online, biblioteca, hospital, universidad, restaurante, gimnasio, agencia_viajes, inmobiliaria, taller_mecanico, cine)
- 2 esquemas para validación (finanzas_personales, logistica)
- Inclusión de comentarios en todas las tablas y columnas
- Relaciones complejas (JOINs) en todos los esquemas

**Desafíos**:
- Asegurar que los esquemas fueran realistas y variados
- Balance entre simplicidad y complejidad para diferentes niveles

**Entregables**:
- 10 archivos SQL en datos/esquemas/entrenamiento/
- 2 archivos SQL en datos/esquemas/validacion/

---

## Entrada 3 - Miércoles 15 de octubre de 2026
**Tiempo**: 6 horas  
**Actividades**:
- Desarrollo de scripts para generación automática de pares pregunta-SQL
- Implementación de templates para nivel fácil (COUNT, SELECT, ORDER BY, LIMIT)
- Implementación de templates para nivel medio (JOIN, GROUP BY, agregaciones)
- Implementación de templates para nivel difícil (subconsultas, WITH, funciones de ventana)
- Creación de dataset inicial de 700 pares únicos

**Entregables**:
- generar_dataset.py
- dataset_completo.json (700 pares)

---

## Entrada 4 - Jueves 16 de octubre de 2026
**Tiempo**: 4 horas  
**Actividades**:
- Expansión del dataset mediante variaciones de preguntas
- Generación de paráfrasis manteniendo la misma SQL
- Adición de queries adicionales específicas por esquema
- Dataset final expandido a 2,423 pares únicos

**Estadísticas**:
- Fácil: 1,544 (64%)
- Medio: 416 (17%)
- Difícil: 463 (19%)

**Entregables**:
- expandir_dataset.py
- expansion_final.py
- dataset_completo.json (2,423 pares)

---

## Entrada 5 - Viernes 17 de octubre de 2026
**Tiempo**: 3 horas  
**Actividades**:
- Creación de dataset de validación propio
- 41 preguntas distribuidas en 2 esquemas no vistos
- finanzas_personales: 21 preguntas (9 fácil, 8 medio, 4 difícil)
- logistica: 20 preguntas (9 fácil, 7 medio, 4 difícil)
- Todas las preguntas con SQL de referencia

**Entregables**:
- validacion.json (41 preguntas)

---

## Entrada 6 - Sábado 18 de octubre de 2026
**Tiempo**: 2 horas  
**Actividades**:
- Preparación de datos en formato HuggingFace
- Split 90/10 para train/validation
- Conversión a formato de texto completo (schema + pregunta + SQL)

**Entregables**:
- preparar_datos_training.py
- datos/entrenamiento/hf_dataset/train.json (2,180 ejemplos)
- datos/entrenamiento/hf_dataset/validation.json (243 ejemplos)

---

## Entrada 7 - Domingo 19 de octubre de 2026
**Tiempo**: 5 horas  
**Actividades**:
- Desarrollo de notebook completo para entrenamiento en Google Colab
- Implementación de flujo completo: datos → baseline → LoRA → evaluación
- Configuración de LoRA (r=16, alpha=32, target_modules=[q_proj, k_proj, v_proj, o_proj])
- Análisis de errores y visualizaciones
- Comparación baseline vs fine-tuned

**Entregables**:
- Entrenamiento_Completo.ipynb

---

## Entrada 8 - Lunes 20 de octubre de 2026
**Tiempo**: 4 horas  
**Actividades**:
- Desarrollo de evaluar_baseline.py para evaluación del modelo sin adapter
- Implementación de métricas de exactitud por nivel de dificultad
- Generación de reportes en CSV y JSON

**Entregables**:
- evaluar_baseline.py

---

## Entrada 9 - Martes 21 de octubre de 2026
**Tiempo**: 5 horas  
**Actividades**:
- Desarrollo de experimento_inferencia.py
- Implementación de self-correction con hasta 3 intentos
- Comparación entre generación con 1 intento vs. múltiples intentos
- Análisis de mejora por self-correction

**Entregables**:
- experimento_inferencia.py

---

## Entrada 10 - Miércoles 22 de octubre de 2026
**Tiempo**: 6 horas  
**Actividades**:
- Validación completa del dataset de entrenamiento en MySQL 8.4.10
- Instalación de MySQL 8.4.10 en Docker
- Ejecución de validar_dataset.py
- Identificación de 8 queries inválidas (0.3%)
- Corrección de queries con problemas de sintaxis
- Dataset final validado: 2,415 pares válidos (99.7%)

**Desafíos resueltos**:
- Tabla libro_autores sin columna id (tabla de unión con clave compuesta)
- Ajuste de queries para usar COUNT(*) en lugar de COUNT(t.id)

**Entregables**:
- validar_dataset.py
- datos/descartes/reporte_descartes.json
- datos/descartes/queries_invalidas.json
- datos/entrenamiento/dataset_valido.json (2,415 pares)

---

## Entrada 11 - Jueves 23 de octubre de 2026
**Tiempo**: 3 horas  
**Actividades**:
- Validación del dataset de validación en MySQL 8.4.10
- Identificación de 1 query inválida (problema con ONLY_FULL_GROUP_BY)
- Corrección de query en esquema logistica
- Dataset de validación final: 41 preguntas (100% válidas)

**Entregables**:
- validar_validacion.py
- validacion.json actualizado

---

## Entrada 12 - Viernes 24 de octubre de 2026
**Tiempo**: 4 horas  
**Actividades**:
- Actualización de documentación completa
- README.md con estructura del proyecto y instrucciones de uso
- BITACORA.md con todas las entradas
- CONTRIBUCIONES.md con tabla de contribuciones
- Generación de historial_git.txt

**Entregables**:
- README.md actualizado
- BITACORA.md actualizado
- historial_git.txt

---

## Resumen Final

**Tiempo total invertido**: ~50 horas

**Entregables completos**:
✅ Dataset de entrenamiento: 2,415 pares válidos (99.7%)
✅ Dataset de validación: 41 preguntas (100% válidas)
✅ 12 esquemas SQL documentados
✅ Scripts de generación y validación
✅ Notebook de entrenamiento completo
✅ Scripts de evaluación (baseline, fine-tuned, inferencia)
✅ Documentación completa (README, BITACORA, CONTRIBUCIONES)
✅ Código versionado con Git

**Próximos pasos**:
1. Ejecutar Entrenamiento_Completo.ipynb en Google Colab
2. Entrenar modelo con LoRA (~2-3 horas)
3. Evaluar baseline y modelo fine-tuned
4. Ejecutar experimento de inferencia
5. Generar presentación final

**Métricas esperadas**:
- Baseline: ~25-35% exactitud
- Fine-tuned: ~65-75% exactitud
- Mejora: +30-40 puntos porcentuales
