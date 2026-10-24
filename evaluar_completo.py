"""
Evaluación completa: baseline vs modelo fine-tuned
Evalúa ambos modelos en el dataset de validación propio contra MySQL
"""
import json
import torch
import mysql.connector
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from tqdm import tqdm
import pandas as pd
import time

# Configuración
CONFIG_PATH = "config.json"
VALIDACION_PATH = "datos/validacion/validacion.json"
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "text2sql",
    "database": "text_to_sql_eval"
}

def cargar_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def cargar_dataset_validacion():
    with open(VALIDACION_PATH, 'r') as f:
        return json.load(f)

def setup_mysql(esquema_sql):
    """Configura MySQL con el esquema dado"""
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    # Limpiar tablas existentes
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("SHOW TABLES")
    for (table,) in cursor.fetchall():
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    # Crear tablas del esquema
    for statement in esquema_sql.split(';'):
        if statement.strip():
            try:
                cursor.execute(statement)
            except Exception as e:
                print(f"Error creando tabla: {e}")
    
    conn.commit()
    return conn, cursor

def ejecutar_query(cursor, sql):
    """Ejecuta una query y retorna resultados"""
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return True, rows, columns, None
    except Exception as e:
        return False, [], [], str(e)

def generar_sql(modelo, tokenizer, esquema, pregunta, device):
    """Genera SQL usando el modelo"""
    prompt = f"""### Esquema de la base de datos:
{esquema}

### Pregunta:
{pregunta}

### SQL:"""
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)
    
    with torch.no_grad():
        outputs = modelo.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extraer solo la parte SQL
    if "### SQL:" in generated_text:
        sql = generated_text.split("### SQL:")[-1].strip()
        # Tomar solo la primera línea o hasta el próximo ###
        sql = sql.split('\n')[0].split('###')[0].strip()
        return sql
    
    return generated_text.strip()

def comparar_resultados(rows1, rows2):
    """Compara si dos conjuntos de resultados son equivalentes"""
    # Convertir a sets de tuples para comparación independiente del orden
    set1 = set(tuple(row) for row in rows1)
    set2 = set(tuple(row) for row in rows2)
    return set1 == set2

def evaluar_modelo(modelo, tokenizer, device, nombre_modelo):
    """Evalúa un modelo en todo el dataset de validación"""
    print(f"\n{'='*60}")
    print(f"Evaluando: {nombre_modelo}")
    print(f"{'='*60}")
    
    dataset = cargar_dataset_validacion()
    resultados = []
    
    total_preguntas = sum(len(d['preguntas']) for d in dataset)
    preguntas_correctas = 0
    peso_total = 0
    peso_correcto = 0
    
    for esquema_data in tqdm(dataset, desc="Esquemas"):
        esquema_nombre = esquema_data['nombre']
        esquema_sql = esquema_data['esquema']
        
        # Setup MySQL para este esquema
        try:
            conn, cursor = setup_mysql(esquema_sql)
        except Exception as e:
            print(f"Error configurando MySQL para {esquema_nombre}: {e}")
            continue
        
        # Evaluar cada pregunta
        for pregunta_data in tqdm(esquema_data['preguntas'], desc=f"{esquema_nombre}", leave=False):
            pregunta = pregunta_data['pregunta']
            sql_referencia = pregunta_data['sql']
            peso = pregunta_data['peso']
            nivel = pregunta_data['nivel']
            
            peso_total += peso
            
            # Generar SQL
            sql_generada = generar_sql(modelo, tokenizer, esquema_sql, pregunta, device)
            
            # Ejecutar SQL de referencia
            ok_ref, rows_ref, cols_ref, err_ref = ejecutar_query(cursor, sql_referencia)
            
            # Ejecutar SQL generada
            ok_gen, rows_gen, cols_gen, err_gen = ejecutar_query(cursor, sql_generada)
            
            # Comparar
            correcta = False
            if ok_ref and ok_gen:
                correcta = comparar_resultados(rows_ref, rows_gen)
                if correcta:
                    preguntas_correctas += 1
                    peso_correcto += peso
            
            resultados.append({
                'modelo': nombre_modelo,
                'esquema': esquema_nombre,
                'pregunta': pregunta,
                'nivel': nivel,
                'peso': peso,
                'sql_referencia': sql_referencia,
                'sql_generada': sql_generada,
                'correcta': correcta,
                'error_ref': err_ref,
                'error_gen': err_gen
            })
        
        conn.close()
    
    # Calcular métricas
    ex_score = peso_correcto / peso_total if peso_total > 0 else 0
    
    print(f"\n{nombre_modelo} - Resultados:")
    print(f"  Preguntas correctas: {preguntas_correctas}/{total_preguntas}")
    print(f"  EX Score: {ex_score:.4f}")
    
    # Guardar resultados
    df = pd.DataFrame(resultados)
    df.to_csv(f'resultados/{nombre_modelo}_results.csv', index=False)
    
    # Guardar reporte
    reporte = {
        'modelo': nombre_modelo,
        'preguntas_correctas': preguntas_correctas,
        'total_preguntas': total_preguntas,
        'ex_score': ex_score,
        'peso_correcto': peso_correcto,
        'peso_total': peso_total
    }
    
    with open(f'resultados/{nombre_modelo}_report.json', 'w') as f:
        json.dump(reporte, f, indent=2)
    
    return df, reporte

def main():
    print("="*60)
    print("EVALUACIÓN COMPLETA: BASELINE vs FINE-TUNED")
    print("="*60)
    
    config = cargar_config()
    modelo_base = config['modelo_base']
    
    # Detectar dispositivo
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Dispositivo: {device}")
    
    # Cargar tokenizer
    print("\nCargando tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(modelo_base, trust_remote_code=True)
    
    # ===== EVALUAR BASELINE =====
    print("\n" + "="*60)
    print("Cargando modelo BASELINE (sin adapter)...")
    print("="*60)
    
    modelo_baseline = AutoModelForCausalLM.from_pretrained(
        modelo_base,
        torch_dtype=torch.float32 if device.type == "mps" else torch.float16,
        trust_remote_code=True
    ).to(device)
    modelo_baseline.eval()
    
    df_baseline, reporte_baseline = evaluar_modelo(
        modelo_baseline, tokenizer, device, "baseline"
    )
    
    # Limpiar memoria
    del modelo_baseline
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    if device.type == "mps":
        torch.mps.empty_cache()
    
    # ===== EVALUAR FINE-TUNED =====
    print("\n" + "="*60)
    print("Cargando modelo FINE-TUNED (con adapter)...")
    print("="*60)
    
    modelo_base_model = AutoModelForCausalLM.from_pretrained(
        modelo_base,
        torch_dtype=torch.float32 if device.type == "mps" else torch.float16,
        trust_remote_code=True
    ).to(device)
    
    modelo_finetuned = PeftModel.from_pretrained(
        modelo_base_model, 
        config['adapter']
    )
    modelo_finetuned = modelo_finetuned.merge_and_unload()
    modelo_finetuned.eval()
    
    df_finetuned, reporte_finetuned = evaluar_modelo(
        modelo_finetuned, tokenizer, device, "finetuned"
    )
    
    # ===== COMPARACIÓN FINAL =====
    print("\n" + "="*60)
    print("COMPARACIÓN FINAL")
    print("="*60)
    print(f"\nBaseline EX Score:   {reporte_baseline['ex_score']:.4f}")
    print(f"Fine-tuned EX Score: {reporte_finetuned['ex_score']:.4f}")
    print(f"Mejora:              {reporte_finetuned['ex_score'] - reporte_baseline['ex_score']:.4f}")
    
    # Guardar comparación
    comparacion = {
        'baseline': reporte_baseline,
        'finetuned': reporte_finetuned,
        'mejora': reporte_finetuned['ex_score'] - reporte_baseline['ex_score']
    }
    
    with open('resultados/comparacion_final.json', 'w') as f:
        json.dump(comparacion, f, indent=2)
    
    print("\n✓ Resultados guardados en resultados/")
    print(f"✓ Reporte final: resultados/comparacion_final.json")

if __name__ == "__main__":
    main()
