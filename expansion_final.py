"""
expansion_final.py - Expansión final para superar los 2,000 pares.
Agrega queries adicionales complejas y variaciones.
"""

import json
import random
from pathlib import Path

random.seed(2027)

def cargar_dataset():
    with open("datos/entrenamiento/dataset_completo.json", "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_esquemas():
    esquemas = {}
    for f in Path("datos/esquemas/entrenamiento").glob("*.sql"):
        esquemas[f.stem] = f.read_text()
    return esquemas

def extraer_tablas(sql):
    import re
    tablas = {}
    tabla_actual = None
    for linea in sql.split("\n"):
        linea = linea.strip()
        m = re.match(r'CREATE TABLE (\w+)', linea, re.IGNORECASE)
        if m:
            tabla_actual = m.group(1)
            tablas[tabla_actual] = {"columnas": [], "foreign_keys": []}
            continue
        if tabla_actual is None:
            continue
        m = re.match(r'(\w+)\s+([\w(,)]+)\s+.*?COMMENT\s+\'([^\']*)\'', linea)
        if m and m.group(1).upper() not in ("PRIMARY", "FOREIGN", "UNIQUE", "KEY"):
            tablas[tabla_actual]["columnas"].append({
                "nombre": m.group(1),
                "tipo": m.group(2),
                "comentario": m.group(3)
            })
        m = re.match(r'FOREIGN KEY \((\w+)\) REFERENCES (\w+)\((\w+)\)', linea, re.IGNORECASE)
        if m:
            tablas[tabla_actual]["foreign_keys"].append({
                "columna": m.group(1),
                "tabla_ref": m.group(2),
                "columna_ref": m.group(3)
            })
    return tablas

def generar_queries_extra(esquemas):
    queries = []
    
    for nombre, sql in esquemas.items():
        tablas = extraer_tablas(sql)
        tnames = list(tablas.keys())
        
        for tname, tinfo in tablas.items():
            cols = tinfo["columnas"]
            col_names = [c["nombre"] for c in cols if c["nombre"] != "id"]
            col_num = [c["nombre"] for c in cols if any(t in c["tipo"].upper() for t in ["DECIMAL", "INT"]) and "id" not in c["nombre"].lower()]
            col_date = [c["nombre"] for c in cols if "DATE" in c["tipo"].upper()]
            col_varchar = [c["nombre"] for c in cols if "VARCHAR" in c["tipo"].upper() and c["nombre"] != "id"]
            fks = tinfo.get("foreign_keys", [])
            
            # Queries de ORDER BY con diferentes columnas
            for cn in col_names[:3]:
                queries.append({
                    "pregunta": f"Lista los {tname.replace('_', ' ')} ordenados por {cn}",
                    "sql": f"SELECT * FROM {tname} ORDER BY {cn}",
                    "nivel": "facil", "esquema": nombre, "peso": 1
                })
            
            # Queries LIMIT con variaciones
            for n in [3, 5, 10, 20]:
                queries.append({
                    "pregunta": f"Muestra los primeros {n} registros de {tname.replace('_', ' ')}",
                    "sql": f"SELECT * FROM {tname} LIMIT {n}",
                    "nivel": "facil", "esquema": nombre, "peso": 1
                })
            
            # Queries de COUNT con condición de fecha
            for cd in col_date[:1]:
                queries.append({
                    "pregunta": f"¿Cuántos {tname.replace('_', ' ')} fueron registrados en 2024?",
                    "sql": f"SELECT COUNT(*) FROM {tname} WHERE YEAR({cd}) = 2024",
                    "nivel": "facil", "esquema": nombre, "peso": 1
                })
                queries.append({
                    "pregunta": f"¿Cuántos {tname.replace('_', ' ')} fueron registrados en 2026?",
                    "sql": f"SELECT COUNT(*) FROM {tname} WHERE YEAR({cd}) = 2026",
                    "nivel": "facil", "esquema": nombre, "peso": 1
                })
            
            # SUM con GROUP BY
            if col_num and fks:
                fk = fks[0]
                tabla_ref = fk["tabla_ref"]
                ref_cols = tablas.get(tabla_ref, {}).get("columnas", [])
                ref_name = next((c["nombre"] for c in ref_cols if "nombre" in c["nombre"].lower()), None)
                for cn in col_num[:1]:
                    if ref_name:
                        queries.append({
                            "pregunta": f"¿Cuál es la suma total de {cn} agrupada por {tabla_ref.replace('_', ' ')}?",
                            "sql": f"SELECT r.{ref_name}, SUM(t.{cn}) AS total FROM {tname} t JOIN {tabla_ref} r ON t.{fk['columna']} = r.{fk['columna_ref']} GROUP BY r.{fk['columna_ref']}, r.{ref_name}",
                            "nivel": "media", "esquema": nombre, "peso": 2
                        })
            
            # AVG y MAX por grupo
            if col_num and col_varchar:
                vc = col_varchar[0]
                cn = col_num[0]
                queries.append({
                    "pregunta": f"¿Cuál es el promedio de {cn} para cada {vc} en {tname.replace('_', ' ')}?",
                    "sql": f"SELECT {vc}, AVG({cn}) AS promedio FROM {tname} GROUP BY {vc}",
                    "nivel": "media", "esquema": nombre, "peso": 2
                })
                queries.append({
                    "pregunta": f"¿Cuál es el máximo de {cn} para cada {vc} en {tname.replace('_', ' ')}?",
                    "sql": f"SELECT {vc}, MAX({cn}) AS maximo FROM {tname} GROUP BY {vc}",
                    "nivel": "media", "esquema": nombre, "peso": 2
                })
            
            # Subconsulta con IN
            if fks:
                fk = fks[0]
                tabla_ref = fk["tabla_ref"]
                ref_cols = tablas.get(tabla_ref, {}).get("columnas", [])
                ref_name = next((c["nombre"] for c in ref_cols if "nombre" in c["nombre"].lower()), None)
                if ref_name:
                    queries.append({
                        "pregunta": f"¿Cuáles {tname.replace('_', ' ')} pertenecen a un {tabla_ref.replace('_', ' ')} cuyo nombre contiene la letra 'a'?",
                        "sql": f"SELECT t.* FROM {tname} t WHERE t.{fk['columna']} IN (SELECT r.id FROM {tabla_ref} r WHERE r.{ref_name} LIKE '%a%')",
                        "nivel": "dificil", "esquema": nombre, "peso": 3
                    })
            
            # RANK con partition
            if col_num and fks:
                fk = fks[0]
                cn = col_num[0]
                queries.append({
                    "pregunta": f"Ranking de {tname.replace('_', ' ')} por {cn} dentro de cada grupo usando funciones de ventana",
                    "sql": f"SELECT *, RANK() OVER (PARTITION BY {fk['columna']} ORDER BY {cn} DESC) AS ranking FROM {tname}",
                    "nivel": "dificil", "esquema": nombre, "peso": 3
                })
    
    return queries


def main():
    print("Cargando dataset...")
    dataset = cargar_dataset()
    print(f"Pares actuales: {len(dataset)}")
    
    print("Generando queries adicionales...")
    esquemas = cargar_esquemas()
    adicionales = generar_queries_extra(esquemas)
    print(f"Queries adicionales: {len(adicionales)}")
    
    # Combinar
    dataset_completo = dataset + adicionales
    
    # Eliminar duplicados
    vistos = set()
    sin_duplicados = []
    for par in dataset_completo:
        key = (par["pregunta"], par["sql"])
        if key not in vistos:
            vistos.add(key)
            sin_duplicados.append(par)
    
    facil = sum(1 for p in sin_duplicados if p["nivel"] == "facil")
    medio = sum(1 for p in sin_duplicados if p["nivel"] == "media")
    dificil = sum(1 for p in sin_duplicados if p["nivel"] == "dificil")
    
    print(f"\n{'='*60}")
    print(f"Dataset final:")
    print(f"Total pares: {len(sin_duplicados)}")
    print(f"  Fácil: {facil}")
    print(f"  Medio: {medio}")
    print(f"  Difícil: {dificil}")
    
    with open("datos/entrenamiento/dataset_completo.json", "w", encoding="utf-8") as f:
        json.dump(sin_duplicados, f, ensure_ascii=False, indent=2)
    
    print(f"\nDataset guardado.")

if __name__ == "__main__":
    main()
