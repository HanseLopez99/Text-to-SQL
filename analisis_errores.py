"""
Análisis de Errores por Categoría
Clasifica los errores del modelo fine-tuned en categorías específicas
"""
import json
import pandas as pd
from collections import Counter

print("=" * 60)
print("ANÁLISIS DE ERRORES POR CATEGORÍA")
print("=" * 60)

# Cargar resultados de Config A
try:
    df = pd.read_csv('resultados/finetuned_results.csv')
except:
    print("⚠ No se encontraron resultados de Config A")
    print("Ejecutar primero: python evaluar_completo.py")
    exit()

# Filtrar solo las preguntas incorrectas
errores = df[df['correcta'] == False].copy()

print(f"\nTotal de preguntas evaluadas: {len(df)}")
print(f"Preguntas correctas: {len(df[df['correcta'] == True])}")
print(f"Preguntas incorrectas: {len(errores)}")

# Función para clasificar errores
def clasificar_error(row):
    """Clasifica el error en categorías específicas"""
    sql_gen = str(row['sql_generada']).upper()
    sql_ref = str(row['sql_referencia']).upper()
    error = str(row.get('error', '')).lower()
    
    # Categoría 1: Error de sintaxis
    if 'syntax' in error or 'parse' in error:
        return 'sintaxis'
    
    # Categoría 2: Columna o tabla inexistente
    if 'unknown column' in error or 'unknown table' in error:
        return 'columna_tabla_inexistente'
    
    # Categoría 3: Error de JOIN
    if 'JOIN' in sql_ref and 'JOIN' not in sql_gen:
        return 'join_faltante'
    if sql_gen.count('JOIN') != sql_ref.count('JOIN'):
        return 'join_incorrecto'
    
    # Categoría 4: Error de agregación
    if any(agg in sql_ref for agg in ['COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN(']):
        if not any(agg in sql_gen for agg in ['COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN(']):
            return 'agregacion_faltante'
        if 'GROUP BY' in sql_ref and 'GROUP BY' not in sql_gen:
            return 'group_by_faltante'
    
    # Categoría 5: Error de filtro
    if 'WHERE' in sql_ref and 'WHERE' not in sql_gen:
        return 'filtro_faltante'
    
    # Categoría 6: Error de ordenamiento/limite
    if 'ORDER BY' in sql_ref and 'ORDER BY' not in sql_gen:
        return 'order_by_faltante'
    if 'LIMIT' in sql_ref and 'LIMIT' not in sql_gen:
        return 'limit_faltante'
    
    # Categoría 7: Error de subconsulta
    if sql_ref.count('SELECT') > 1 and sql_gen.count('SELECT') <= 1:
        return 'subconsulta_faltante'
    
    # Categoría 8: Resultado distinto (query se ejecuta pero da resultados diferentes)
    if error == '' or error == 'None':
        return 'resultado_distinto'
    
    return 'otro'

# Clasificar todos los errores
errores['categoria'] = errores.apply(clasificar_error, axis=1)

# Estadísticas por categoría
print("\n" + "=" * 60)
print("DISTRIBUCIÓN DE ERRORES POR CATEGORÍA")
print("=" * 60)

categorias = errores['categoria'].value_counts()
total_errores = len(errores)

for categoria, count in categorias.items():
    porcentaje = (count / total_errores) * 100
    print(f"{categoria:30s}: {count:3d} ({porcentaje:5.1f}%)")

# Análisis por nivel de dificultad
print("\n" + "=" * 60)
print("ERRORES POR NIVEL DE DIFICULTAD")
print("=" * 60)

for nivel in ['facil', 'medio', 'dificil']:
    errores_nivel = errores[errores['nivel'] == nivel]
    if len(errores_nivel) > 0:
        print(f"\n{nivel.upper()} ({len(errores_nivel)} errores):")
        categorias_nivel = errores_nivel['categoria'].value_counts()
        for categoria, count in categorias_nivel.items():
            porcentaje = (count / len(errores_nivel)) * 100
            print(f"  {categoria:30s}: {count:3d} ({porcentaje:5.1f}%)")

# Guardar análisis
analisis = {
    'total_preguntas': len(df),
    'preguntas_correctas': len(df[df['correcta'] == True]),
    'preguntas_incorrectas': len(errores),
    'tasa_exito': len(df[df['correcta'] == True]) / len(df),
    'distribucion_errores': categorias.to_dict(),
    'errores_por_nivel': {}
}

for nivel in ['facil', 'medio', 'dificil']:
    errores_nivel = errores[errores['nivel'] == nivel]
    if len(errores_nivel) > 0:
        analisis['errores_por_nivel'][nivel] = errores_nivel['categoria'].value_counts().to_dict()

with open('resultados/analisis_errores.json', 'w') as f:
    json.dump(analisis, f, indent=2)

# Guardar errores detallados
errores.to_csv('resultados/errores_detallados.csv', index=False)

print("\n" + "=" * 60)
print("RESULTADOS GUARDADOS")
print("=" * 60)
print("✓ resultados/analisis_errores.json")
print("✓ resultados/errores_detallados.csv")

# Ejemplos de errores por categoría
print("\n" + "=" * 60)
print("EJEMPLOS DE ERRORES POR CATEGORÍA")
print("=" * 60)

for categoria in categorias.index[:5]:  # Top 5 categorías
    print(f"\n--- {categoria.upper()} ---")
    ejemplos = errores[errores['categoria'] == categoria].head(2)
    for idx, row in ejemplos.iterrows():
        print(f"\nPregunta: {row['pregunta'][:100]}...")
        print(f"SQL Esperada: {row['sql_referencia'][:100]}...")
        print(f"SQL Generada: {row['sql_generada'][:100]}...")
        if pd.notna(row.get('error')) and row['error'] != '':
            print(f"Error: {row['error'][:100]}...")
