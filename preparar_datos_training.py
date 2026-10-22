"""
preparar_datos_training.py
Convierte el dataset JSON al formato necesario para entrenamiento
Funciona localmente - las dependencias de HuggingFace se instalan en Colab
"""
import json
from pathlib import Path
import random

random.seed(2026)


def cargar_esquemas(ruta="datos/esquemas"):
    """Carga todos los esquemas SQL."""
    esquemas = {}
    for path in Path(ruta).rglob("*.sql"):
        nombre = path.stem
        with open(path, 'r', encoding='utf-8') as f:
            esquemas[nombre] = f.read()
    return esquemas


def construir_prompt(esquema, pregunta):
    """Construye el prompt de entrada para el modelo."""
    return f"""### Esquema de la base de datos:
{esquema.strip()}

### Pregunta:
{pregunta.strip()}

### Consulta MySQL:
"""


def preparar_dataset(ruta_dataset="datos/entrenamiento/dataset_completo.json"):
    """Prepara el dataset para entrenamiento."""
    print("Cargando dataset...")
    with open(ruta_dataset, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    print("Cargando esquemas...")
    esquemas = cargar_esquemas()
    
    print(f"Procesando {len(dataset)} ejemplos...")
    registros = []
    
    for item in dataset:
        esquema_nombre = item.get("esquema", "")
        
        # Buscar el esquema
        if esquema_nombre in esquemas:
            esquema_sql = esquemas[esquema_nombre]
        else:
            # Usar un esquema aleatorio si no se encuentra
            esquema_sql = random.choice(list(esquemas.values()))
        
        pregunta = item["pregunta"]
        sql = item["sql"]
        
        # Construir texto completo para entrenamiento
        prompt = construir_prompt(esquema_sql, pregunta)
        texto_completo = prompt + sql
        
        registros.append({
            "text": texto_completo,
            "prompt": prompt,
            "completion": sql,
            "nivel": item.get("nivel", "facil")
        })
    
    print(f"✓ {len(registros)} ejemplos preparados")
    
    # Dividir en train/validation (90/10)
    random.shuffle(registros)
    split_idx = int(len(registros) * 0.9)
    
    train_data = registros[:split_idx]
    val_data = registros[split_idx:]
    
    print(f"Train: {len(train_data)}, Validation: {len(val_data)}")
    
    # Estadísticas por nivel
    for split_name, split_data in [("Train", train_data), ("Validation", val_data)]:
        facil = sum(1 for r in split_data if r["nivel"] == "facil")
        medio = sum(1 for r in split_data if r["nivel"] == "media")
        dificil = sum(1 for r in split_data if r["nivel"] == "dificil")
        print(f"  {split_name}: fácil={facil}, medio={medio}, difícil={dificil}")
    
    # Guardar en formato JSON para Colab
    output_dir = Path("datos/entrenamiento/hf_dataset")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "train.json", 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    
    with open(output_dir / "validation.json", 'w', encoding='utf-8') as f:
        json.dump(val_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Dataset guardado en {output_dir}")
    print(f"  - train.json ({len(train_data)} ejemplos)")
    print(f"  - validation.json ({len(val_data)} ejemplos)")
    
    # Intentar guardar en formato HuggingFace si está disponible
    try:
        from datasets import Dataset, DatasetDict
        dataset_dict = DatasetDict({
            "train": Dataset.from_list(train_data),
            "validation": Dataset.from_list(val_data)
        })
        dataset_dict.save_to_disk(str(output_dir / "hf_format"))
        print(f"✓ También guardado en formato HuggingFace en {output_dir / 'hf_format'}")
    except ImportError:
        print("ℹ Formato HuggingFace no disponible (se generará en Colab)")
    
    return train_data, val_data


if __name__ == "__main__":
    train_data, val_data = preparar_dataset()
    print(f"\nDataset listo para entrenamiento en Colab:")
    print(f"  Ejecutar: python entrenar_colab.py")
