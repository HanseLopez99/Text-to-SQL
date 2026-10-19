"""
solucion.py - Text-to-SQL con LoRA
Genera consultas MySQL a partir de un esquema y pregunta en español.
"""

import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel


def cargar_config():
    """Carga la configuración desde config.json."""
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def construir_prompt(esquema: str, pregunta: str) -> str:
    """
    Construye el prompt para el modelo.
    """
    prompt = f"""### Esquema de la base de datos:
{esquema.strip()}

### Pregunta:
{pregunta.strip()}

### Consulta MySQL:
"""
    return prompt


# Variables globales para cache del modelo
_model = None
_tokenizer = None


def cargar_modelo(config=None):
    """Carga el modelo base y opcionalmente el adapter LoRA."""
    global _model, _tokenizer

    if config is None:
        config = cargar_config()

    modelo_nombre = config["modelo_base"]
    usar_adapter = config.get("usar_adapter", True)
    adapter_path = config.get("adapter", "adapter/")

    # Configurar semilla para generación determinista
    seed = config.get("semilla", 2026)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    # Cargar tokenizer
    _tokenizer = AutoTokenizer.from_pretrained(
        modelo_nombre, trust_remote_code=True
    )
    if _tokenizer.pad_token is None:
        _tokenizer.pad_token = _tokenizer.eos_token

    # Cargar modelo base
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    _model = AutoModelForCausalLM.from_pretrained(
        modelo_nombre,
        torch_dtype=dtype,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=True,
    )

    # Cargar adapter si está habilitado
    if usar_adapter:
        _model = PeftModel.from_pretrained(_model, adapter_path)
        _model = _model.merge_and_unload()

    _model.eval()
    return _model, _tokenizer


def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    """
    Genera una consulta SQL MySQL dado un esquema y una pregunta en español.

    Parámetros:
        esquema: CREATE TABLE statements con COMMENTs
        pregunta: texto en español
        ejecutar: función opcional que ejecuta SQL y retorna
                  dict con ok, columnas, filas, error (hasta 3 llamadas)

    Retorno:
        Una consulta SELECT o WITH ... SELECT
    """
    global _model, _tokenizer

    # Cargar modelo si no está en memoria
    if _model is None or _tokenizer is None:
        cargar_modelo()

    config = cargar_config()
    seed = config.get("semilla", 2026)

    # Construir prompt
    prompt = construir_prompt(esquema, pregunta)

    # Tokenizar
    inputs = _tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    if torch.cuda.is_available():
        inputs = {k: v.to(_model.device) for k, v in inputs.items()}

    # Generar
    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,
            temperature=1.0,
            num_beams=1,
            pad_token_id=_tokenizer.eos_token_id,
            eos_token_id=_tokenizer.eos_token_id,
        )

    # Decodificar solo los tokens nuevos
    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    respuesta = _tokenizer.decode(generated_tokens, skip_special_tokens=True)

    # Extraer la consulta SQL
    sql = _extraer_sql(respuesta)

    # Si tenemos función de ejecutar, intentamos self-correction
    if ejecutar is not None:
        resultado = ejecutar(sql)
        if not resultado.get("ok", False):
            # Reintentar con el error como contexto
            sql = _corregir_sql(esquema, pregunta, sql, resultado.get("error", ""), seed)

    return sql


def _extraer_sql(respuesta: str) -> str:
    """Extrae la consulta SQL de la respuesta del modelo."""
    respuesta = respuesta.strip()

    # Buscar patrones comunes de inicio de SQL
    lineas = respuesta.split("\n")
    sql_lineas = []
    en_sql = False

    for linea in lineas:
        linea_stripped = linea.strip()
        # Detectar inicio de SQL
        if any(linea_stripped.upper().startswith(kw) for kw in
               ["SELECT", "WITH", "select", "with"]):
            en_sql = True

        if en_sql:
            # Detectar fin (línea vacía, explicación, o marca)
            if linea_stripped == "" and len(sql_lineas) > 0:
                # Verificar si la siguiente línea relevante no es SQL
                break
            if "```" in linea_stripped and len(sql_lineas) > 0:
                break
            if linea_stripped.startswith("###") and len(sql_lineas) > 0:
                break
            sql_lineas.append(linea)

    if sql_lineas:
        sql = "\n".join(sql_lineas).strip()
        # Limpiar markdown code blocks si están presentes
        sql = sql.replace("```sql", "").replace("```SQL", "").replace("```", "")
        sql = sql.strip()
        # Quitar punto y coma final si lo tiene
        if sql.endswith(";"):
            sql = sql[:-1].strip()
        return sql

    # Fallback: limpiar la respuesta completa
    sql = respuesta.split("\n")[0].strip()
    sql = sql.replace("```sql", "").replace("```SQL", "").replace("```", "").strip()
    if sql.endswith(";"):
        sql = sql[:-1].strip()
    return sql


def _corregir_sql(esquema: str, pregunta: str, sql_previo: str, error: str, seed: int) -> str:
    """Intenta corregir la SQL dado un error de ejecución."""
    prompt = f"""### Esquema de la base de datos:
{esquema.strip()}

### Pregunta:
{pregunta.strip()}

### Consulta anterior (tiene un error):
{sql_previo}

### Error de MySQL:
{error}

### Consulta MySQL corregida:
"""

    inputs = _tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    if torch.cuda.is_available():
        inputs = {k: v.to(_model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,
            temperature=1.0,
            num_beams=1,
            pad_token_id=_tokenizer.eos_token_id,
            eos_token_id=_tokenizer.eos_token_id,
        )

    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    respuesta = _tokenizer.decode(generated_tokens, skip_special_tokens=True)
    return _extraer_sql(respuesta)


if __name__ == "__main__":
    # Prueba básica
    config = cargar_config()
    print(f"Modelo: {config['modelo_base']}")
    print(f"Adapter: {config['adapter']}")
    print(f"Usar adapter: {config['usar_adapter']}")
    print("\nCargando modelo...")
    cargar_modelo(config)
    print("Modelo cargado correctamente.")

    # Ejemplo
    esquema_test = """
CREATE TABLE productos (
    id INT PRIMARY KEY COMMENT 'Identificador del producto',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del producto',
    precio DECIMAL(10,2) NOT NULL COMMENT 'Precio del producto',
    categoria VARCHAR(50) COMMENT 'Categoría del producto'
) COMMENT='Productos de la tienda';
"""
    pregunta_test = "¿Cuáles son los 5 productos más caros?"
    sql = generar_sql(esquema_test, pregunta_test)
    print(f"\nSQL generada:\n{sql}")
