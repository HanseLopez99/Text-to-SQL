"""
expandir_dataset.py - Genera variaciones adicionales de pares pregunta-SQL
Usando paráfrasis y diferentes formulaciones de las mismas queries
"""

import json
import random
from pathlib import Path

random.seed(2026)

def cargar_dataset():
    with open("datos/entrenamiento/dataset_completo.json", "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_esquemas():
    esquemas = {}
    for f in Path("datos/esquemas/entrenamiento").glob("*.sql"):
        esquemas[f.stem] = f.read_text()
    return esquemas

# Parámetros de variación
VARIACIONES_PREGUNTA = {
    "contar": [
        "¿Cuántos {entidad} hay?",
        "Dime la cantidad de {entidad}",
        "Necesito saber el número de {entidad}",
        "¿Cuál es el total de {entidad}?",
        "¿Cuántos registros de {entidad} existen?",
    ],
    "listar": [
        "Muestra todos los {entidad}",
        "Lista los {entidad}",
        "Dame todos los {entidad}",
        "Quiero ver los {entidad}",
        "Muéstrame el listado de {entidad}",
    ],
    "filtro": [
        "¿Cuáles {entidad} tienen {condicion}?",
        "Muéstrame los {entidad} con {condicion}",
        "Necesito los {entidad} donde {condicion}",
        "Dame los {entidad} que cumplen {condicion}",
    ],
    "maximo": [
        "¿Cuál es el {campo} máximo?",
        "¿Cuál es el valor más alto de {campo}?",
        "¿Cuál es el {campo} más grande?",
        "Dime el {campo} máximo",
    ],
    "minimo": [
        "¿Cuál es el {campo} mínimo?",
        "¿Cuál es el valor más bajo de {campo}?",
        "¿Cuál es el {campo} más pequeño?",
        "Dime el {campo} mínimo",
    ],
    "promedio": [
        "¿Cuál es el promedio de {campo}?",
        "Calcula el promedio de {campo}",
        "Dime el valor promedio de {campo}",
        "¿Cuál es la media de {campo}?",
    ],
}

def generar_variaciones(pares_existentes):
    """Genera variaciones de preguntas manteniendo la misma SQL"""
    nuevas_preguntas = []
    
    for par in pares_existentes:
        sql = par["sql"].lower()
        pregunta_original = par["pregunta"]
        nivel = par["nivel"]
        esquema = par["esquema"]
        peso = par["peso"]
        
        # Detectar tipo de query
        if "count(*)" in sql or "count(id)" in sql:
            # Queries de conteo
            for variacion in random.sample(VARIACIONES_PREGUNTA["contar"], min(3, len(VARIACIONES_PREGUNTA["contar"]))):
                nueva_pregunta = variacion.format(entidad=esquema.replace("_", " "))
                if nueva_pregunta != pregunta_original:
                    nuevas_preguntas.append({
                        "pregunta": nueva_pregunta,
                        "sql": par["sql"],
                        "nivel": nivel,
                        "esquema": esquema,
                        "peso": peso
                    })
        
        elif "select *" in sql and "where" not in sql:
            # Queries de listar todo
            for variacion in random.sample(VARIACIONES_PREGUNTA["listar"], min(3, len(VARIACIONES_PREGUNTA["listar"]))):
                nueva_pregunta = variacion.format(entidad=esquema.replace("_", " "))
                if nueva_pregunta != pregunta_original:
                    nuevas_preguntas.append({
                        "pregunta": nueva_pregunta,
                        "sql": par["sql"],
                        "nivel": nivel,
                        "esquema": esquema,
                        "peso": peso
                    })
        
        elif "max(" in sql:
            # Queries de máximo
            # Extraer nombre de campo del SQL
            import re
            match = re.search(r'max\((\w+)\)', sql)
            if match:
                campo = match.group(1)
                for variacion in random.sample(VARIACIONES_PREGUNTA["maximo"], min(2, len(VARIACIONES_PREGUNTA["maximo"]))):
                    nueva_pregunta = variacion.format(campo=campo)
                    if nueva_pregunta != pregunta_original:
                        nuevas_preguntas.append({
                            "pregunta": nueva_pregunta,
                            "sql": par["sql"],
                            "nivel": nivel,
                            "esquema": esquema,
                            "peso": peso
                        })
        
        elif "min(" in sql:
            # Queries de mínimo
            import re
            match = re.search(r'min\((\w+)\)', sql)
            if match:
                campo = match.group(1)
                for variacion in random.sample(VARIACIONES_PREGUNTA["minimo"], min(2, len(VARIACIONES_PREGUNTA["minimo"]))):
                    nueva_pregunta = variacion.format(campo=campo)
                    if nueva_pregunta != pregunta_original:
                        nuevas_preguntas.append({
                            "pregunta": nueva_pregunta,
                            "sql": par["sql"],
                            "nivel": nivel,
                            "esquema": esquema,
                            "peso": peso
                        })
        
        elif "avg(" in sql:
            # Queries de promedio
            import re
            match = re.search(r'avg\((\w+)\)', sql)
            if match:
                campo = match.group(1)
                for variacion in random.sample(VARIACIONES_PREGUNTA["promedio"], min(2, len(VARIACIONES_PREGUNTA["promedio"]))):
                    nueva_pregunta = variacion.format(campo=campo)
                    if nueva_pregunta != pregunta_original:
                        nuevas_preguntas.append({
                            "pregunta": nueva_pregunta,
                            "sql": par["sql"],
                            "nivel": nivel,
                            "esquema": esquema,
                            "peso": peso
                        })
    
    return nuevas_preguntas

def generar_queries_adicionales(esquemas):
    """Genera queries adicionales específicas para cada esquema"""
    nuevas_queries = []
    
    for nombre, sql in esquemas.items():
        # Extraer tablas y columnas
        import re
        tablas = re.findall(r'CREATE TABLE (\w+)', sql)
        
        for tabla in tablas:
            # Queries de ORDER BY con LIMIT
            nuevas_queries.append({
                "pregunta": f"Muestra los 10 primeros registros de {tabla} ordenados por id",
                "sql": f"SELECT * FROM {tabla} ORDER BY id LIMIT 10",
                "nivel": "facil",
                "esquema": nombre,
                "peso": 1
            })
            
            # Queries de DISTINCT
            nuevas_queries.append({
                "pregunta": f"¿Qué valores únicos existen en la primera columna de {tabla}?",
                "sql": f"SELECT DISTINCT * FROM {tabla} LIMIT 20",
                "nivel": "facil",
                "esquema": nombre,
                "peso": 1
            })
            
            # Queries con WHERE simple
            nuevas_queries.append({
                "pregunta": f"Muestra el primer registro de {tabla}",
                "sql": f"SELECT * FROM {tabla} LIMIT 1",
                "nivel": "facil",
                "esquema": nombre,
                "peso": 1
            })
            
            # Queries de agregación básicas
            nuevas_queries.append({
                "pregunta": f"¿Cuántos registros hay en {tabla}?",
                "sql": f"SELECT COUNT(*) FROM {tabla}",
                "nivel": "facil",
                "esquema": nombre,
                "peso": 1
            })
            
            # Queries con GROUP BY simples
            if len(tablas) > 1:
                otra_tabla = random.choice([t for t in tablas if t != tabla])
                nuevas_queries.append({
                    "pregunta": f"¿Cuántos {tabla} hay por cada {otra_tabla}?",
                    "sql": f"SELECT {otra_tabla}.id, COUNT({tabla}.id) FROM {tabla} JOIN {otra_tabla} ON {tabla}.id = {otra_tabla}.id GROUP BY {otra_tabla}.id LIMIT 10",
                    "nivel": "media",
                    "esquema": nombre,
                    "peso": 2
                })
    
    return nuevas_queries

def main():
    print("Cargando dataset existente...")
    pares_existentes = cargar_dataset()
    print(f"Pares existentes: {len(pares_existentes)}")
    
    print("\nGenerando variaciones...")
    variaciones = generar_variaciones(pares_existentes)
    print(f"Variaciones generadas: {len(variaciones)}")
    
    print("\nGenerando queries adicionales...")
    esquemas = cargar_esquemas()
    adicionales = generar_queries_adicionales(esquemas)
    print(f"Queries adicionales: {len(adicionales)}")
    
    # Combinar todo
    dataset_completo = pares_existentes + variaciones + adicionales
    
    # Eliminar duplicados
    vistos = set()
    sin_duplicados = []
    for par in dataset_completo:
        key = (par["pregunta"], par["sql"])
        if key not in vistos:
            vistos.add(key)
            sin_duplicados.append(par)
    
    # Estadísticas
    facil = sum(1 for p in sin_duplicados if p["nivel"] == "facil")
    medio = sum(1 for p in sin_duplicados if p["nivel"] == "media")
    dificil = sum(1 for p in sin_duplicados if p["nivel"] == "dificil")
    
    print(f"\n{'='*60}")
    print(f"Dataset expandido:")
    print(f"Total pares: {len(sin_duplicados)}")
    print(f"  Fácil: {facil}")
    print(f"  Medio: {medio}")
    print(f"  Difícil: {dificil}")
    
    # Guardar
    with open("datos/entrenamiento/dataset_completo.json", "w", encoding="utf-8") as f:
        json.dump(sin_duplicados, f, ensure_ascii=False, indent=2)
    
    print(f"\nDataset actualizado en datos/entrenamiento/dataset_completo.json")

if __name__ == "__main__":
    main()
