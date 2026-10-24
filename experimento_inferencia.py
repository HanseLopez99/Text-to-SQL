"""
Experimento de Inferencia: Self-Correction con MySQL
Genera SQL, la ejecuta, y si hay error, re-genera con el error como contexto
"""
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import mysql.connector
from tqdm import tqdm
import time

print("=" * 60)
print("EXPERIMENTO DE INFERENCIA: SELF-CORRECTION")
print("=" * 60)

# Configuración
with open('config.json', 'r') as f:
    config = json.load(f)

MODELO_BASE = config['modelo_base']
ADAPTER_PATH = config['adapter']

print(f"Modelo base: {MODELO_BASE}")
print(f"Adapter: {ADAPTER_PATH}")

# Cargar modelo fine-tuned
print("\nCargando modelo fine-tuned...")
device = 'mps' if torch.backends.mps.is_available() else 'cpu'
print(f"Dispositivo: {device}")

tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODELO_BASE,
    dtype=torch.float32 if device == 'mps' else torch.float16,
    device_map=None,
    trust_remote_code=True
).to(device)

model = PeftModel.from_pretrained(model, ADAPTER_PATH)
model = model.merge_and_unload()
model.eval()
print("✓ Modelo cargado")

# Conexión MySQL
def conectar_mysql():
    return mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="text2sql",
        database="text_to_sql_eval"
    )

def setup_esquema(cursor, esquema_sql):
    """Configura el esquema en MySQL"""
    # Limpiar tablas existentes
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("SHOW TABLES")
    for (table,) in cursor.fetchall():
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    # Crear tablas
    for statement in esquema_sql.split(';'):
        if statement.strip():
            try:
                cursor.execute(statement)
            except Exception as e:
                pass  # Ignorar errores de sintaxis en comentarios

def generar_sql(model, tokenizer, esquema, pregunta, device, contexto_error=None):
    """Genera SQL, opcionalmente con contexto de error previo"""
    if contexto_error:
        prompt = f"""### Esquema de la base de datos:
{esquema}

### Pregunta:
{pregunta}

### Consulta SQL anterior (tiene error):
{contexto_error['sql_previa']}

### Error de MySQL:
{contexto_error['error']}

### Genera una consulta SQL corregida:"""
    else:
        prompt = f"""### Esquema de la base de datos:
{esquema}

### Pregunta:
{pregunta}

### Consulta SQL:"""
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extraer SQL
    sql = generated_text.split("###")[-1].strip()
    sql = sql.split('\n')[0].strip()
    return sql

def ejecutar_query(cursor, sql):
    """Ejecuta una query y retorna resultado"""
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return True, rows, columns, None
    except Exception as e:
        return False, [], [], str(e)

def comparar_resultados(rows1, rows2):
    """Compara dos conjuntos de resultados"""
    set1 = set(tuple(row) for row in rows1)
    set2 = set(tuple(row) for row in rows2)
    return set1 == set2

# Cargar dataset de validación
print("\nCargando dataset de validación...")
with open('datos/validacion/validacion.json', 'r') as f:
    dataset = json.load(f)

print(f"✓ {len(dataset)} esquemas cargados")

# Experimento: Comparar sin self-correction vs con self-correction
resultados_sin_corr = []
resultados_con_corr = []

for esquema_data in tqdm(dataset, desc="Esquemas"):
    esquema_nombre = esquema_data['nombre']
    esquema_sql = esquema_data['esquema']
    
    conn = conectar_mysql()
    cursor = conn.cursor()
    setup_esquema(cursor, esquema_sql)
    conn.commit()
    
    for pregunta_data in tqdm(esquema_data['preguntas'], desc=f"{esquema_nombre}", leave=False):
        pregunta = pregunta_data['pregunta']
        sql_referencia = pregunta_data['sql']
        peso = pregunta_data['peso']
        nivel = pregunta_data['nivel']
        
        # Ejecutar query de referencia
        ok_ref, rows_ref, cols_ref, _ = ejecutar_query(cursor, sql_referencia)
        
        # ===== SIN SELF-CORRECTION (1 intento) =====
        inicio = time.time()
        sql_sin = generar_sql(model, tokenizer, esquema_sql, pregunta, device)
        tiempo_sin = time.time() - inicio
        
        ok_sin, rows_sin, cols_sin, err_sin = ejecutar_query(cursor, sql_sin)
        
        correcta_sin = False
        if ok_ref and ok_sin:
            correcta_sin = comparar_resultados(rows_ref, rows_sin)
        
        resultados_sin_corr.append({
            'esquema': esquema_nombre,
            'pregunta': pregunta,
            'nivel': nivel,
            'peso': peso,
            'sql_generada': sql_sin,
            'correcta': correcta_sin,
            'tiempo': tiempo_sin,
            'intentos': 1
        })
        
        # ===== CON SELF-CORRECTION (hasta 3 intentos) =====
        inicio = time.time()
        sql_con = None
        correcta_con = False
        intentos = 0
        contexto_error = None
        
        for intento in range(3):
            intentos += 1
            sql_con = generar_sql(model, tokenizer, esquema_sql, pregunta, device, contexto_error)
            ok_con, rows_con, cols_con, err_con = ejecutar_query(cursor, sql_con)
            
            if ok_ref and ok_con:
                correcta_con = comparar_resultados(rows_ref, rows_con)
                if correcta_con:
                    break  # Éxito, no necesitamos más intentos
            
            # Preparar contexto para siguiente intento
            contexto_error = {
                'sql_previa': sql_con,
                'error': err_con if err_con else "Resultado incorrecto"
            }
        
        tiempo_con = time.time() - inicio
        
        resultados_con_corr.append({
            'esquema': esquema_nombre,
            'pregunta': pregunta,
            'nivel': nivel,
            'peso': peso,
            'sql_generada': sql_con,
            'correcta': correcta_con,
            'tiempo': tiempo_con,
            'intentos': intentos
        })
    
    conn.close()

# Calcular métricas
def calcular_ex(resultados):
    """Calcula EX Score (exactitud ponderada)"""
    peso_correcto = sum(r['peso'] for r in resultados if r['correcta'])
    peso_total = sum(r['peso'] for r in resultados)
    return peso_correcto / peso_total if peso_total > 0 else 0

ex_sin_corr = calcular_ex(resultados_sin_corr)
ex_con_corr = calcular_ex(resultados_con_corr)

print("\n" + "=" * 60)
print("RESULTADOS DEL EXPERIMENTO")
print("=" * 60)
print(f"\nSin self-correction (1 intento):")
print(f"  EX Score: {ex_sin_corr:.4f}")
print(f"  Tiempo promedio: {sum(r['tiempo'] for r in resultados_sin_corr)/len(resultados_sin_corr):.2f}s")

print(f"\nCon self-correction (hasta 3 intentos):")
print(f"  EX Score: {ex_con_corr:.4f}")
print(f"  Tiempo promedio: {sum(r['tiempo'] for r in resultados_con_corr)/len(resultados_con_corr):.2f}s")
print(f"  Intentos promedio: {sum(r['intentos'] for r in resultados_con_corr)/len(resultados_con_corr):.2f}")

print(f"\nMejora por self-correction: {ex_con_corr - ex_sin_corr:+.4f}")

# Guardar resultados
import pandas as pd

df_sin = pd.DataFrame(resultados_sin_corr)
df_con = pd.DataFrame(resultados_con_corr)

df_sin.to_csv('resultados/experimento_sin_correccion.csv', index=False)
df_con.to_csv('resultados/experimento_con_correccion.csv', index=False)

experimento = {
    'sin_self_correction': {
        'ex_score': ex_sin_corr,
        'tiempo_promedio': sum(r['tiempo'] for r in resultados_sin_corr)/len(resultados_sin_corr)
    },
    'con_self_correction': {
        'ex_score': ex_con_corr,
        'tiempo_promedio': sum(r['tiempo'] for r in resultados_con_corr)/len(resultados_con_corr),
        'intentos_promedio': sum(r['intentos'] for r in resultados_con_corr)/len(resultados_con_corr)
    },
    'mejora': ex_con_corr - ex_sin_corr
}

with open('resultados/experimento_inferencia.json', 'w') as f:
    json.dump(experimento, f, indent=2)

print(f"\n✓ Resultados guardados en:")
print(f"  - resultados/experimento_sin_correccion.csv")
print(f"  - resultados/experimento_con_correccion.csv")
print(f"  - resultados/experimento_inferencia.json")
