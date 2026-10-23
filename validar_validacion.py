"""
validar_validacion.py
Valida las 41 preguntas del dataset de validación en MySQL 8.4.10
"""
import json
import re
from pathlib import Path
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "text2sql",
    "charset": "utf8mb4"
}


def limpiar_comentarios_sql(sql_text):
    """Limpia los COMMENT de un schema SQL."""
    sql_text = re.sub(r"\s+COMMENT\s+'[^']*'", "", sql_text)
    sql_text = re.sub(r"\)\s+COMMENT\s*=\s*'[^']*'", ")", sql_text)
    return sql_text


def setup_database(cursor):
    """Crea o recrea la base de datos."""
    cursor.execute("DROP DATABASE IF EXISTS text_to_sql_val")
    cursor.execute("CREATE DATABASE text_to_sql_val CHARACTER SET utf8mb4")
    cursor.execute("USE text_to_sql_val")


def crear_tablas(cursor, schema_sql):
    """Crea las tablas del esquema."""
    schema_clean = limpiar_comentarios_sql(schema_sql)
    statements = []
    current = []
    for line in schema_clean.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        current.append(line)
        if line.endswith(';'):
            stmt = ' '.join(current)
            if stmt.strip() and stmt.strip() != ';':
                statements.append(stmt)
            current = []
    if current:
        stmt = ' '.join(current).strip()
        if stmt and stmt != ';':
            statements.append(stmt)
    for stmt in statements:
        if stmt.strip():
            cursor.execute(stmt)
    return True


def validar_query(cursor, sql):
    """Valida una query."""
    try:
        cursor.execute(f"EXPLAIN {sql}")
        cursor.fetchall()
        return True, None
    except mysql.connector.Error as e:
        try:
            cursor.fetchall()
        except:
            pass
        return False, str(e)


def main():
    print("=" * 60)
    print("VALIDACIÓN DEL DATASET DE VALIDACIÓN (41 preguntas)")
    print("=" * 60)
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✓ Conectado a MySQL")
    
    # Cargar dataset de validación
    with open("datos/validacion/validacion.json", 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    print(f"✓ {len(dataset)} esquemas cargados")
    
    total_preguntas = 0
    total_validas = 0
    total_invalidas = 0
    
    for esquema_data in dataset:
        nombre = esquema_data["nombre"]
        schema_sql = esquema_data["esquema"]
        preguntas = esquema_data["preguntas"]
        
        print(f"\n=== {nombre} ({len(preguntas)} preguntas) ===")
        
        # Crear tablas
        setup_database(cursor)
        crear_tablas(cursor, schema_sql)
        
        validas = 0
        invalidas = 0
        
        for pregunta_data in preguntas:
            sql = pregunta_data["sql"]
            valido, error = validar_query(cursor, sql)
            
            if valido:
                validas += 1
            else:
                invalidas += 1
                print(f"  ✗ {pregunta_data['pregunta'][:60]}...")
                print(f"    Error: {error}")
            
            pregunta_data["valida"] = valido
            if error:
                pregunta_data["error"] = error
        
        total_preguntas += len(preguntas)
        total_validas += validas
        total_invalidas += invalidas
        
        print(f"  ✓ Válidas: {validas}, ✗ Inválidas: {invalidas}")
    
    cursor.close()
    conn.close()
    
    # Resumen
    print(f"\n{'='*60}")
    print(f"RESULTADOS FINALES")
    print(f"{'='*60}")
    print(f"  Total preguntas:  {total_preguntas}")
    print(f"  Válidas:          {total_validas}")
    print(f"  Inválidas:        {total_invalidas}")
    print(f"  % Válidas:        {total_validas/total_preguntas*100:.1f}%")
    
    # Guardar dataset actualizado
    with open("datos/validacion/validacion.json", 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Dataset de validación actualizado")
    
    if total_invalidas > 0:
        print(f"\n⚠ {total_invalidas} preguntas inválidas requieren corrección")
    else:
        print(f"\n✓ Todas las preguntas son válidas")


if __name__ == "__main__":
    main()
