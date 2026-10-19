-- ============================================
-- Esquema: agencia_viajes
-- Entrenamiento
-- ============================================

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del cliente',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del cliente',
    email VARCHAR(150) UNIQUE COMMENT 'Correo electrónico del cliente',
    telefono VARCHAR(20) COMMENT 'Teléfono del cliente',
    ciudad VARCHAR(100) COMMENT 'Ciudad de residencia del cliente'
) COMMENT='Clientes de la agencia de viajes';

CREATE TABLE destinos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del destino',
    ciudad VARCHAR(100) NOT NULL COMMENT 'Ciudad del destino turístico',
    pais VARCHAR(100) NOT NULL COMMENT 'País del destino turístico',
    descripcion TEXT COMMENT 'Descripción del destino',
    clima VARCHAR(50) COMMENT 'Clima predominante del destino'
) COMMENT='Destinos turísticos ofrecidos por la agencia';

CREATE TABLE hoteles (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del hotel',
    nombre VARCHAR(200) NOT NULL COMMENT 'Nombre del hotel',
    destino_id INT NOT NULL COMMENT 'Destino donde se ubica el hotel',
    estrellas INT NOT NULL COMMENT 'Clasificación de estrellas del hotel',
    precio_noche DECIMAL(8,2) NOT NULL COMMENT 'Precio por noche en dólares',
    FOREIGN KEY (destino_id) REFERENCES destinos(id)
) COMMENT='Hoteles disponibles en los destinos';

CREATE TABLE vuelos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del vuelo',
    aerolinea VARCHAR(100) NOT NULL COMMENT 'Nombre de la aerolínea',
    origen VARCHAR(100) NOT NULL COMMENT 'Ciudad de origen del vuelo',
    destino_id INT NOT NULL COMMENT 'Destino del vuelo',
    fecha_salida DATETIME NOT NULL COMMENT 'Fecha y hora de salida',
    fecha_llegada DATETIME NOT NULL COMMENT 'Fecha y hora de llegada',
    precio DECIMAL(10,2) NOT NULL COMMENT 'Precio del vuelo por persona en dólares',
    FOREIGN KEY (destino_id) REFERENCES destinos(id)
) COMMENT='Vuelos disponibles ofrecidos por la agencia';

CREATE TABLE paquetes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del paquete',
    nombre VARCHAR(200) NOT NULL COMMENT 'Nombre del paquete turístico',
    destino_id INT NOT NULL COMMENT 'Destino principal del paquete',
    hotel_id INT NOT NULL COMMENT 'Hotel incluido en el paquete',
    vuelo_id INT NOT NULL COMMENT 'Vuelo incluido en el paquete',
    duracion_dias INT NOT NULL COMMENT 'Duración del paquete en días',
    precio_persona DECIMAL(10,2) NOT NULL COMMENT 'Precio por persona en dólares',
    FOREIGN KEY (destino_id) REFERENCES destinos(id),
    FOREIGN KEY (hotel_id) REFERENCES hoteles(id),
    FOREIGN KEY (vuelo_id) REFERENCES vuelos(id)
) COMMENT='Paquetes turísticos ofrecidos por la agencia';

CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la reserva',
    cliente_id INT NOT NULL COMMENT 'Cliente que realizó la reserva',
    paquete_id INT NOT NULL COMMENT 'Paquete turístico reservado',
    fecha_reserva DATE NOT NULL COMMENT 'Fecha en que se realizó la reserva',
    fecha_viaje DATE NOT NULL COMMENT 'Fecha de inicio del viaje',
    num_personas INT NOT NULL COMMENT 'Número de personas que viajan',
    total DECIMAL(12,2) NOT NULL COMMENT 'Total pagado por la reserva',
    estado VARCHAR(20) NOT NULL DEFAULT 'confirmada' COMMENT 'Estado: confirmada, cancelada, completada',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (paquete_id) REFERENCES paquetes(id)
) COMMENT='Reservas de paquetes turísticos realizadas por clientes';
