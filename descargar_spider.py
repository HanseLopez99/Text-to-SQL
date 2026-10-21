"""
descargar_spider.py
Descarga y procesa el dataset Spider (SQLite -> MySQL + español)
"""
import json
import os
import re
import urllib.request
import zipfile
from pathlib import Path

SPIDER_URL = "https://drive.google.com/uc?export=download&id=1TqYTyDNfEBSgfyWFxbMSwKrlMPZkGGiR"
SPIDER_DIR = Path("datos/spider_raw")
SPIDER_TRAIN = SPIDER_DIR / "train_spider.json"
SPIDER_TABLES = SPIDER_DIR / "tables.json"

def descargar_spider():
    """Descarga el dataset Spider si no existe."""
    SPIDER_DIR.mkdir(parents=True, exist_ok=True)
    
    if SPIDER_TRAIN.exists() and SPIDER_TABLES.exists():
        print("✓ Spider ya descargado")
        return True
    
    print("Spider requiere descarga manual:")
    print("1. Ir a: https://yale-lily.github.io/spider")
    print("2. Descargar 'train_spider.json' y 'tables.json'")
    print(f"3. Colocarlos en: {SPIDER_DIR}/")
    print("\nAlternativa: usar solo datos generados localmente")
    return False


def sqlite_a_mysql(sql: str) -> str:
    """Convierte sintaxis SQLite a MySQL 8.4."""
    sql = re.sub(r'\bLIMIT\s+1\s+OFFSET\s+(\d+)\b', r'LIMIT 1 OFFSET \1', sql)
    sql = re.sub(r"STRFTIME\('%Y',\s*(.+?)\)", r"YEAR(\1)", sql, flags=re.IGNORECASE)
    sql = re.sub(r"STRFTIME\('%m',\s*(.+?)\)", r"MONTH(\1)", sql, flags=re.IGNORECASE)
    sql = re.sub(r"STRFTIME\('%d',\s*(.+?)\)", r"DAY(\1)", sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bIFNULL\b', 'COALESCE', sql, flags=re.IGNORECASE)
    return sql.strip()


def procesar_spider():
    """Procesa Spider y lo convierte a formato MySQL."""
    if not SPIDER_TRAIN.exists():
        print("❌ Spider no disponible, omitiendo")
        return []
    
    with open(SPIDER_TRAIN, 'r', encoding='utf-8') as f:
        train_data = json.load(f)
    
    with open(SPIDER_TABLES, 'r', encoding='utf-8') as f:
        tables_data = json.load(f)
    
    print(f"Procesando {len(train_data)} ejemplos de Spider...")
    
    # Crear mapeo db_id -> schema
    db_schemas = {}
    for db in tables_data:
        db_id = db['db_id']
        table_names = db['table_names_original']
        column_names = db['column_names_original']
        
        schema_lines = []
        for i, table in enumerate(table_names):
            cols = [c for c in column_names if c[0] == i+1]  # columnas de esta tabla
            col_defs = []
            for col in cols:
                col_name = col[2]
                col_type = col[3]
                col_defs.append(f"    {col_name} {col_type}")
            if col_defs:
                schema_lines.append(f"CREATE TABLE {table} (\n" + ",\n".join(col_defs) + "\n)")
        
        db_schemas[db_id] = "\n\n".join(schema_lines)
    
    # Convertir cada ejemplo
    pares = []
    descartados = 0
    
    for item in train_data:
        try:
            db_id = item['db_id']
            question = item['question']  # Inglés
            sql = item['query']  # SQLite
            
            if db_id not in db_schemas:
                descartados += 1
                continue
            
            # Convertir SQL a MySQL
            sql_mysql = sqlite_a_mysql(sql)
            
            # TODO: Traducir pregunta al español (usar modelo de traducción)
            # Por ahora mantener en inglés como placeholder
            pregunta_es = question  # Placeholder
            
            pares.append({
                "pregunta": pregunta_es,
                "sql": sql_mysql,
                "nivel": "media",  # Spider es principalmente nivel medio
                "esquema": db_id,
                "peso": 2,
                "fuente": "spider"
            })
        except Exception as e:
            descartados += 1
    
    print(f"✓ Convertidos: {len(pares)}, Descartados: {descartados}")
    return pares


if __name__ == "__main__":
    descargar_spider()
    pares = procesar_spider()
    
    if pares:
        output = Path("datos/entrenamiento/spider_convertido.json")
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(pares, f, ensure_ascii=False, indent=2)
        print(f"Guardado en {output}")
