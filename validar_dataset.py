"""
validar_dataset.py
Valida que todas las queries del dataset sean válidas en MySQL 8.4.10
"""
import json
import re
from pathlib import Path
import mysql.connector
from tqdm import tqdm

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "text2sql",
    "charset": "utf8mb4",
    "database": "text_to_sql_test"
}


def limpiar_comentarios_sql(sql_text):
    """Limpia los COMMENT de un schema SQL para compatibilidad."""
    # Eliminar COMMENT en columnas
    sql_text = re.sub(r"\s+COMMENT\s+'[^']*'", "", sql_text)
    # Eliminar COMMENT de tabla
    sql_text = re.sub(r"\)\s+COMMENT\s*=\s*'[^']*'", ")", sql_text)
    return sql_text


def setup_database(cursor):
    """Crea o recrea la base de datos de prueba."""
    cursor.execute("DROP DATABASE IF EXISTS text_to_sql_test")
    cursor.execute("CREATE DATABASE text_to_sql_test CHARACTER SET utf8mb4")
    cursor.execute("USE text_to_sql_test")


def crear_tablas(cursor, schema_sql):
    """Crea las tablas del esquema."""
    # Limpiar comentarios
    schema_clean = limpiar_comentarios_sql(schema_sql)
    
    # Dividir en statements
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
        stmt = stmt.strip()
        if stmt:
            try:
                cursor.execute(stmt)
            except mysql.connector.Error as e:
                return False, str(e)
    
    return True, None


def validar_query(cursor, sql):
    """Valida una query usando EXPLAIN."""
    try:
        cursor.execute(f"EXPLAIN {sql}")
        cursor.fetchall()  # Consumir resultados
        return True, None
    except mysql.connector.Error as e:
        try:
            cursor.fetchall()  # Consumir resultados del error
        except:
            pass
        return False, str(e)


def cargar_esquemas():
    """Carga todos los esquemas SQL."""
    esquemas = {}
    for path in Path("datos/esquemas/entrenamiento").glob("*.sql"):
        with open(path, 'r', encoding='utf-8') as f:
            esquemas[path.stem] = f.read()
    return esquemas


def main():
    print("=" * 60)
    print("VALIDACIÓN DE DATASET EN MySQL 8.4.10")
    print("=" * 60)
    
    # Conectar
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except mysql.connector.Error:
        # Intentar sin database
        config = DB_CONFIG.copy()
        config.pop("database", None)
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
        except mysql.connector.Error as e:
            print(f"❌ No se pudo conectar: {e}")
            return
    
    print("✓ Conectado a MySQL")
    setup_database(cursor)
    print("✓ Base de datos creada")
    
    # Cargar dataset
    with open("datos/entrenamiento/dataset_completo.json", 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    esquemas = cargar_esquemas()
    print(f"✓ {len(dataset)} queries a validar")
    
    # Agrupar por esquema
    por_esquema = {}
    for item in dataset:
        esquema = item.get("esquema", "desconocido")
        if esquema not in por_esquema:
            por_esquema[esquema] = []
        por_esquema[esquema].append(item)
    
    validos = []
    invalidos = []
    
    for esquema_nombre, items in por_esquema.items():
        if esquema_nombre not in esquemas:
            print(f"\n⚠ Esquema '{esquema_nombre}' no encontrado, {len(items)} queries omitidas")
            invalidos.extend(items)
            continue
        
        # Recrear tablas para este esquema
        setup_database(cursor)
        ok, err = crear_tablas(cursor, esquemas[esquema_nombre])
        
        if not ok:
            print(f"\n❌ Error creando tablas para {esquema_nombre}: {err}")
            invalidos.extend(items)
            continue
        
        print(f"\n=== {esquema_nombre} ({len(items)} queries) ===")
        
        esquema_validos = 0
        esquema_invalidos = 0
        
        for item in tqdm(items, desc=esquema_nombre):
            sql = item["sql"]
            valido, error = validar_query(cursor, sql)
            
            if valido:
                validos.append(item)
                esquema_validos += 1
            else:
                item_err = item.copy()
                item_err["error"] = error
                invalidos.append(item_err)
                esquema_invalidos += 1
        
        print(f"  ✓ Válidas: {esquema_validos}, ✗ Inválidas: {esquema_invalidos}")
    
    cursor.close()
    conn.close()
    
    # Resumen
    print(f"\n{'='*60}")
    print(f"RESULTADOS FINALES")
    print(f"{'='*60}")
    print(f"  Válidas:    {len(validos)}")
    print(f"  Inválidas:  {len(invalidos)}")
    print(f"  Total:      {len(dataset)}")
    print(f"  % Válidas:  {len(validos)/len(dataset)*100:.1f}%")
    
    # Por nivel
    for nivel in ["facil", "media", "dificil"]:
        v = sum(1 for p in validos if p["nivel"] == nivel)
        i = sum(1 for p in invalidos if p["nivel"] == nivel)
        print(f"  {nivel}: válidas={v}, inválidas={i}")
    
    # Guardar resultados
    Path("datos/descartes").mkdir(exist_ok=True)
    
    with open("datos/entrenamiento/dataset_valido.json", 'w', encoding='utf-8') as f:
        json.dump(validos, f, ensure_ascii=False, indent=2)
    
    with open("datos/descartes/queries_invalidas.json", 'w', encoding='utf-8') as f:
        json.dump(invalidos, f, ensure_ascii=False, indent=2)
    
    # Reporte de descartes
    reporte = {
        "total_generados": len(dataset),
        "validos_mysql": len(validos),
        "invalidos": len(invalidos),
        "porcentaje_validos": round(len(validos)/len(dataset)*100, 1),
        "descartados_sintaxis": sum(1 for i in invalidos if "syntax" in i.get("error", "").lower()),
        "descartados_columna": sum(1 for i in invalidos if "unknown column" in i.get("error", "").lower()),
        "descartados_tabla": sum(1 for i in invalidos if "doesn't exist" in i.get("error", "").lower()),
        "descartados_otro": sum(1 for i in invalidos if "syntax" not in i.get("error", "").lower() and "unknown column" not in i.get("error", "").lower() and "doesn't exist" not in i.get("error", "").lower())
    }
    
    with open("datos/descartes/reporte_descartes.json", 'w', encoding='utf-8') as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Dataset válido guardado en datos/entrenamiento/dataset_valido.json")
    print(f"✓ Queries inválidas guardadas en datos/descartes/queries_invalidas.json")
    
    if len(validos) >= 2000:
        print(f"\n✓ CUMPLE requisito mínimo: {len(validos)} pares válidos (>= 2000)")
    else:
        print(f"\n⚠ NO cumple mínimo: {len(validos)} pares válidos (se necesitan 2000)")


if __name__ == "__main__":
    main()
