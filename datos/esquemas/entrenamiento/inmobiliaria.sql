-- ============================================
-- Esquema: inmobiliaria
-- Entrenamiento
-- ============================================

CREATE TABLE zonas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la zona',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre de la zona o barrio',
    ciudad VARCHAR(100) NOT NULL COMMENT 'Ciudad donde se ubica la zona',
    descripcion TEXT COMMENT 'Descripción de la zona'
) COMMENT='Zonas o barrios donde se ubican las propiedades';

CREATE TABLE agentes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del agente',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del agente inmobiliario',
    telefono VARCHAR(20) COMMENT 'Teléfono de contacto del agente',
    email VARCHAR(150) UNIQUE COMMENT 'Correo electrónico del agente',
    fecha_contratacion DATE NOT NULL COMMENT 'Fecha en que fue contratado'
) COMMENT='Agentes inmobiliarios de la empresa';

CREATE TABLE propiedades (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la propiedad',
    direccion VARCHAR(300) NOT NULL COMMENT 'Dirección completa de la propiedad',
    zona_id INT NOT NULL COMMENT 'Zona donde se ubica la propiedad',
    tipo VARCHAR(50) NOT NULL COMMENT 'Tipo: casa, apartamento, oficina, terreno, local',
    area_m2 DECIMAL(10,2) NOT NULL COMMENT 'Área de la propiedad en metros cuadrados',
    habitaciones INT COMMENT 'Número de habitaciones',
    banos INT COMMENT 'Número de baños',
    precio_venta DECIMAL(12,2) COMMENT 'Precio de venta en dólares',
    precio_alquiler DECIMAL(8,2) COMMENT 'Precio de alquiler mensual en dólares',
    disponible BOOLEAN DEFAULT TRUE COMMENT 'Indica si la propiedad está disponible',
    FOREIGN KEY (zona_id) REFERENCES zonas(id)
) COMMENT='Propiedades disponibles para venta o alquiler';

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del cliente',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del cliente',
    email VARCHAR(150) UNIQUE COMMENT 'Correo electrónico del cliente',
    telefono VARCHAR(20) COMMENT 'Teléfono del cliente',
    tipo VARCHAR(20) NOT NULL COMMENT 'Tipo: comprador, arrendatario, vendedor'
) COMMENT='Clientes interesados en propiedades';

CREATE TABLE visitas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la visita',
    propiedad_id INT NOT NULL COMMENT 'Propiedad visitada',
    cliente_id INT NOT NULL COMMENT 'Cliente que realizó la visita',
    agente_id INT NOT NULL COMMENT 'Agente que acompañó la visita',
    fecha_visita DATETIME NOT NULL COMMENT 'Fecha y hora de la visita',
    comentario TEXT COMMENT 'Comentarios del cliente sobre la visita',
    FOREIGN KEY (propiedad_id) REFERENCES propiedades(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (agente_id) REFERENCES agentes(id)
) COMMENT='Visitas de clientes a propiedades';

CREATE TABLE contratos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del contrato',
    propiedad_id INT NOT NULL COMMENT 'Propiedad objeto del contrato',
    cliente_id INT NOT NULL COMMENT 'Cliente que firma el contrato',
    agente_id INT NOT NULL COMMENT 'Agente que gestionó el contrato',
    tipo VARCHAR(20) NOT NULL COMMENT 'Tipo: venta, alquiler',
    fecha_firma DATE NOT NULL COMMENT 'Fecha en que se firmó el contrato',
    monto DECIMAL(12,2) NOT NULL COMMENT 'Monto total del contrato en dólares',
    FOREIGN KEY (propiedad_id) REFERENCES propiedades(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (agente_id) REFERENCES agentes(id)
) COMMENT='Contratos de venta o alquiler de propiedades';
