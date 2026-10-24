"""
Predicción Justificada de EX en Evaluación Oculta
Analiza el rendimiento en validación propia y predice EX en evaluación oculta
"""
import json
import pandas as pd

print("=" * 60)
print("PREDICCIÓN DE EX EN EVALUACIÓN OCULTA")
print("=" * 60)

# Cargar resultados
try:
    with open('resultados/comparacion_completa.json', 'r') as f:
        comparacion = json.load(f)
except:
    print("⚠ Ejecutar primero: python evaluar_completo.py y python evaluar_config_b.py")
    exit()

# Cargar análisis de errores
try:
    with open('resultados/analisis_errores.json', 'r') as f:
        analisis = json.load(f)
except:
    print("⚠ Ejecutar primero: python analisis_errores.py")
    exit()

# Cargar métricas de entrenamiento
with open('resultados/metricas_entrenamiento.json', 'r') as f:
    config_a_metrics = json.load(f)

with open('resultados/metricas_config_b.json', 'r') as f:
    config_b_metrics = json.load(f)

print("\n" + "=" * 60)
print("RESUMEN DE RESULTADOS EN VALIDACIÓN PROPIA")
print("=" * 60)

baseline_ex = comparacion['baseline']['ex_score']
config_a_ex = comparacion['config_a']['ex_score']
config_b_ex = comparacion['config_b']['ex_score']

print(f"\nBaseline (sin adapter): EX = {baseline_ex:.4f}")
print(f"Config A (rank=16):     EX = {config_a_ex:.4f}")
print(f"Config B (rank=32):     EX = {config_b_ex:.4f}")

# Seleccionar mejor configuración
mejor_config = 'A' if config_a_ex >= config_b_ex else 'B'
mejor_ex = max(config_a_ex, config_b_ex)

print(f"\n✓ Mejor configuración: Config {mejor_config} (EX = {mejor_ex:.4f})")

# Análisis por nivel de dificultad
print("\n" + "=" * 60)
print("ANÁLISIS POR NIVEL DE DIFICULTAD")
print("=" * 60)

df = pd.read_csv(f'resultados/config_{mejor_config.lower()}_results.csv')

for nivel in ['facil', 'medio', 'dificil']:
    nivel_df = df[df['nivel'] == nivel]
    if len(nivel_df) > 0:
        correctas = nivel_df['correcta'].sum()
        total = len(nivel_df)
        ex_nivel = (nivel_df[nivel_df['correcta']]['peso'].sum() / 
                    nivel_df['peso'].sum()) if nivel_df['peso'].sum() > 0 else 0
        print(f"{nivel:10s}: {correctas:2d}/{total:2d} correctas (EX = {ex_nivel:.4f})")

# Análisis de errores
print("\n" + "=" * 60)
print("ANÁLISIS DE ERRORES")
print("=" * 60)

distribucion = analisis['distribucion_errores']
total_errores = sum(distribucion.values())

print(f"\nTotal de errores: {total_errores}")
print("\nDistribución por categoría:")
for categoria, count in sorted(distribucion.items(), key=lambda x: x[1], reverse=True):
    porcentaje = (count / total_errores) * 100
    print(f"  {categoria:30s}: {count:3d} ({porcentaje:5.1f}%)")

# Predicción de EX en evaluación oculta
print("\n" + "=" * 60)
print("PREDICCIÓN DE EX EN EVALUACIÓN OCULTA")
print("=" * 60)

# Factores a considerar:
# 1. Rendimiento en validación propia (mejor config)
# 2. Complejidad de la evaluación oculta (30-40 preguntas, 3 niveles)
# 3. Esquemas no vistos (5-10 tablas)
# 4. Tipos de queries (JOIN, GROUP BY, subconsultas, ventanas, fechas)

# Factor de generalización (penalización por esquemas no vistos)
# Basado en literatura: 0.75-0.85 para modelos fine-tuned
factor_generalizacion = 0.80

# Predicción conservadora
ex_predicho_conservador = mejor_ex * factor_generalizacion

# Predicción optimista (asumiendo buena generalización)
factor_optimista = 0.90
ex_predicho_optimista = mejor_ex * factor_optimista

# Predicción más probable
ex_predicho = mejor_ex * 0.85

print(f"\nEX en validación propia: {mejor_ex:.4f}")
print(f"\nFactores considerados:")
print(f"  • Rendimiento en validación propia (41 preguntas)")
print(f"  • Esquemas no vistos en evaluación oculta (5-10 tablas)")
print(f"  • Distribución de niveles: fácil (30%), medio (50%), difícil (20%)")
print(f"  • Complejidad de queries: JOINs, agregaciones, subconsultas, ventanas")
print(f"  • Factor de generalización estimado: 0.80-0.90")

print(f"\n{'='*60}")
print("PREDICCIÓN JUSTIFICADA")
print(f"{'='*60}")
print(f"\nEX predicho en evaluación oculta:")
print(f"  • Escenario conservador: {ex_predicho_conservador:.4f}")
print(f"  • Escenario probable:    {ex_predicho:.4f} ← MEJOR ESTIMACIÓN")
print(f"  • Escenario optimista:   {ex_predicho_optimista:.4f}")

# Justificación detallada
print(f"\n{'='*60}")
print("JUSTIFICACIÓN DETALLADA")
print(f"{'='*60}")

justificacion = f"""
El modelo fue fine-tuned con {config_a_metrics['parametros_entrenables']:,} parámetros 
usando LoRA (rank={comparacion['config_a']['rank']}) sobre Qwen2.5-Coder-1.5B-Instruct.

Dataset de entrenamiento:
  • 2,415 pares pregunta-SQL validados en MySQL 8.4.10
  • 10 esquemas propios con complejidad variable
  • Distribución: 64% fácil, 17% medio, 19% difícil
  • Queries incluyen: SELECT, JOIN, GROUP BY, HAVING, subconsultas, ventanas

Rendimiento en validación propia:
  • EX = {mejor_ex:.4f} sobre 41 preguntas (2 esquemas no vistos)
  • Fácil: {df[df['nivel']=='facil']['correcta'].sum()}/{len(df[df['nivel']=='facil'])} correctas
  • Medio: {df[df['nivel']=='medio']['correcta'].sum()}/{len(df[df['nivel']=='medio'])} correctas
  • Difícil: {df[df['nivel']=='dificil']['correcta'].sum()}/{len(df[df['nivel']=='dificil'])} correctas

Análisis de errores principales:
  • {distribucion.get('columna_tabla_inexistente', 0)} errores de columnas/tablas inexistentes
  • {distribucion.get('join_incorrecto', 0) + distribucion.get('join_faltante', 0)} errores de JOIN
  • {distribucion.get('agregacion_faltante', 0) + distribucion.get('group_by_faltante', 0)} errores de agregación
  • {distribucion.get('subconsulta_faltante', 0)} errores de subconsultas

Predicción para evaluación oculta:
  • Esquemas no vistos: 5-10 tablas (mayor complejidad que validación)
  • 30-40 preguntas con distribución: fácil (30%), medio (50%), difícil (20%)
  • Factor de generalización aplicado: 0.85 (15% de penalización)
  • EX predicho: {ex_predicho:.4f}

Factores de incertidumbre:
  • Complejidad de esquemas ocultos (puede ser mayor que validación)
  • Tipos de queries no vistas durante entrenamiento
  • Nombre de tablas/columnas en español vs inglés
  • Uso de funciones de fecha específicas de MySQL

Conclusión:
  El modelo debería alcanzar un EX entre {ex_predicho_conservador:.4f} y {ex_predicho_optimista:.4f},
  con mejor estimación de {ex_predicho:.4f}. El rendimiento será superior al baseline
  (EX = {baseline_ex:.4f}) con una mejora de aproximadamente {mejor_ex - baseline_ex:.4f} puntos.
"""

print(justificacion)

# Guardar predicción
prediccion = {
    'mejor_configuracion': mejor_config,
    'ex_validacion_propia': mejor_ex,
    'ex_predicho_conservador': ex_predicho_conservador,
    'ex_predicho_probable': ex_predicho,
    'ex_predicho_optimista': ex_predicho_optimista,
    'factor_generalizacion': 0.85,
    'justificacion': justificacion.strip(),
    'metricas_entrenamiento': {
        'config_a': {
            'rank': comparacion['config_a']['rank'],
            'loss_final': config_a_metrics['loss_final'],
            'tiempo_horas': config_a_metrics['tiempo_horas']
        },
        'config_b': {
            'rank': comparacion['config_b']['rank'],
            'loss_final': config_b_metrics['loss_final'],
            'tiempo_horas': config_b_metrics['tiempo_horas']
        }
    }
}

with open('resultados/prediccion_ex.json', 'w') as f:
    json.dump(prediccion, f, indent=2)

print(f"\n✓ Predicción guardada en: resultados/prediccion_ex.json")
