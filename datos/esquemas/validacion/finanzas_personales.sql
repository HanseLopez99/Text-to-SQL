-- ============================================
-- Esquema: finanzas_personales
-- VALIDACIÓN
-- ============================================

CREATE TABLE cuentas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la cuenta',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre de la cuenta bancaria',
    tipo VARCHAR(30) NOT NULL COMMENT 'Tipo de cuenta: ahorro, corriente, inversión',
    saldo DECIMAL(12,2) NOT NULL COMMENT 'Saldo actual de la cuenta en dólares',
    moneda VARCHAR(5) NOT NULL DEFAULT 'USD' COMMENT 'Moneda de la cuenta',
    fecha_apertura DATE NOT NULL COMMENT 'Fecha en que se abrió la cuenta'
) COMMENT='Cuentas bancarias del usuario';

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la categoría',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre de la categoría de gasto o ingreso',
    tipo VARCHAR(20) NOT NULL COMMENT 'Tipo: ingreso, gasto',
    descripcion TEXT COMMENT 'Descripción de la categoría'
) COMMENT='Categorías para clasificar transacciones';

CREATE TABLE transacciones (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la transacción',
    cuenta_id INT NOT NULL COMMENT 'Cuenta asociada a la transacción',
    categoria_id INT NOT NULL COMMENT 'Categoría de la transacción',
    monto DECIMAL(12,2) NOT NULL COMMENT 'Monto de la transacción (positivo ingreso, negativo gasto)',
    descripcion TEXT COMMENT 'Descripción o detalle de la transacción',
    fecha DATE NOT NULL COMMENT 'Fecha en que se realizó la transacción',
    FOREIGN KEY (cuenta_id) REFERENCES cuentas(id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
) COMMENT='Transacciones financieras del usuario';

CREATE TABLE presupuestos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del presupuesto',
    categoria_id INT NOT NULL COMMENT 'Categoría presupuestada',
    monto_maximo DECIMAL(10,2) NOT NULL COMMENT 'Monto máximo asignado al presupuesto',
    mes INT NOT NULL COMMENT 'Mes del presupuesto (1-12)',
    anio INT NOT NULL COMMENT 'Año del presupuesto',
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
) COMMENT='Presupuestos mensuales por categoría';

CREATE TABLE metas_ahorro (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la meta',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre de la meta de ahorro',
    monto_objetivo DECIMAL(12,2) NOT NULL COMMENT 'Monto objetivo a alcanzar',
    monto_actual DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT 'Monto ahorrado hasta ahora',
    fecha_limite DATE COMMENT 'Fecha límite para alcanzar la meta',
    completada BOOLEAN DEFAULT FALSE COMMENT 'Indica si la meta fue completada'
) COMMENT='Metas de ahorro del usuario';

CREATE TABLE tarjetas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la tarjeta',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre de la tarjeta de crédito',
    entidad VARCHAR(100) NOT NULL COMMENT 'Entidad emisora de la tarjeta',
    limite_credito DECIMAL(10,2) NOT NULL COMMENT 'Límite de crédito de la tarjeta',
    saldo_actual DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Saldo actual utilizado',
    fecha_corte INT NOT NULL COMMENT 'Día del mes del corte de tarjeta',
    fecha_vencimiento DATE NOT NULL COMMENT 'Fecha de vencimiento de la tarjeta'
) COMMENT='Tarjetas de crédito del usuario';
