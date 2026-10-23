"""
evaluar_baseline.py
Evalúa el modelo base (sin adapter) en el dataset de validación propio.
Esto es el punto de comparación para medir la mejora del fine-tuning.
"""
import json
import time
import re
import mysql.connector
from pathlib import Path
from tqdm import tqdm

# Configuración
DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "text2sql",
    "database": "text_to_sql_eval",
    "charset": "utf8mb4"
}

MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"


def generar_sql_baseline(esquema, pregunta, model, tokenizer, max_new_tokens=256):
    """
    Genera SQL usando el modelo base sin adapter.
    """
    prompt = f"""### Esquema de la base de datos:
{esquema.strip()}

### Pregunta:
{pregunta.strip()}

### Consulta MySQL:
"""
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    import torch
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extraer SQL
    if "### Consulta MySQL:" in response:
        sql = response.split("### Consulta MySQL:")[-1].strip()
        sql = sql.split("\n")[0].split("###")[0].strip()
        return sql
    
    return response.strip()


def crear_esquema(cursor, esquema_sql, nombre):
    """Crea las tablas del esquema en la base de datos."""
    # Limpiar comentarios para compatibilidad
    esquema_clean = re.sub(r"\s+COMMENT\s+'[^']*'", "", esquema_sql)
    esquema_clean = re.sub(r"\)\s+COMMENT\s*=\s*'[^']*'", ")", esquema_clean)
    
    # Dividir en statements
    statements = []
    current = []
    for line in esquema_clean.split('\n'):
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


def ejecutar_query(cursor, sql):
    """Ejecuta una query y retorna el resultado."""
    try:
        cursor.execute(sql)
        columnas = [desc[0] for desc in cursor.description] if cursor.description else []
        filas = cursor.fetchmany(10)
        return {"ok": True, "columnas": columnas, "filas": filas, "error": None}
    except mysql.connector.Error as e:
        return {"ok": False, "columnas": [], "filas": [], "error": str(e)}


def main():
    print("=" * 60)
    print("EVALUACIÓN BASELINE (MODELO SIN ADAPTER)")
    print("=" * 60)
    print(f"Modelo: {MODEL_NAME}")
    print()
    
    # Importar dependencias de transformers
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    
    # Cargar modelo
    print("Cargando modelo base...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    model.eval()
    print("✓ Modelo cargado")
    print()
    
    # Cargar dataset de validación
    with open("datos/validacion/validacion.json", 'r', encoding='utf-8') as f:
        val_data = json.load(f)
    
    # Conectar a MySQL
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except mysql.connector.Error as e:
        print(f"⚠ No se pudo conectar a MySQL: {e}")
        print("La evaluación por ejecución se omitirá")
        conn = None
    
    resultados = []
    total_preguntas = sum(len(schema['preguntas']) for schema in val_data)
    
    print(f"Evaluando {total_preguntas} preguntas en {len(val_data)} esquemas...\n")
    
    for schema_data in val_data:
        nombre = schema_data['name']
        esquema = schema_data['esquema']
        preguntas = schema_data['preguntas']
        
        print(f"--- {nombre} ({len(preguntas)} preguntas) ---")
        
        # Crear tablas si hay conexión
        if conn:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("SHOW TABLES")
            for table in cursor.fetchall():
                cursor.execute(f"DROP TABLE IF EXISTS `{table[0]}`")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            try:
                crear_esquema(cursor, esquema, nombre)
            except Exception as e:
                print(f"  ⚠ Error creando tablas: {e}")
                continue
        
        # Evaluar cada pregunta
        for pregunta_data in tqdm(preguntas, desc=nombre):
            pregunta = pregunta_data['question']
            sql_ref = pregunta_data['sql']
            nivel = pregunta_data['level']
            
            inicio = time.time()
            sql_gen = generar_sql_baseline(esquema, pregunta, model, tokenizer)
            tiempo = time.time() - inicio
            
            # Comparar resultados si hay conexión
            exactitud = False
            if conn and sql_gen:
                try:
                    res_gen = ejecutar_query(cursor, sql_gen)
                    res_ref = ejecutar_query(cursor, sql_ref)
                    
                    if res_gen['ok'] and res_ref['ok']:
                        # Comparar resultados (orden no importa)
                        filas_gen = sorted([tuple(
                            round(float(x), 2) if isinstance(x, float) else x 
                            for x in f
                        ) for f in res_gen['filas']])
                        filas_ref = sorted([tuple(
                            round(float(x), 2) if isinstance(x, float) else x 
                            for x in f
                        ) for f in res_ref['filas']])
                        exactitud = filas_gen == filas_ref
                except Exception:
                    pass
            
            resultados.append({
                'esquema': nombre,
                'pregunta': pregunta,
                'nivel': nivel,
                'sql_referencia': sql_ref,
                'sql_generada': sql_gen,
                'exacta': exactitud,
                'tiempo': round(tiempo, 2)
            })
    
    if conn:
        cursor.close()
        conn.close()
    
    # Calcular métricas
    print("\n" + "=" * 60)
    print("RESULTADOS BASELINE")
    print("=" * 60)
    
    df = pd.DataFrame(resultados)
    
    # Exactitud total
    ex_total = df['exacta'].mean()
    print(f"\nExactitud total: {ex_total:.4f} ({ex_total*100:.2f}%)")
    
    # Por nivel
    print("\nPor nivel de dificultad:")
    for nivel in ['facil', 'media', 'dificil']:
        mask = df['nivel'] == nivel
        if mask.sum() > 0:
            ex = df[mask]['exacta'].mean()
            print(f"  {nivel}: {ex:.4f} ({ex*100:.2f}%)")
    
    # Guardar resultados
    Path("resultados").mkdir(exist_ok=True)
    df.to_csv("resultados/baseline_results.csv", index=False)
    print(f"\n✓ Resultados guardados en resultados/baseline_results.csv")
    
    # Guardar reporte JSON
    reporte = {
        "modelo": MODEL_NAME,
        "usar_adapter": False,
        "exactitud_total": float(ex_total),
        "por_nivel": {
            nivel: float(df[df['nivel'] == nivel]['exacta'].mean())
            for nivel in ['facil', 'media', 'dificil']
        },
        "total_preguntas": len(resultados)
    }
    
    with open("resultados/baseline_report.json", 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Reporte guardado en resultados/baseline_report.json")
    
    return reporte


if __name__ == "__main__":
    import pandas as pd
    main()
