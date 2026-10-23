"""
experimento_inferencia.py
Experimento de inferencia: Self-correction con la función ejecutar()
Genera SQL, la ejecuta, y si falla, re-genera con el error como contexto.
"""
import json
import time
import re
import mysql.connector
from pathlib import Path
from tqdm import tqdm

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "text2sql",
    "database": "text_to_sql_eval",
    "charset": "utf8mb4"
}


def crear_esquema(cursor, esquema_sql):
    """Crea las tablas del esquema."""
    esquema_clean = re.sub(r"\s+COMMENT\s+'[^']*'", "", esquema_sql)
    esquema_clean = re.sub(r"\)\s+COMMENT\s*=\s*'[^']*'", ")", esquema_clean)
    
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


def generar_sql_sin_correccion(esquema, pregunta, model, tokenizer):
    """Genera SQL sin corrección (1 intento)."""
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
            max_new_tokens=256,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    if "### Consulta MySQL:" in response:
        sql = response.split("### Consulta MySQL:")[-1].strip()
        sql = sql.split("\n")[0].split("###")[0].strip()
        return sql
    
    return response.strip()


def generar_sql_con_correccion(esquema, pregunta, model, tokenizer, ejecutar_fn, max_intentos=3):
    """
    Genera SQL con self-correction: si la query falla, re-genera con el error.
    Hasta max_intentos intentos.
    """
    sql_previa = None
    error_previo = None
    
    for intento in range(max_intentos):
        # Construir prompt
        if intento == 0:
            prompt = f"""### Esquema de la base de datos:
{esquema.strip()}

### Pregunta:
{pregunta.strip()}

### Consulta MySQL:
"""
        else:
            prompt = f"""### Esquema de la base de datos:
{esquema.strip()}

### Pregunta:
{pregunta.strip()}

### Consulta anterior (tiene error):
{sql_previa}

### Error de MySQL:
{error_previo}

### Consulta MySQL corregida:
"""
        
        # Generar SQL
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        import torch
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.1,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "### Consulta MySQL:" in response or "### Consulta MySQL corregida:" in response:
            sql = response.split("### Consulta MySQL")[-1].strip()
            sql = sql.split("\n")[0].split("###")[0].strip()
        else:
            sql = response.strip()
        
        # Ejecutar la query
        resultado = ejecutar_fn(sql)
        
        if resultado['ok']:
            return sql, intento + 1, None
        
        # Guardar para el siguiente intento
        sql_previa = sql
        error_previo = resultado['error']
    
    # Si llegamos aquí, todos los intentos fallaron
    return sql_previa, max_intentos, error_previo


def main():
    print("=" * 60)
    print("EXPERIMENTO DE INFERENCIA: SELF-CORRECTION")
    print("=" * 60)
    print()
    
    # Importar dependencias
    import torch
    import pandas as pd
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel
    
    # Cargar configuración
    with open("config.json", 'r') as f:
        config = json.load(f)
    
    model_name = config['modelo_base']
    adapter_path = config.get('adapter', 'adapter')
    
    print(f"Modelo: {model_name}")
    print(f"Adapter: {adapter_path}")
    print()
    
    # Cargar modelo con adapter
    print("Cargando modelo...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    
    model = PeftModel.from_pretrained(base_model, adapter_path)
    model = model.merge_and_unload()
    model.eval()
    print("✓ Modelo cargado")
    print()
    
    # Cargar dataset de validación
    with open("datos/validacion/validacion.json", 'r', encoding='utf-8') as f:
        val_data = json.load(f)
    
    # Conectar a MySQL
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    resultados_sin = []
    resultados_con = []
    
    total_preguntas = sum(len(schema['preguntas']) for schema in val_data)
    print(f"Experimento en {total_preguntas} preguntas...\n")
    
    for schema_data in val_data:
        nombre = schema_data['name']
        esquema = schema_data['esquema']
        preguntas = schema_data['preguntas']
        
        print(f"--- {nombre} ---")
        
        # Crear tablas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("SHOW TABLES")
        for table in cursor.fetchall():
            cursor.execute(f"DROP TABLE IF EXISTS `{table[0]}`")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        try:
            crear_esquema(cursor, esquema)
        except Exception as e:
            print(f"  ⚠ Error creando tablas: {e}")
            continue
        
        def ejecutar_fn(sql):
            return ejecutar_query(cursor, sql)
        
        # Evaluar cada pregunta
        for pregunta_data in tqdm(preguntas, desc=nombre):
            pregunta = pregunta_data['question']
            sql_ref = pregunta_data['sql']
            nivel = pregunta_data['level']
            
            # Sin corrección (1 intento)
            inicio = time.time()
            sql_sin = generar_sql_sin_correccion(esquema, pregunta, model, tokenizer)
            tiempo_sin = time.time() - inicio
            
            res_sin = ejecutar_fn(sql_sin)
            exacta_sin = False
            if res_sin['ok']:
                try:
                    res_ref = ejecutar_query(cursor, sql_ref)
                    if res_ref['ok']:
                        filas_sin = sorted([tuple(
                            round(float(x), 2) if isinstance(x, float) else x 
                            for x in f
                        ) for f in res_sin['filas']])
                        filas_ref = sorted([tuple(
                            round(float(x), 2) if isinstance(x, float) else x 
                            for x in f
                        ) for f in res_ref['filas']])
                        exacta_sin = filas_sin == filas_ref
                except:
                    pass
            
            resultados_sin.append({
                'esquema': nombre,
                'pregunta': pregunta,
                'nivel': nivel,
                'sql_generada': sql_sin,
                'exacta': exacta_sin,
                'tiempo': round(tiempo_sin, 2),
                'intentos': 1
            })
            
            # Con corrección (hasta 3 intentos)
            inicio = time.time()
            sql_con, intentos, error = generar_sql_con_correccion(
                esquema, pregunta, model, tokenizer, ejecutar_fn, max_intentos=3
            )
            tiempo_con = time.time() - inicio
            
            res_con = ejecutar_fn(sql_con)
            exacta_con = False
            if res_con['ok']:
                try:
                    res_ref = ejecutar_query(cursor, sql_ref)
                    if res_ref['ok']:
                        filas_con = sorted([tuple(
                            round(float(x), 2) if isinstance(x, float) else x 
                            for x in f
                        ) for f in res_con['filas']])
                        filas_ref = sorted([tuple(
                            round(float(x), 2) if isinstance(x, float) else x 
                            for x in f
                        ) for f in res_ref['filas']])
                        exacta_con = filas_con == filas_ref
                except:
                    pass
            
            resultados_con.append({
                'esquema': nombre,
                'pregunta': pregunta,
                'nivel': nivel,
                'sql_generada': sql_con,
                'exacta': exacta_con,
                'tiempo': round(tiempo_con, 2),
                'intentos': intentos
            })
    
    cursor.close()
    conn.close()
    
    # Análisis
    print("\n" + "=" * 60)
    print("RESULTADOS DEL EXPERIMENTO")
    print("=" * 60)
    
    df_sin = pd.DataFrame(resultados_sin)
    df_con = pd.DataFrame(resultados_con)
    
    ex_sin = df_sin['exacta'].mean()
    ex_con = df_con['exacta'].mean()
    
    print(f"\nSin self-correction:")
    print(f"  Exactitud: {ex_sin:.4f} ({ex_sin*100:.2f}%)")
    print(f"  Tiempo promedio: {df_sin['tiempo'].mean():.2f}s")
    
    print(f"\nCon self-correction (hasta 3 intentos):")
    print(f"  Exactitud: {ex_con:.4f} ({ex_con*100:.2f}%)")
    print(f"  Tiempo promedio: {df_con['tiempo'].mean():.2f}s")
    print(f"  Intentos promedio: {df_con['intentos'].mean():.2f}")
    
    mejora = ex_con - ex_sin
    print(f"\nMejora por self-correction: {mejora:+.4f} ({mejora*100:+.2f}%)")
    
    # Guardar resultados
    Path("resultados").mkdir(exist_ok=True)
    
    df_sin.to_csv("resultados/inferencia_sin_correccion.csv", index=False)
    df_con.to_csv("resultados/inferencia_con_correccion.csv", index=False)
    
    print(f"\n✓ Resultados guardados en resultados/")
    
    # Reporte
    reporte = {
        "experimento": "self-correction",
        "sin_correccion": {
            "exactitud": float(ex_sin),
            "tiempo_promedio": float(df_sin['tiempo'].mean())
        },
        "con_correccion": {
            "exactitud": float(ex_con),
            "tiempo_promedio": float(df_con['tiempo'].mean()),
            "intentos_promedio": float(df_con['intentos'].mean())
        },
        "mejora": float(mejora)
    }
    
    with open("resultados/experimento_inferencia.json", 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Reporte guardado en resultados/experimento_inferencia.json")


if __name__ == "__main__":
    main()
