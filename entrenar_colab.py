"""
entrenar_colab.py
Script optimizado para ejecutar en Google Colab con GPU T4
Incluye ambas configuraciones de LoRA
"""
import json
import os
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
from datasets import load_from_disk
import matplotlib.pyplot as plt
import time


def main():
    print("=" * 60)
    print("ENTRENAMIENTO TEXT-TO-SQL CON LORA")
    print("=" * 60)
    
    # Verificar GPU
    if not torch.cuda.is_available():
        raise RuntimeError("Este script requiere GPU. Ejecutar en Google Colab.")
    
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")
    
    # Cargar configuración
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    MODELO_BASE = config['modelo_base']
    SEMILLA = config['semilla']
    
    print(f"\nModelo base: {MODELO_BASE}")
    print(f"Semilla: {SEMILLA}")
    
    # Cargar dataset
    print("\nCargando dataset...")
    dataset_path = Path("datos/entrenamiento/hf_dataset")
    if dataset_path.exists():
        dataset = load_from_disk(str(dataset_path))
    else:
        print("Dataset no encontrado. Ejecutar primero: python preparar_datos_training.py")
        return
    
    print(f"Train: {len(dataset['train'])} ejemplos")
    print(f"Validation: {len(dataset['validation'])} ejemplos")
    
    # Cargar modelo y tokenizer
    print("\nCargando modelo...")
    tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        MODELO_BASE,
        torch_dtype=torch.float16,
        device_map='auto',
        trust_remote_code=True
    )
    
    # ================================================================
    # CONFIGURACIÓN A: rank=8, alpha=32, targets=[q_proj, v_proj]
    # ================================================================
    print("\n" + "=" * 60)
    print("CONFIGURACIÓN A")
    print("=" * 60)
    print("Hipótesis: rank bajo es suficiente para patrones SQL básicos")
    
    lora_config_a = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=['q_proj', 'v_proj'],
        lora_dropout=0.05,
        bias='none',
        task_type='CAUSAL_LM'
    )
    
    model_a = get_peft_model(model, lora_config_a)
    model_a.print_trainable_parameters()
    
    training_args_a = SFTConfig(
        output_dir='resultados/training_config_a',
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_strategy='epoch',
        save_total_limit=2,
        seed=SEMILLA,
        max_seq_length=2048,
        report_to='none',
        eval_strategy='epoch',
        eval_steps=100
    )
    
    trainer_a = SFTTrainer(
        model=model_a,
        args=training_args_a,
        train_dataset=dataset['train'],
        eval_dataset=dataset['validation'],
        tokenizer=tokenizer
    )
    
    print("\nEntrenando Config A...")
    inicio = time.time()
    train_result_a = trainer_a.train()
    tiempo_a = time.time() - inicio
    
    print(f"Tiempo de entrenamiento: {tiempo_a:.1f}s ({tiempo_a/60:.1f} min)")
    print(f"Loss final: {train_result_a.metrics['train_loss']:.4f}")
    
    # Guardar adapter A
    adapter_dir_a = 'adapter/config_a'
    os.makedirs(adapter_dir_a, exist_ok=True)
    trainer_a.model.save_pretrained(adapter_dir_a)
    tokenizer.save_pretrained(adapter_dir_a)
    print(f"✓ Adapter guardado en {adapter_dir_a}")
    
    # Liberar memoria
    del model_a, trainer_a
    torch.cuda.empty_cache()
    
    # ================================================================
    # CONFIGURACIÓN B: rank=32, alpha=64, targets=[q_proj, v_proj, k_proj, o_proj]
    # ================================================================
    print("\n" + "=" * 60)
    print("CONFIGURACIÓN B")
    print("=" * 60)
    print("Hipótesis: rank alto captura patrones SQL complejos")
    
    # Recargar modelo base
    model = AutoModelForCausalLM.from_pretrained(
        MODELO_BASE,
        torch_dtype=torch.float16,
        device_map='auto',
        trust_remote_code=True
    )
    
    lora_config_b = LoraConfig(
        r=32,
        lora_alpha=64,
        target_modules=['q_proj', 'v_proj', 'k_proj', 'o_proj'],
        lora_dropout=0.05,
        bias='none',
        task_type='CAUSAL_LM'
    )
    
    model_b = get_peft_model(model, lora_config_b)
    model_b.print_trainable_parameters()
    
    training_args_b = SFTConfig(
        output_dir='resultados/training_config_b',
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_strategy='epoch',
        save_total_limit=2,
        seed=SEMILLA,
        max_seq_length=2048,
        report_to='none',
        eval_strategy='epoch',
        eval_steps=100
    )
    
    trainer_b = SFTTrainer(
        model=model_b,
        args=training_args_b,
        train_dataset=dataset['train'],
        eval_dataset=dataset['validation'],
        tokenizer=tokenizer
    )
    
    print("\nEntrenando Config B...")
    inicio = time.time()
    train_result_b = trainer_b.train()
    tiempo_b = time.time() - inicio
    
    print(f"Tiempo de entrenamiento: {tiempo_b:.1f}s ({tiempo_b/60:.1f} min)")
    print(f"Loss final: {train_result_b.metrics['train_loss']:.4f}")
    
    # Guardar adapter B
    adapter_dir_b = 'adapter/config_b'
    os.makedirs(adapter_dir_b, exist_ok=True)
    trainer_b.model.save_pretrained(adapter_dir_b)
    tokenizer.save_pretrained(adapter_dir_b)
    print(f"✓ Adapter guardado en {adapter_dir_b}")
    
    # ================================================================
    # RESUMEN Y COMPARACIÓN
    # ================================================================
    print("\n" + "=" * 60)
    print("RESUMEN DE ENTRENAMIENTO")
    print("=" * 60)
    
    comparacion = {
        'config_a': {
            'rank': 8,
            'alpha': 32,
            'targets': ['q_proj', 'v_proj'],
            'loss': float(train_result_a.metrics['train_loss']),
            'tiempo_seg': tiempo_a,
            'hipotesis': 'Rank bajo es suficiente para patrones SQL básicos'
        },
        'config_b': {
            'rank': 32,
            'alpha': 64,
            'targets': ['q_proj', 'v_proj', 'k_proj', 'o_proj'],
            'loss': float(train_result_b.metrics['train_loss']),
            'tiempo_seg': tiempo_b,
            'hipotesis': 'Rank alto captura patrones SQL complejos'
        }
    }
    
    print(f"\nConfig A:")
    print(f"  Loss: {comparacion['config_a']['loss']:.4f}")
    print(f"  Tiempo: {comparacion['config_a']['tiempo_seg']/60:.1f} min")
    
    print(f"\nConfig B:")
    print(f"  Loss: {comparacion['config_b']['loss']:.4f}")
    print(f"  Tiempo: {comparacion['config_b']['tiempo_seg']/60:.1f} min")
    
    # Guardar comparación
    with open('resultados/comparacion_entrenamiento.json', 'w') as f:
        json.dump(comparacion, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Comparación guardada en resultados/comparacion_entrenamiento.json")
    
    # Graficar curvas de loss
    plt.figure(figsize=(10, 6))
    # TODO: Cargar logs de entrenamiento y graficar curvas
    plt.xlabel('Step')
    plt.ylabel('Loss')
    plt.title('Curvas de pérdida: Config A vs Config B')
    plt.legend(['Config A', 'Config B'])
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('resultados/curvas_loss.png', dpi=150)
    print(f"✓ Gráfica guardada en resultados/curvas_loss.png")
    
    print("\n" + "=" * 60)
    print("ENTRENAMIENTO COMPLETADO")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Evaluar ambos adapters en validación propia")
    print("2. Ejecutar: python evaluar.py")
    print("3. Comparar resultados y seleccionar mejor adapter")
    print("4. Copiar mejor adapter a adapter/ para entrega final")


if __name__ == "__main__":
    main()
