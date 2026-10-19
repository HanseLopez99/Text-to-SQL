"""
generar_dataset.py - Pipeline de generación de datos para entrenamiento
Genera pares pregunta-SQL válidos sobre los esquemas propios.
Usa templates + variaciones para cubrir múltiples niveles de dificultad.
"""

import json
import os
import re
import random
from pathlib import Path
from itertools import product


random.seed(2026)

# ============================================
# 1. Cargar esquemas y extraer metadata
# ============================================

def cargar_esquemas(ruta="datos/esquemas/entrenamiento"):
    esquemas = {}
    for f in Path(ruta).glob("*.sql"):
        esquemas[f.stem] = f.read_text()
    return esquemas


def extraer_metadata(esquema_sql):
    """Extrae tablas, columnas y relaciones de un esquema SQL."""
    tablas = {}
    tabla_actual = None
    
    for linea in esquema_sql.split("\n"):
        linea = linea.strip()
        
        # Detectar CREATE TABLE
        m = re.match(r'CREATE TABLE (\w+)', linea, re.IGNORECASE)
        if m:
            tabla_actual = m.group(1)
            tablas[tabla_actual] = {"columnas": [], "comentario": ""}
            continue
        
        if tabla_actual is None:
            continue
        
        # Detectar comentario de tabla
        m = re.search(r"COMMENT\s*=\s*'([^']*)'", linea, re.IGNORECASE)
        if m and "CREATE" not in linea.upper():
            tablas[tabla_actual]["comentario"] = m.group(1)
            continue
        
        # Detectar columnas con su comentario
        m = re.match(r'(\w+)\s+(.+?)\s+COMMENT\s+\'([^\']*)\'', linea, re.IGNORECASE)
        if m:
            col_nombre = m.group(1)
            col_tipo = m.group(2).rstrip(",").strip()
            col_comentario = m.group(3)
            
            if col_nombre.upper() not in ("PRIMARY", "FOREIGN", "UNIQUE", "KEY", "INDEX"):
                tablas[tabla_actual]["columnas"].append({
                    "nombre": col_nombre,
                    "tipo": col_tipo,
                    "comentario": col_comentario
                })
        
        # Detectar FOREIGN KEY
        m = re.match(r'FOREIGN KEY \((\w+)\) REFERENCES (\w+)\((\w+)\)', linea, re.IGNORECASE)
        if m:
            if "foreign_keys" not in tablas[tabla_actual]:
                tablas[tabla_actual]["foreign_keys"] = []
            tablas[tabla_actual]["foreign_keys"].append({
                "columna": m.group(1),
                "tabla_ref": m.group(2),
                "columna_ref": m.group(3)
            })
    
    return tablas


# ============================================
# 2. Templates de generación
# ============================================

# --- Nivel FÁCIL ---

def template_contar(tablas):
    pares = []
    for tname, tinfo in tablas.items():
        desc = tinfo.get("comentario", tname)
        pares.append({
            "pregunta": f"¿Cuántos registros hay en {desc.lower()}?",
            "sql": f"SELECT COUNT(*) FROM {tname}",
            "nivel": "facil"
        })
        pares.append({
            "pregunta": f"¿Cuántos {tname.replace('_', ' ')} hay registrados?",
            "sql": f"SELECT COUNT(*) FROM {tname}",
            "nivel": "facil"
        })
    return pares


def template_listar_todos(tablas):
    pares = []
    for tname, tinfo in tablas.items():
        cols = tinfo["columnas"]
        if cols:
            cols_principales = [c["nombre"] for c in cols[:3]]
            col_str = ", ".join(cols_principales)
            desc = tinfo.get("comentario", tname)
            pares.append({
                "pregunta": f"Muestra todos los registros de {desc.lower()}",
                "sql": f"SELECT {col_str} FROM {tname}",
                "nivel": "facil"
            })
    return pares


def template_filtro_simple(tablas):
    pares = []
    for tname, tinfo in tablas.items():
        cols = tinfo["columnas"]
        for col in cols:
            coltipo = col["tipo"].upper()
            colname = col["nombre"]
            
            # Filtro por VARCHAR con valor conocido
            if "BOOLEAN" in coltipo or "BOOL" in coltipo:
                pares.append({
                    "pregunta": f"¿Cuáles están activos en {tname.replace('_', ' ')}?",
                    "sql": f"SELECT * FROM {tname} WHERE {colname} = TRUE",
                    "nivel": "facil"
                })
                pares.append({
                    "pregunta": f"¿Cuáles no están activos en {tname.replace('_', ' ')}?",
                    "sql": f"SELECT * FROM {tname} WHERE {colname} = FALSE",
                    "nivel": "facil"
                })
            
            # Filtro por VARCHAR con estados comunes
            if "VARCHAR" in coltipo and colname.lower() in ("estado", "tipo", "prioridad"):
                pares.append({
                    "pregunta": f"Muestra los diferentes valores de {colname} en {tname.replace('_', ' ')}",
                    "sql": f"SELECT DISTINCT {colname} FROM {tname}",
                    "nivel": "facil"
                })
            
            # ORDER BY y LIMIT
            if "DECIMAL" in coltipo or "INT" in coltipo:
                if "precio" in colname.lower() or "monto" in colname.lower() or "saldo" in colname.lower() or "total" in colname.lower():
                    pares.append({
                        "pregunta": f"¿Cuáles son los 5 registros con mayor {colname} en {tname.replace('_', ' ')}?",
                        "sql": f"SELECT * FROM {tname} ORDER BY {colname} DESC LIMIT 5",
                        "nivel": "facil"
                    })
                    pares.append({
                        "pregunta": f"¿Cuál es el {colname} máximo en {tname.replace('_', ' ')}?",
                        "sql": f"SELECT MAX({colname}) FROM {tname}",
                        "nivel": "facil"
                    })
                    pares.append({
                        "pregunta": f"¿Cuál es el {colname} mínimo en {tname.replace('_', ' ')}?",
                        "sql": f"SELECT MIN({colname}) FROM {tname}",
                        "nivel": "facil"
                    })
                    pares.append({
                        "pregunta": f"¿Cuál es el promedio de {colname} en {tname.replace('_', ' ')}?",
                        "sql": f"SELECT AVG({colname}) FROM {tname}",
                        "nivel": "facil"
                    })
    
    return pares


def template_fecha(tablas):
    pares = []
    for tname, tinfo in tablas.items():
        cols = tinfo["columnas"]
        for col in cols:
            if "DATE" in col["tipo"].upper() and "DATETIME" not in col["tipo"].upper():
                colname = col["nombre"]
                pares.append({
                    "pregunta": f"¿Cuáles son los 10 registros más recientes por {colname} en {tname.replace('_', ' ')}?",
                    "sql": f"SELECT * FROM {tname} ORDER BY {colname} DESC LIMIT 10",
                    "nivel": "facil"
                })
                pares.append({
                    "pregunta": f"¿Cuántos registros de {tname.replace('_', ' ')} son del año 2025?",
                    "sql": f"SELECT COUNT(*) FROM {tname} WHERE YEAR({colname}) = 2025",
                    "nivel": "facil"
                })
    return pares


# --- Nivel MEDIO ---

def template_join(tablas):
    pares = []
    for tname, tinfo in tablas.items():
        fks = tinfo.get("foreign_keys", [])
        tcols = [c["nombre"] for c in tinfo["columnas"]]
        
        for fk in fks:
            tabla_ref = fk["tabla_ref"]
            col_fk = fk["columna"]
            col_ref = fk["columna_ref"]
            ref_cols = [c["nombre"] for c in tablas.get(tabla_ref, {}).get("columnas", [])]
            
            if ref_cols:
                # Seleccionar columnas legibles
                col_legible_ref = next((c for c in ref_cols if "nombre" in c.lower()), ref_cols[1] if len(ref_cols) > 1 else ref_cols[0])
                col_legible_t = next((c for c in tcols if "nombre" in c.lower()), tcols[1] if len(tcols) > 1 else tcols[0])
                
                pares.append({
                    "pregunta": f"Lista los {tname.replace('_', ' ')} junto con el nombre de su {tabla_ref.replace('_', ' ')} asociado",
                    "sql": f"SELECT t.{col_legible_t}, r.{col_legible_ref} FROM {tname} t JOIN {tabla_ref} r ON t.{col_fk} = r.{col_ref}",
                    "nivel": "media"
                })
                
                # COUNT con JOIN
                pares.append({
                    "pregunta": f"¿Cuántos {tname.replace('_', ' ')} tiene cada {tabla_ref.replace('_', ' ')}?",
                    "sql": f"SELECT r.{col_legible_ref}, COUNT(t.id) AS cantidad FROM {tabla_ref} r LEFT JOIN {tname} t ON t.{col_fk} = r.{col_ref} GROUP BY r.{col_ref}, r.{col_legible_ref}",
                    "nivel": "media"
                })
                
                # Con filtro en el JOIN
                pares.append({
                    "pregunta": f"¿Qué {tabla_ref.replace('_', ' ')} tienen más de 3 {tname.replace('_', ' ')}?",
                    "sql": f"SELECT r.{col_legible_ref}, COUNT(t.id) AS cantidad FROM {tabla_ref} r JOIN {tname} t ON t.{col_fk} = r.{col_ref} GROUP BY r.{col_ref}, r.{col_legible_ref} HAVING cantidad > 3",
                    "nivel": "media"
                })
    
    return pares


def template_agregacion(tablas):
    pares = []
    for tname, tinfo in tablas.items():
        cols = tinfo["columnas"]
        col_num = [c for c in cols if any(t in c["tipo"].upper() for t in ["DECIMAL", "INT", "FLOAT"]) and "id" not in c["nombre"].lower()]
        
        # Obtener columnas que son FK
        fk_cols = [fk["columna"] for fk in tinfo.get("foreign_keys", [])]
        
        if col_num:
            for cn in col_num[:2]:
                colname = cn["nombre"]
                # Agregar por columna de texto (no numérica, no FK)
                for cc in cols:
                    if "VARCHAR" in cc["tipo"].upper() and cc["nombre"] != colname and cc["nombre"] not in fk_cols and cc["nombre"] != "id":
                        pares.append({
                            "pregunta": f"¿Cuál es el total de {colname} por cada {cc['comentario'].lower() if cc.get('comentario') else cc['nombre']} en {tname.replace('_', ' ')}?",
                            "sql": f"SELECT {cc['nombre']}, SUM({colname}) AS total FROM {tname} GROUP BY {cc['nombre']}",
                            "nivel": "media"
                        })
                        pares.append({
                            "pregunta": f"¿Cuál es el promedio de {colname} por {cc['nombre']} en {tname.replace('_', ' ')}?",
                            "sql": f"SELECT {cc['nombre']}, AVG({colname}) AS promedio FROM {tname} GROUP BY {cc['nombre']}",
                            "nivel": "media"
                        })
                        break  # Solo un GROUP BY por columna numérica
    
    return pares


# --- Nivel DIFÍCIL ---

def template_subconsulta(tablas):
    pares = []
    for tname, tinfo in tablas.items():
        cols = tinfo["columnas"]
        col_num = [c for c in cols if any(t in c["tipo"].upper() for t in ["DECIMAL", "INT"]) and "id" not in c["nombre"].lower() and "num" not in c["nombre"].lower() and "cantidad" not in c["nombre"].lower()]
        
        if col_num:
            cn = col_num[0]
            colname = cn["nombre"]
            pares.append({
                "pregunta": f"¿Cuáles {tname.replace('_', ' ')} tienen {colname} superior al promedio?",
                "sql": f"SELECT * FROM {tname} WHERE {colname} > (SELECT AVG({colname}) FROM {tname})",
                "nivel": "dificil"
            })
            pares.append({
                "pregunta": f"¿Cuáles son los {tname.replace('_', ' ')} con el {colname} máximo?",
                "sql": f"SELECT * FROM {tname} WHERE {colname} = (SELECT MAX({colname}) FROM {tname})",
                "nivel": "dificil"
            })
    
    return pares


def template_with(tablas):
    pares = []
    for tname, tinfo in tablas.items():
        fks = tinfo.get("foreign_keys", [])
        cols_num = [c for c in tinfo["columnas"] if "DECIMAL" in c["tipo"].upper() or "INT" in c["tipo"].upper()]
        
        for fk in fks:
            tabla_ref = fk["tabla_ref"]
            ref_info = tablas.get(tabla_ref, {})
            ref_cols = [c["nombre"] for c in ref_info.get("columnas", [])]
            col_legible = next((c for c in ref_cols if "nombre" in c.lower()), ref_cols[1] if len(ref_cols) > 1 else ref_cols[0] if ref_cols else None)
            
            if col_legible and cols_num:
                col_num = next((c["nombre"] for c in cols_num if "id" not in c["nombre"].lower()), cols_num[0]["nombre"])
                
                pares.append({
                    "pregunta": f"Usando WITH, calcula el total de {col_num} por {tabla_ref.replace('_', ' ')} y muestra solo los que superan el promedio general",
                    "sql": f"WITH totales AS (SELECT r.{col_legible}, SUM(t.{col_num}) AS total FROM {tabla_ref} r JOIN {tname} t ON t.{fk['columna']} = r.{fk['columna_ref']} GROUP BY r.{col_legible}), promedio AS (SELECT AVG(total) AS prom FROM totales) SELECT t.{col_legible}, t.total FROM totales t CROSS JOIN promedio p WHERE t.total > p.prom",
                    "nivel": "dificil"
                })
    
    return pares


def template_ventana(tablas):
    pares = []
    for tname, tinfo in tablas.items():
        cols = tinfo["columnas"]
        col_num = [c for c in cols if "DECIMAL" in c["tipo"].upper()]
        col_fecha = [c for c in cols if "DATE" in c["tipo"].upper()]
        col_fk = [fk["columna"] for fk in tinfo.get("foreign_keys", [])]
        
        if col_num and col_fecha:
            cn = col_num[0]["nombre"]
            cf = col_fecha[0]["nombre"]
            pares.append({
                "pregunta": f"Muestra los registros de {tname.replace('_', ' ')} con su {cn} y el ranking por {cn} usando funciones de ventana",
                "sql": f"SELECT *, RANK() OVER (ORDER BY {cn} DESC) AS ranking FROM {tname}",
                "nivel": "dificil"
            })
            
            if col_fk:
                group_col = col_fk[0]
                pares.append({
                "pregunta": f"Para cada grupo en {tname.replace('_', ' ')}, muestra los registros con el row number usando funciones de ventana",
                "sql": f"SELECT *, ROW_NUMBER() OVER (PARTITION BY {group_col} ORDER BY {cf} DESC) AS rn FROM {tname}",
                "nivel": "dificil"
                })
    
    return pares


# ============================================
# 3. Generar dataset completo
# ============================================

def generar_dataset():
    esquemas = cargar_esquemas()
    todos_los_pares = []
    descartes = []
    
    for nombre, sql in esquemas.items():
        metadata = extraer_metadata(sql)
        
        if not metadata:
            descartes.append({"esquema": nombre, "razon": "No se pudo extraer metadata"})
            continue
        
        print(f"\n=== {nombre} ===")
        print(f"  Tablas: {list(metadata.keys())}")
        
        # Fácil
        pares_facil = []
        pares_facil.extend(template_contar(metadata))
        pares_facil.extend(template_listar_todos(metadata))
        pares_facil.extend(template_filtro_simple(metadata))
        pares_facil.extend(template_fecha(metadata))
        
        # Medio
        pares_medio = []
        pares_medio.extend(template_join(metadata))
        pares_medio.extend(template_agregacion(metadata))
        
        # Difícil
        pairs_dificil = []
        pairs_dificil.extend(template_subconsulta(metadata))
        pairs_dificil.extend(template_with(metadata))
        pairs_dificil.extend(template_ventana(metadata))
        
        # Asignar esquema y agregar
        for p in pares_facil + pares_medio + pairs_dificil:
            p["esquema"] = nombre
            p["peso"] = {"facil": 1, "media": 2, "dificil": 3}[p["nivel"]]
        
        todos_los_pares.extend(pares_facil + pares_medio + pairs_dificil)
        
        print(f"  Fácil: {len(pares_facil)}, Medio: {len(pares_medio)}, Difícil: {len(pairs_dificil)}")
        print(f"  Total: {len(pares_facil) + len(pares_medio) + len(pairs_dificil)}")
    
    # Eliminar duplicados
    vistos = set()
    sin_duplicados = []
    for p in todos_los_pares:
        key = (p["pregunta"], p["sql"])
        if key not in vistos:
            vistos.add(key)
            sin_duplicados.append(p)
    
    duplicados = len(todos_los_pares) - len(sin_duplicados)
    
    # Estadísticas
    facil = sum(1 for p in sin_duplicados if p["nivel"] == "facil")
    medio = sum(1 for p in sin_duplicados if p["nivel"] == "media")
    dificil = sum(1 for p in sin_duplicados if p["nivel"] == "dificil")
    
    print(f"\n{'='*60}")
    print(f"Total pares generados: {len(todos_los_pares)}")
    print(f"Duplicados eliminados: {duplicados}")
    print(f"Pares únicos: {len(sin_duplicados)}")
    print(f"  Fácil: {facil}")
    print(f"  Medio: {medio}")
    print(f"  Difícil: {dificil}")
    
    # Guardar
    output_dir = Path("datos/entrenamiento")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "dataset_completo.json", "w", encoding="utf-8") as f:
        json.dump(sin_duplicados, f, ensure_ascii=False, indent=2)
    
    # Guardar descartes
    descartes_dir = Path("datos/descartes")
    descartes_dir.mkdir(parents=True, exist_ok=True)
    
    reporte = {
        "total_generados": len(todos_los_pares),
        "duplicados": duplicados,
        "validos": len(sin_duplicados),
        "por_nivel": {"facil": facil, "media": medio, "dificil": dificil},
        "descartes": descartes,
        "nota": "Pendientes de validación en MySQL 8.4.10"
    }
    
    with open(descartes_dir / "reporte_descartes.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
    
    return sin_duplicados


if __name__ == "__main__":
    pares = generar_dataset()
    print(f"\nDataset guardado en datos/entrenamiento/dataset_completo.json")
