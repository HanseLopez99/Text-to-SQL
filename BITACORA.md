# Bitácora del Proyecto

## Entrada 1 - Lunes 12 de octubre de 2026
**Autor:** Hansel López  
**Tarea:** Inicio del proyecto y configuración inicial

Se creó la estructura del proyecto, archivos base y configuración. Se definieron los 12 esquemas de bases de datos (10 para entrenamiento, 2 para validación).

**Próximos pasos:**
- Generar dataset de entrenamiento (≥2,000 pares)
- Implementar solución baseline

---

## Entrada 2 - Martes 13 de octubre de 2026
**Autor:** Hansel López  
**Tarea:** Diseño de esquemas de base de datos

Se diseñaron 10 esquemas para entrenamiento cubriendo diferentes dominios:
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

Y 2 esquemas para validación:
11. finanzas_personales
12. logistica

**Próximos pasos:**
- Crear scripts SQL para los esquemas
- Iniciar generación de datos

---

## Entrada 3 - Miércoles 14 de octubre de 2026
**Autor:** Hansel López  
**Tarea:** Implementación de solución baseline

Se implementó `solucion.py` con la función `generar_sql()` usando el modelo base sin adapter. Se configuró el prompt template para el modelo.

**Próximos pasos:**
- Crear dataset de validación propio (40 preguntas)
- Evaluar baseline

---

## Entrada 4 - Jueves 15 de octubre de 2026
**Autor:** Hansel López  
**Tarea:** Generación de dataset de entrenamiento

Se descargaron los datasets Spider y BIRD. Se inició el proceso de conversión a MySQL y traducción al español.

**Próximos pasos:**
- Completar conversión de datasets
- Generar pares adicionales con LLM

---

## Entrada 5 - Viernes 16 de octubre de 2026
**Autor:** Hansel López  
**Tarea:** Generación de pares con LLM

Se generaron aproximadamente 3,000 pares pregunta-SQL usando un LLM sobre los esquemas propios. Se validó que las consultas funcionen en MySQL 8.4.10.

**Próximos pasos:**
- Consolidar dataset final
- Iniciar fine-tuning

---

## Entrada 6 - Sábado 17 de octubre de 2026
**Autor:** Hansel López  
**Tarea:** Primer experimento de fine-tuning (Config A)

Se entrenó el modelo con LoRA Config A (rank=8, alpha=32, target_modules=[q_proj, v_proj]).

**Hipótesis:** rank bajo es suficiente para patrones SQL básicos.

**Resultados preliminares:**
- Tiempo de entrenamiento: ~2 horas en T4
- Loss final: [pendiente]

**Próximos pasos:**
- Entrenar Config B
- Comparar resultados

---

## Entrada 7 - Domingo 18 de octubre de 2026
**Autor:** Hansel López  
**Tarea:** Segundo experimento de fine-tuning (Config B)

Se entrenó el modelo con LoRA Config B (rank=32, alpha=64, target_modules=[q_proj, v_proj, k_proj, o_proj]).

**Hipótesis:** rank alto y más módulos target mejora capacidad para queries complejas.

**Resultados preliminares:**
- Tiempo de entrenamiento: ~3 horas en T4
- Loss final: [pendiente]

**Próximos pasos:**
- Evaluar ambas configs en validación propia
- Analizar resultados

---

## Entrada 8 - Lunes 19 de octubre de 2026
**Autor:** Hansel López  
**Tarea:** Evaluación y análisis de errores

Se evaluaron ambas configuraciones en el dataset de validación. Se realizó análisis de errores por categoría.

**Próximos pasos:**
- Experimento de inferencia
- Finalizar documentación
