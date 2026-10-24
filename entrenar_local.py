"""
entrenar_local.py
Entrenamiento con LoRA optimizado para Apple Silicon (MPS)
MacBook Air M3 - 24GB RAM
"""
import json
import time
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig
from datasets import Dataset
import matplotlib.pyplot as plt


def main():
    print("=" * 60)
    print("ENTRENAMIENTO LOCAL - APPLE SILICON M3")
    print("=" * 60)
    
    # Verificar dispositivo
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print(f"✓ Usando MPS (Metal Performance Shaders)")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"✓ Usando CUDA: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print(f"⚠ Usando CPU (será muy lento)")
    
    print(f"✓ PyTorch: {torch.__version__}")
    
    # Configuración
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    MODELO_BASE = config['modelo_base']
    SEMILLA = config['semilla']
    
    print(f"\nModelo base: {MODELO_BASE}")
    print(f"Semilla: {SEMILLA}")
    
    # Cargar dataset
    print("\nCargando dataset...")
    with open('datos/entrenamiento/hf_dataset/train.json', 'r', encoding='utf-8') as f:
        train_data = json.load(f)
    
    with open('datos/entrenamiento/hf_dataset/validation.json', 'r', encoding='utf-8') as f:
        val_data = json.load(f)
    
    print(f"✓ Train: {len(train_data)} ejemplos")
    print(f"✓ Validation: {len(val_data)} ejemplos")
    
    # Crear datasets de HuggingFace
    train_dataset = Dataset.from_list(train_data)
    val_dataset = Dataset.from_list(val_data)
    
    # Cargar tokenizer
    print("\nCargando tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print("✓ Tokenizer cargado")
    
    # Cargar modelo
    print("\nCargando modelo base...")
    print("(Esto puede tomar 1-2 minutos la primera vez)")
    
    # Para MPS, usar float32 (MPS tiene problemas con float16)
    # Para CUDA, usar float16
    dtype = torch.float32 if device.type == "mps" else torch.float16
    
    model = AutoModelForCausalLM.from_pretrained(
        MODELO_BASE,
        dtype=dtype,
        device_map=None,  # No usar device_map con MPS
        trust_remote_code=True
    )
    
    # Mover a dispositivo manualmente para MPS
    if device.type == "mps":
        model = model.to(device)
    
    print("✓ Modelo cargado")
    
    # Configuración de LoRA
    print("\nConfigurando LoRA...")
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=['q_proj', 'v_proj'],
        lora_dropout=0.05,
        bias='none',
        task_type='CAUSAL_LM'
    )
    
    model = get_peft_model(model, lora_config)
    
    # Contar parámetros
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"✓ Parámetros totales: {total_params:,}")
    print(f"✓ Parámetros entrenables: {trainable_params:,}")
    print(f"✓ Porcentaje: {trainable_params/total_params*100:.2f}%")
    
    # Training arguments optimizados para M3
    print("\nConfigurando entrenamiento...")
    output_dir = 'resultados/training_local'
    
    # Para MPS, no usar fp16 (no está bien soportado)
    # Usar batch size pequeño y gradient accumulation
    training_args = SFTConfig(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=1,  # Batch size 1 para ahorrar memoria
        gradient_accumulation_steps=8,  # Acumular 8 steps = batch efectivo de 8
        learning_rate=2e-4,
        fp16=False,  # No usar fp16 con MPS
        bf16=False,
        logging_steps=10,
        save_strategy='epoch',
        save_total_limit=2,
        seed=SEMILLA,
        max_length=1024,  # Aumentado para acomodar todos los ejemplos (máx 982 tokens)
        report_to='none',
        eval_strategy='epoch',
        optim='adamw_torch',  # Optimizador compatible con MPS
    )
    
    print(f"✓ Épocas: {training_args.num_train_epochs}")
    print(f"✓ Batch size: {training_args.per_device_train_batch_size}")
    print(f"✓ Gradient accumulation: {training_args.gradient_accumulation_steps}")
    print(f"✓ Learning rate: {training_args.learning_rate}")
    print(f"✓ Max sequence length: {training_args.max_length}")
    
    # Crear trainer
    print("\nInicializando trainer...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )
    
    # Entrenar
    print("\n" + "=" * 60)
    print("INICIANDO ENTRENAMIENTO")
    print("=" * 60)
    print(f"Tiempo estimado: 4-6 horas en M3")
    print(f"(Puedes dejarlo corriendo y hacer otras cosas)\n")
    
    inicio = time.time()
    train_result = trainer.train()
    tiempo_total = time.time() - inicio
    
    print(f"\n{'=' * 60}")
    print("ENTRENAMIENTO COMPLETADO")
    print(f"{'=' * 60}")
    print(f"Tiempo total: {tiempo_total/3600:.2f} horas")
    print(f"Loss final: {train_result.metrics['train_loss']:.4f}")
    
    # Guardar adapter
    adapter_dir = 'adapter'
    Path(adapter_dir).mkdir(exist_ok=True)
    trainer.model.save_pretrained(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)
    
    print(f"\n✓ Adapter guardado en: {adapter_dir}/")
    
    # Guardar métricas
    metrics = {
        'tiempo_horas': tiempo_total / 3600,
        'loss_final': float(train_result.metrics['train_loss']),
        'parametros_entrenables': trainable_params,
        'parametros_totales': total_params,
        'device': str(device),
        'modelo_base': MODELO_BASE,
        'config': {
            'r': 16,
            'alpha': 32,
            'epochs': 3,
            'batch_size': 1,
            'gradient_accumulation': 8,
            'learning_rate': 2e-4,
            'max_seq_length': 512
        }
    }
    
    with open('resultados/metricas_entrenamiento.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✓ Métricas guardadas en: resultados/metricas_entrenamiento.json")
    
    # Actualizar config.json para usar el adapter
    config['usar_adapter'] = True
    config['adapter'] = 'adapter/'
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ config.json actualizado")
    
    print("\n" + "=" * 60)
    print("PRÓXIMOS PASOS")
    print("=" * 60)
    print("1. Evaluar baseline: python evaluar_baseline.py")
    print("2. Evaluar modelo: python evaluar.py")
    print("3. Experimento inferencia: python experimento_inferencia.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
