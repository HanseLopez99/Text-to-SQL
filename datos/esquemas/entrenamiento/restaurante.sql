-- ============================================
-- Esquema: restaurante
-- Entrenamiento
-- ============================================

CREATE TABLE meseros (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del mesero',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo del mesero',
    turno VARCHAR(20) NOT NULL COMMENT 'Turno de trabajo: matutino, vespertino, nocturno',
    fecha_contratacion DATE NOT NULL COMMENT 'Fecha en que fue contratado'
) COMMENT='Meseros que trabajan en el restaurante';

CREATE TABLE mesas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la mesa',
    numero INT NOT NULL UNIQUE COMMENT 'Número de la mesa en el restaurante',
    capacidad INT NOT NULL COMMENT 'Cantidad de personas que se pueden sentar',
    ubicacion VARCHAR(50) COMMENT 'Ubicación dentro del restaurante: interior, terraza, barra'
) COMMENT='Mesas disponibles en el restaurante';

CREATE TABLE platillos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del platillo',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre del platillo',
    descripcion TEXT COMMENT 'Descripción del platillo',
    precio DECIMAL(8,2) NOT NULL COMMENT 'Precio del platillo en dólares',
    categoria VARCHAR(50) NOT NULL COMMENT 'Categoría: entrada, plato_fuerte, postre, bebida',
    disponible BOOLEAN DEFAULT TRUE COMMENT 'Indica si el platillo está disponible hoy'
) COMMENT='Platillos disponibles en el menú del restaurante';

CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la reserva',
    cliente_nombre VARCHAR(150) NOT NULL COMMENT 'Nombre del cliente que hizo la reserva',
    cliente_telefono VARCHAR(20) COMMENT 'Teléfono de contacto del cliente',
    mesa_id INT NOT NULL COMMENT 'Mesa reservada',
    fecha_reserva DATETIME NOT NULL COMMENT 'Fecha y hora para la reserva',
    personas INT NOT NULL COMMENT 'Número de personas para la reserva',
    FOREIGN KEY (mesa_id) REFERENCES mesas(id)
) COMMENT='Reservas de mesas en el restaurante';

CREATE TABLE ordenes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la orden',
    mesa_id INT NOT NULL COMMENT 'Mesa en que se realizó la orden',
    mesero_id INT NOT NULL COMMENT 'Mesero que atendió la orden',
    fecha_orden DATETIME NOT NULL COMMENT 'Fecha y hora en que se tomó la orden',
    total DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Total de la orden',
    FOREIGN KEY (mesa_id) REFERENCES mesas(id),
    FOREIGN KEY (mesero_id) REFERENCES meseros(id)
) COMMENT='Órdenes tomadas en el restaurante';

CREATE TABLE detalles_orden (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del detalle',
    orden_id INT NOT NULL COMMENT 'Orden a la que pertenece',
    platillo_id INT NOT NULL COMMENT 'Platillo ordenado',
    cantidad INT NOT NULL DEFAULT 1 COMMENT 'Cantidad del platillo',
    notas TEXT COMMENT 'Notas especiales sobre el platillo',
    FOREIGN KEY (orden_id) REFERENCES ordenes(id),
    FOREIGN KEY (platillo_id) REFERENCES platillos(id)
) COMMENT='Detalle de platillos en cada orden';
