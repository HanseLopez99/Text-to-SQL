"""
evaluar.py - Evalúa el modelo en el dataset de validación propio.
"""

import json
import csv
import time
import mysql.connector
import pandas as pd
from tqdm import tqdm
from solucion import generar_sql, cargar_modelo, cargar_config


def crearConexionMySQL():
    """Crea una conexión a MySQL."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="text_to_sql_eval",
        charset="utf8mb4"
    )


def ejecutar_query(conn, sql):
    """
    Ejecuta una query en MySQL y retorna el resultado.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columnas = [desc[0] for desc in cursor.description] if cursor.description else []
        filas = cursor.fetchmany(10)
        cursor.close()
        return {"ok": True, "columnas": columnas, "filas": filas, "error": None}
    except Exception as e:
        return {"ok": False, "columnas": [], "filas": [], "error": str(e)}


def cargar_dataset_validacion(path="datos/validacion/validacion.json"):
    """Carga el dataset de validación."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluar(esquema_sql, preguntas, conn, usar_ejecutar=True):
    """
    Evalúa el modelo en un esquema dado.
    """
    resultados = []

    def ejecutar_fn(sql):
        if usar_ejecutar:
            return ejecutar_query(conn, sql)
        return None

    for item in tqdm(preguntas, desc="Evaluando"):
        pregunta = item["pregunta"]
        sql_referencia = item["sql"]
        peso = item.get("peso", 1)
        nivel = item.get("nivel", "facil")

        inicio = time.time()
        try:
            sql_generada = generar_sql(esquema_sql, pregunta,
                                       ejecutar=ejecutar_fn if usar_ejecutar else None)
        except Exception as e:
            sql_generada = ""
            print(f"  Error generando SQL: {e}")
        tiempo = time.time() - inicio

        # Evaluar exactitud por ejecución
        acertada = False
        if sql_generada:
            try:
                res_generada = ejecutar_query(conn, sql_generada)
                res_referencia = ejecutar_query(conn, sql_referencia)

                if res_generada["ok"] and res_referencia["ok"]:
                    # Comparar resultados (orden no importa salvo que se pida)
                    filas_gen = sorted([tuple(
                        round(float(x), 2) if isinstance(x, float) else x for x in f
                    ) for f in res_generada["filas"]])
                    filas_ref = sorted([tuple(
                        round(float(x), 2) if isinstance(x, float) else x for x in f
                    ) for f in res_referencia["filas"]])
                    acertada = filas_gen == filas_ref
            except Exception:
                acertada = False

        resultados.append({
            "pregunta": pregunta,
            "nivel": nivel,
            "peso": peso,
            "sql_generada": sql_generada,
            "sql_referencia": sql_referencia,
            "acertada": acertada,
            "tiempo_seg": round(tiempo, 2)
        })

    return resultados


def calcular_ex(resultados):
    """Calcula la exactitud ponderada (EX)."""
    if not resultados:
        return 0.0
    peso_acertado = sum(r["peso"] for r in resultados if r["acertada"])
    peso_total = sum(r["peso"] for r in resultados)
    return peso_acertado / peso_total if peso_total > 0 else 0.0


def main():
    print("=" * 60)
    print("Evaluación en validación propia")
    print("=" * 60)

    config = cargar_config()
    print(f"Modelo: {config['modelo_base']}")
    print(f"Usar adapter: {config['usar_adapter']}")

    print("\nCargando modelo...")
    cargar_modelo(config)
    print("Modelo cargado.")

    dataset = cargar_dataset_validacion()

    todos_resultados = []

    for esquema_data in dataset:
        nombre = esquema_data["nombre"]
        esquema_sql = esquema_data["esquema"]
        preguntas = esquema_data["preguntas"]

        print(f"\n--- Evaluando esquema: {nombre} ---")

        conn = crearConexionMySQL()
        try:
            resultados = evaluar(esquema_sql, preguntas, conn)
            ex = calcular_ex(resultados)
            print(f"  EX para {nombre}: {ex:.4f}")
            todos_resultados.extend(resultados)
        finally:
            conn.close()

    ex_total = calcular_ex(todos_resultados)
    print(f"\n{'=' * 60}")
    print(f"EX TOTAL: {ex_total:.4f}")
    print(f"{'=' * 60}")

    # Guardar resultados
    df = pd.DataFrame(todos_resultados)
    df.to_csv("resultados/validacion_propia.csv", index=False)
    print(f"Resultados guardados en resultados/validacion_propia.csv")

    # Resumen por nivel
    for nivel in ["facil", "media", "dificil"]:
        nivel_res = [r for r in todos_resultados if r["nivel"] == nivel]
        if nivel_res:
            ex_nivel = calcular_ex(nivel_res)
            acertadas = sum(1 for r in nivel_res if r["acertada"])
            print(f"  {nivel}: {acertadas}/{len(nivel_res)} correctas (EX={ex_nivel:.4f})")


if __name__ == "__main__":
    main()
