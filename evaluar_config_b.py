"""
Evaluación de Config B (rank=32)
Compara con Config A (rank=16) y baseline
"""
import json
import torch
import mysql.connector
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from tqdm import tqdm
import pandas as pd

print("=" * 60)
print("EVALUACIÓN CONFIG B (rank=32)")
print("=" * 60)

# Configuración
with open('config.json', 'r') as f:
    config = json.load(f)

MODELO_BASE = config['modelo_base']
ADAPTER_PATH = 'adapter_config_b'

print(f"Modelo base: {MODELO_BASE}")
print(f"Adapter Config B: {ADAPTER_PATH}")

# Cargar modelo Config B
print("\nCargando modelo Config B...")
device = 'mps' if torch.backends.mps.is_available() else 'cpu'

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
print("✓ Modelo Config B cargado")

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
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("SHOW TABLES")
    for (table,) in cursor.fetchall():
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    for statement in esquema_sql.split(';'):
        if statement.strip():
            try:
                cursor.execute(statement)
            except:
                pass

def generar_sql(model, tokenizer, esquema, pregunta, device):
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
    sql = generated_text.split("###")[-1].strip()
    sql = sql.split('\n')[0].strip()
    return sql

def ejecutar_query(cursor, sql):
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return True, rows, columns, None
    except Exception as e:
        return False, [], [], str(e)

def comparar_resultados(rows1, rows2):
    set1 = set(tuple(row) for row in rows1)
    set2 = set(tuple(row) for row in rows2)
    return set1 == set2

# Cargar dataset de validación
print("\nCargando dataset de validación...")
with open('datos/validacion/validacion.json', 'r') as f:
    dataset = json.load(f)

# Evaluar Config B
resultados = []

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
        
        # Generar SQL con Config B
        sql_generada = generar_sql(model, tokenizer, esquema_sql, pregunta, device)
        ok_gen, rows_gen, cols_gen, err_gen = ejecutar_query(cursor, sql_generada)
        
        # Comparar resultados
        correcta = False
        if ok_ref and ok_gen:
            correcta = comparar_resultados(rows_ref, rows_gen)
        
        resultados.append({
            'esquema': esquema_nombre,
            'pregunta': pregunta,
            'nivel': nivel,
            'peso': peso,
            'sql_referencia': sql_referencia,
            'sql_generada': sql_generada,
            'correcta': correcta,
            'error': err_gen
        })
    
    conn.close()

# Calcular EX Score
peso_correcto = sum(r['peso'] for r in resultados if r['correcta'])
peso_total = sum(r['peso'] for r in resultados)
ex_score = peso_correcto / peso_total if peso_total > 0 else 0

print("\n" + "=" * 60)
print("RESULTADOS CONFIG B")
print("=" * 60)
print(f"EX Score: {ex_score:.4f}")
print(f"Preguntas correctas: {sum(1 for r in resultados if r['correcta'])}/{len(resultados)}")

# Por nivel
for nivel in ['facil', 'medio', 'dificil']:
    preguntas_nivel = [r for r in resultados if r['nivel'] == nivel]
    if preguntas_nivel:
        correctas = sum(1 for r in preguntas_nivel if r['correcta'])
        ex_nivel = sum(r['peso'] for r in preguntas_nivel if r['correcta']) / sum(r['peso'] for r in preguntas_nivel)
        print(f"  {nivel}: {correctas}/{len(preguntas_nivel)} (EX: {ex_nivel:.4f})")

# Guardar resultados
df = pd.DataFrame(resultados)
df.to_csv('resultados/config_b_results.csv', index=False)

config_b_result = {
    'config': 'B',
    'rank': 32,
    'lora_alpha': 64,
    'ex_score': ex_score,
    'preguntas_correctas': sum(1 for r in resultados if r['correcta']),
    'total_preguntas': len(resultados)
}

with open('resultados/config_b_report.json', 'w') as f:
    json.dump(config_b_result, f, indent=2)

# Comparar con Config A
try:
    with open('resultados/comparacion_final.json', 'r') as f:
        comparacion = json.load(f)
    
    with open('resultados/metricas_entrenamiento.json', 'r') as f:
        config_a = json.load(f)
    
    with open('resultados/metricas_config_b.json', 'r') as f:
        config_b = json.load(f)
    
    print("\n" + "=" * 60)
    print("COMPARACIÓN: BASELINE vs CONFIG A vs CONFIG B")
    print("=" * 60)
    print(f"Baseline (sin adapter):")
    print(f"  EX Score: {comparacion['baseline']['ex_score']:.4f}")
    print(f"\nConfig A (rank=16):")
    print(f"  EX Score: {comparacion['finetuned']['ex_score']:.4f}")
    print(f"  Loss final: {config_a['loss_final']:.4f}")
    print(f"  Parámetros: {config_a['parametros_entrenables']:,}")
    print(f"\nConfig B (rank=32):")
    print(f"  EX Score: {config_b_result['ex_score']:.4f}")
    print(f"  Loss final: {config_b['loss_final']:.4f}")
    print(f"  Parámetros: {config_b['parametros_entrenables']:,}")
    
    # Guardar comparación completa
    comparacion_completa = {
        'baseline': comparacion['baseline'],
        'config_a': {
            'rank': 16,
            'ex_score': comparacion['finetuned']['ex_score'],
            'loss_final': config_a['loss_final'],
            'parametros': config_a['parametros_entrenables']
        },
        'config_b': config_b_result
    }
    
    with open('resultados/comparacion_completa.json', 'w') as f:
        json.dump(comparacion_completa, f, indent=2)
    
    print(f"\n✓ Comparación completa guardada en: resultados/comparacion_completa.json")
    
except Exception as e:
    print(f"\n⚠ No se pudo cargar comparación: {e}")

print(f"\n✓ Resultados guardados en:")
print(f"  - resultados/config_b_results.csv")
print(f"  - resultados/config_b_report.json")
