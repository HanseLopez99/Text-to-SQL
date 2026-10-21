"""
validar_dataset.py
Valida que todas las queries del dataset sean válidas en MySQL 8.4.10
Requiere MySQL corriendo (local o Docker)
"""
import json
import mysql.connector
import re
from pathlib import Path
from tqdm import tqdm

# Configuración MySQL
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",  # Cambiar según configuración
    "charset": "utf8mb4"
}

def crear_db_si_no_existe(cursor, db_name="text_to_sql_test"):
    """Crea la base de datos de prueba si no existe."""
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    cursor.execute(f"USE {db_name}")


def cargar_esquemas():
    """Carga todos los esquemas SQL."""
    esquemas = {}
    for path in Path("datos/esquemas").rglob("*.sql"):
        nombre = path.stem
        with open(path, 'r', encoding='utf-8') as f:
            esquemas[nombre] = f.read()
    return esquemas


def validar_schema(cursor, schema_sql, schema_name):
    """Crea las tablas del esquema en la base de datos."""
    # Limpiar tablas existentes
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # Obtener tablas existentes
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    
    # Eliminar tablas
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
        except:
            pass
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    # Dividir el schema en statements individuales
    statements = []
    current = []
    
    for line in schema_sql.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        current.append(line)
        if line.endswith(';'):
            statements.append(' '.join(current))
            current = []
    
    if current:
        statements.append(' '.join(current))
    
    # Ejecutar cada statement
    for stmt in statements:
        if stmt.strip():
            # Limpiar COMMENTs de tabla para compatibilidad
            stmt = re.sub(r"\) COMMENT='[^']*';", ");", stmt)
            stmt = re.sub(r"COMMENT '[^']*'", "", stmt)
            try:
                cursor.execute(stmt)
            except mysql.connector.Error as e:
                print(f"  ⚠ Error creando tabla en {schema_name}: {e}")
                return False
    
    return True


def validar_query(cursor, sql, timeout=5):
    """Valida que una query sea sintácticamente correcta."""
    try:
        cursor.execute(f"SET SESSION MAX_EXECUTION_TIME={timeout*1000}")
        # Solo analizar, no ejecutar
        cursor.execute(f"EXPLAIN {sql}")
        return True, None
    except mysql.connector.Error as e:
        return False, str(e)


def validar_dataset():
    """Valida todo el dataset contra MySQL."""
    print("Conectando a MySQL...")
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except mysql.connector.Error as e:
        print(f"❌ No se pudo conectar a MySQL: {e}")
        print("\nOpciones:")
        print("1. Iniciar Docker: open -a Docker")
        print("2. Ejecutar: docker run -d --name mysql-text2sql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password mysql:8.4.10")
        print("3. O instalar MySQL 8.4.10 localmente")
        return None
    
    print("✓ Conectado a MySQL")
    
    # Cargar dataset
    with open("datos/entrenamiento/dataset_completo.json", 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    print(f"Validando {len(dataset)} queries...")
    
    esquemas = cargar_esquemas()
    resultados = {"validos": [], "invalidos": []}
    
    # Agrupar por esquema
    por_esquema = {}
    for item in dataset:
        esquema = item.get("esquema", "desconocido")
        if esquema not in por_esquema:
            por_esquema[esquema] = []
        por_esquema[esquema].append(item)
    
    # Validar cada esquema
    for esquema_nombre, items in por_esquema.items():
        if esquema_nombre not in esquemas:
            print(f"\n⚠ Esquema '{esquema_nombre}' no encontrado, omitiendo {len(items)} queries")
            continue
        
        print(f"\n=== Validando esquema: {esquema_nombre} ({len(items)} queries) ===")
        
        # Crear tablas
        if not validar_schema(cursor, esquemas[esquema_nombre], esquema_nombre):
            resultados["invalidos"].extend(items)
            continue
        
        # Validar cada query
        for item in tqdm(items, desc=esquema_nombre):
            sql = item["sql"]
            valido, error = validar_query(cursor, sql)
            
            if valido:
                resultados["validos"].append(item)
            else:
                item["error"] = error
                resultados["invalidos"].append(item)
    
    cursor.close()
    conn.close()
    
    # Resumen
    print(f"\n{'='*60}")
    print(f"Resultados de validación:")
    print(f"  Válidas: {len(resultados['validos'])}")
    print(f"  Inválidas: {len(resultados['invalidos'])}")
    print(f"  Total: {len(dataset)}")
    
    # Guardar resultados
    Path("datos/descartes").mkdir(exist_ok=True)
    
    with open("datos/descartes/queries_invalidas.json", 'w', encoding='utf-8') as f:
        json.dump(resultados["invalidos"], f, ensure_ascii=False, indent=2)
    
    # Guardar dataset válido
    with open("datos/entrenamiento/dataset_valido.json", 'w', encoding='utf-8') as f:
        json.dump(resultados["validos"], f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Dataset válido guardado en datos/entrenamiento/dataset_valido.json")
    print(f"✓ Queries inválidas guardadas en datos/descartes/queries_invalidas.json")
    
    return resultados


if __name__ == "__main__":
    resultados = validar_dataset()
    
    if resultados is None:
        print("\n⚠ Validación omitida - MySQL no disponible")
        print("Las queries serán validadas durante el entrenamiento en Colab")
    elif len(resultados["validos"]) >= 2000:
        print(f"\n✓ Dataset cumple requisito mínimo (2000+ pares válidos)")
    else:
        print(f"\n⚠ Dataset tiene {len(resultados['validos'])} pares válidos (mínimo 2000)")
        print("Considera generar más datos o revisar queries inválidas")
