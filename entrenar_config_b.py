"""
Entrenamiento Config B: LoRA con rank=32 (vs rank=16 del Config A)
Mantiene todos los demás parámetros iguales para comparar el impacto del rank
"""
import json
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig
from datasets import Dataset
import time

print("=" * 60)
print("ENTRENAMIENTO CONFIG B: LoRA rank=32")
print("=" * 60)

# Configuración
with open('config.json', 'r') as f:
    config = json.load(f)

MODELO_BASE = config['modelo_base']
SEMILLA = config['semilla']

print(f"Modelo base: {MODELO_BASE}")
print(f"Semilla: {SEMILLA}")
print(f"Dispositivo: MPS (Apple Silicon)")

# Cargar datos
print("\nCargando dataset...")
with open('datos/entrenamiento/hf_dataset/train.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)

with open('datos/entrenamiento/hf_dataset/validation.json', 'r', encoding='utf-8') as f:
    val_data = json.load(f)

train_dataset = Dataset.from_list(train_data)
val_dataset = Dataset.from_list(val_data)

print(f"✓ Train: {len(train_data)} ejemplos")
print(f"✓ Validation: {len(val_data)} ejemplos")

# Cargar modelo base
print("\nCargando modelo base...")
tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODELO_BASE,
    dtype=torch.float32,  # MPS requiere float32
    device_map=None,
    trust_remote_code=True
)
model = model.to('mps')
print("✓ Modelo cargado")

# CONFIGURACIÓN B: rank=32 (vs rank=16 del Config A)
print("\nConfigurando LoRA Config B...")
lora_config_b = LoraConfig(
    r=32,  # DIFERENTE: rank=32 vs rank=16
    lora_alpha=64,  # Mantener ratio alpha/r = 2
    target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'],  # IGUAL que Config A
    lora_dropout=0.05,
    bias='none',
    task_type='CAUSAL_LM'
)

model = get_peft_model(model, lora_config_b)

# Contar parámetros
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

print(f"✓ Parámetros totales: {total_params:,}")
print(f"✓ Parámetros entrenables: {trainable_params:,}")
print(f"✓ Porcentaje: {trainable_params/total_params*100:.2f}%")
print(f"✓ Rank: 32 (Config A usó rank=16)")

# Configuración de entrenamiento (IGUAL que Config A)
print("\nConfigurando entrenamiento...")
output_dir = 'resultados/training_config_b'

training_args = SFTConfig(
    output_dir=output_dir,
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    fp16=False,
    bf16=False,
    logging_steps=10,
    save_strategy='epoch',
    save_total_limit=2,
    seed=SEMILLA,
    max_length=1024,
    report_to='none',
    eval_strategy='epoch',
    optim='adamw_torch',
)

print(f"✓ Épocas: 3")
print(f"✓ Batch size: 1 (gradient accumulation: 8)")
print(f"✓ Learning rate: 2e-4")
print(f"✓ Max length: 1024")

# Inicializar trainer
print("\nInicializando trainer...")
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

# Entrenar
print("\n" + "=" * 60)
print("INICIANDO ENTRENAMIENTO CONFIG B")
print("=" * 60)
print(f"Tiempo estimado: ~30 horas en M3")
print(f"Comparación: Config A (rank=16) tomó 28.77 horas")
print()

inicio = time.time()
train_result = trainer.train()
tiempo_total = time.time() - inicio

print(f"\n{'=' * 60}")
print("ENTRENAMIENTO CONFIG B COMPLETADO")
print(f"{'=' * 60}")
print(f"Tiempo total: {tiempo_total/3600:.2f} horas")
print(f"Loss final: {train_result.metrics['train_loss']:.4f}")

# Guardar adapter Config B
adapter_dir_b = 'adapter_config_b'
Path(adapter_dir_b).mkdir(exist_ok=True)
trainer.model.save_pretrained(adapter_dir_b)
tokenizer.save_pretrained(adapter_dir_b)

print(f"\n✓ Adapter Config B guardado en: {adapter_dir_b}/")

# Guardar métricas
metrics_b = {
    'config': 'B',
    'rank': 32,
    'lora_alpha': 64,
    'target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj'],
    'tiempo_horas': tiempo_total / 3600,
    'loss_final': float(train_result.metrics['train_loss']),
    'parametros_entrenables': trainable_params,
    'parametros_totales': total_params,
    'device': 'mps',
    'modelo_base': MODELO_BASE,
    'diferencia_con_config_a': 'rank=32 vs rank=16, alpha=64 vs alpha=32'
}

with open('resultados/metricas_config_b.json', 'w') as f:
    json.dump(metrics_b, f, indent=2)

print(f"✓ Métricas guardadas en: resultados/metricas_config_b.json")

# Comparación con Config A
try:
    with open('resultados/metricas_entrenamiento.json', 'r') as f:
        metrics_a = json.load(f)
    
    print(f"\n{'=' * 60}")
    print("COMPARACIÓN CONFIG A vs CONFIG B")
    print(f"{'=' * 60}")
    print(f"Config A (rank=16):")
    print(f"  Loss: {metrics_a['loss_final']:.4f}")
    print(f"  Tiempo: {metrics_a['tiempo_horas']:.2f} horas")
    print(f"  Parámetros: {metrics_a['parametros_entrenables']:,}")
    print(f"\nConfig B (rank=32):")
    print(f"  Loss: {metrics_b['loss_final']:.4f}")
    print(f"  Tiempo: {metrics_b['tiempo_horas']:.2f} horas")
    print(f"  Parámetros: {metrics_b['parametros_entrenables']:,}")
    print(f"\nDiferencia en loss: {metrics_b['loss_final'] - metrics_a['loss_final']:+.4f}")
except:
    print("\n⚠ No se encontraron métricas de Config A para comparar")

print("\n" + "=" * 60)
print("PRÓXIMOS PASOS")
print("=" * 60)
print("1. Evaluar Config B con evaluar_config_b.py")
print("2. Comparar EX Score de Config A vs Config B")
print("3. Seleccionar mejor configuración para entrega final")
print("=" * 60)
