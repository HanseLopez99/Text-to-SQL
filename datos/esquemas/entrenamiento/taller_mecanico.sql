-- ============================================
-- Esquema: taller_mecanico
-- Entrenamiento
-- ============================================

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del cliente',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del cliente',
    telefono VARCHAR(20) COMMENT 'Teléfono de contacto del cliente',
    email VARCHAR(150) COMMENT 'Correo electrónico del cliente',
    direccion VARCHAR(300) COMMENT 'Dirección del cliente'
) COMMENT='Clientes del taller mecánico';

CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del vehículo',
    cliente_id INT NOT NULL COMMENT 'Dueño del vehículo',
    marca VARCHAR(50) NOT NULL COMMENT 'Marca del vehículo',
    modelo VARCHAR(50) NOT NULL COMMENT 'Modelo del vehículo',
    anio INT NOT NULL COMMENT 'Año de fabricación del vehículo',
    placa VARCHAR(20) NOT NULL UNIQUE COMMENT 'Placa del vehículo',
    color VARCHAR(30) COMMENT 'Color del vehículo',
    kilometraje INT COMMENT 'Kilometraje actual del vehículo',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
) COMMENT='Vehículos de los clientes del taller';

CREATE TABLE mecánicos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del mecánico',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del mecánico',
    especialidad VARCHAR(100) COMMENT 'Especialidad: motor, suspensión, eléctrica, frenos',
    telefono VARCHAR(20) COMMENT 'Teléfono de contacto'
) COMMENT='Mecánicos que trabajan en el taller';

CREATE TABLE piezas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la pieza',
    nombre VARCHAR(200) NOT NULL COMMENT 'Nombre de la pieza o repuesto',
    descripcion TEXT COMMENT 'Descripción de la pieza',
    precio DECIMAL(10,2) NOT NULL COMMENT 'Precio de la pieza en dólares',
    stock INT NOT NULL DEFAULT 0 COMMENT 'Cantidad disponible en inventario',
    proveedor VARCHAR(150) COMMENT 'Proveedor de la pieza'
) COMMENT='Piezas y repuestos disponibles en el taller';

CREATE TABLE ordenes_servicio (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la orden de servicio',
    vehiculo_id INT NOT NULL COMMENT 'Vehículo al que se le da servicio',
    mecanico_id INT NOT NULL COMMENT 'Mecánico asignado a la orden',
    fecha_ingreso DATETIME NOT NULL COMMENT 'Fecha y hora de ingreso del vehículo',
    fecha_salida DATETIME COMMENT 'Fecha y hora de salida del vehículo',
    descripcion TEXT NOT NULL COMMENT 'Descripción del trabajo solicitado',
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' COMMENT 'Estado: pendiente, en_progreso, completada, entregada',
    total DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Total de la orden de servicio',
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id),
    FOREIGN KEY (mecanico_id) REFERENCES mecanicos(id)
) COMMENT='Órdenes de servicio para los vehículos';

CREATE TABLE facturas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la factura',
    orden_id INT NOT NULL COMMENT 'Orden de servicio asociada',
    fecha_factura DATE NOT NULL COMMENT 'Fecha de emisión de la factura',
    subtotal DECIMAL(10,2) NOT NULL COMMENT 'Subtotal antes de impuestos',
    impuesto DECIMAL(10,2) NOT NULL COMMENT 'Monto del impuesto',
    total DECIMAL(10,2) NOT NULL COMMENT 'Total de la factura',
    FOREIGN KEY (orden_id) REFERENCES ordenes_servicio(id)
) COMMENT='Facturas emitidas por los servicios';
