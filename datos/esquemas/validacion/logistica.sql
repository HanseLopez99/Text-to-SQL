-- ============================================
-- Esquema: logistica
-- VALIDACIÓN
-- ============================================

CREATE TABLE centros_distribucion (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del centro de distribución',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre del centro de distribución',
    ciudad VARCHAR(100) NOT NULL COMMENT 'Ciudad donde se ubica el centro',
    direccion VARCHAR(300) NOT NULL COMMENT 'Dirección completa del centro',
    capacidad INT COMMENT 'Capacidad máxima de almacenamiento en unidades'
) COMMENT='Centros de distribución de la empresa logística';

CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del vehículo',
    placa VARCHAR(20) NOT NULL UNIQUE COMMENT 'Placa del vehículo',
    tipo VARCHAR(30) NOT NULL COMMENT 'Tipo de vehículo: camioneta, camión, furgoneta, moto',
    capacidad_kg DECIMAL(10,2) NOT NULL COMMENT 'Capacidad de carga en kilogramos',
    estado VARCHAR(20) NOT NULL DEFAULT 'disponible' COMMENT 'Estado: disponible, en_ruta, mantenimiento',
    centro_id INT NOT NULL COMMENT 'Centro de distribución base del vehículo',
    FOREIGN KEY (centro_id) REFERENCES centros_distribucion(id)
) COMMENT='Vehículos de la flota de la empresa';

CREATE TABLE repartidores (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del repartidor',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del repartidor',
    telefono VARCHAR(20) COMMENT 'Teléfono del repartidor',
    licencia VARCHAR(30) COMMENT 'Número de licencia de conducir',
    fecha_contratacion DATE NOT NULL COMMENT 'Fecha en que fue contratado',
    centro_id INT NOT NULL COMMENT 'Centro de distribución asignado',
    FOREIGN KEY (centro_id) REFERENCES centros_distribucion(id)
) COMMENT='Repartidores de la empresa logística';

CREATE TABLE rutas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la ruta',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre de la ruta',
    origen_id INT NOT NULL COMMENT 'Centro de distribución de origen',
    destino_ciudad VARCHAR(100) NOT NULL COMMENT 'Ciudad de destino de la ruta',
    distancia_km DECIMAL(10,2) NOT NULL COMMENT 'Distancia de la ruta en kilómetros',
    tiempo_estimado_horas DECIMAL(5,2) NOT NULL COMMENT 'Tiempo estimado de la ruta en horas',
    FOREIGN KEY (origen_id) REFERENCES centros_distribucion(id)
) COMMENT='Rutas de distribución disponibles';

CREATE TABLE paquetes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del paquete',
    remitente VARCHAR(150) NOT NULL COMMENT 'Nombre del remitente del paquete',
    destinatario VARCHAR(150) NOT NULL COMMENT 'Nombre del destinatario del paquete',
    peso_kg DECIMAL(8,2) NOT NULL COMMENT 'Peso del paquete en kilogramos',
    descripcion TEXT COMMENT 'Descripción del contenido del paquete',
    prioridad VARCHAR(10) NOT NULL DEFAULT 'normal' COMMENT 'Prioridad: baja, normal, alta, urgente',
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' COMMENT 'Estado: pendiente, en_transito, entregado, devuelto',
    fecha_envio DATE NOT NULL COMMENT 'Fecha en que se envió el paquete',
    ruta_id INT COMMENT 'Ruta asignada al paquete',
    FOREIGN KEY (ruta_id) REFERENCES rutas(id)
) COMMENT='Paquetes enviados por la empresa';

CREATE TABLE entregas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la entrega',
    paquete_id INT NOT NULL COMMENT 'Paquete entregado',
    repartidor_id INT NOT NULL COMMENT 'Repartidor que realizó la entrega',
    vehiculo_id INT NOT NULL COMMENT 'Vehículo utilizado para la entrega',
    fecha_entrega DATETIME COMMENT 'Fecha y hora en que se entregó el paquete',
    direccion_entrega VARCHAR(300) NOT NULL COMMENT 'Dirección donde se entregó el paquete',
    firmado_por VARCHAR(150) COMMENT 'Nombre de quien recibió el paquete',
    FOREIGN KEY (paquete_id) REFERENCES paquetes(id),
    FOREIGN KEY (repartidor_id) REFERENCES repartidores(id),
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id)
) COMMENT='Entregas realizadas de paquetes';
