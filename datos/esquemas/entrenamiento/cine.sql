-- ============================================
-- Esquema: cine
-- Entrenamiento
-- ============================================

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del cliente',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del cliente',
    email VARCHAR(150) UNIQUE COMMENT 'Correo electrónico del cliente',
    telefono VARCHAR(20) COMMENT 'Teléfono del cliente',
    fecha_registro DATE NOT NULL COMMENT 'Fecha en que se registró el cliente'
) COMMENT='Clientes que compran boletos en el cine';

CREATE TABLE peliculas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la película',
    titulo VARCHAR(200) NOT NULL COMMENT 'Título de la película',
    genero VARCHAR(50) NOT NULL COMMENT 'Género de la película: acción, comedia, drama, terror, etc.',
    duracion_min INT NOT NULL COMMENT 'Duración de la película en minutos',
    clasificacion VARCHAR(10) NOT NULL COMMENT 'Clasificación por edades: A, B, C, D',
    idioma VARCHAR(30) NOT NULL COMMENT 'Idioma original de la película',
    fecha_estreno DATE NOT NULL COMMENT 'Fecha de estreno de la película'
) COMMENT='Películas en cartelera en el cine';

CREATE TABLE salas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la sala',
    numero INT NOT NULL UNIQUE COMMENT 'Número de la sala',
    capacidad INT NOT NULL COMMENT 'Cantidad de asientos de la sala',
    tipo VARCHAR(30) NOT NULL COMMENT 'Tipo de sala: 2D, 3D, IMAX, VIP'
) COMMENT='Salas de proyección del cine';

CREATE TABLE funciones (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la función',
    pelicula_id INT NOT NULL COMMENT 'Película que se proyecta',
    sala_id INT NOT NULL COMMENT 'Sala donde se proyecta',
    fecha_hora DATETIME NOT NULL COMMENT 'Fecha y hora de la función',
    precio DECIMAL(8,2) NOT NULL COMMENT 'Precio del boleto para esta función',
    FOREIGN KEY (pelicula_id) REFERENCES peliculas(id),
    FOREIGN KEY (sala_id) REFERENCES salas(id)
) COMMENT='Funciones de proyección programadas';

CREATE TABLE boletos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del boleto',
    funcion_id INT NOT NULL COMMENT 'Función para la que se compró el boleto',
    cliente_id INT COMMENT 'Cliente que compró el boleto',
    asiento VARCHAR(5) NOT NULL COMMENT 'Identificador del asiento',
    precio DECIMAL(8,2) NOT NULL COMMENT 'Precio pagado por el boleto',
    fecha_compra DATETIME NOT NULL COMMENT 'Fecha y hora de la compra',
    FOREIGN KEY (funcion_id) REFERENCES funciones(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
) COMMENT='Boletos vendidos para las funciones';

CREATE TABLE promociones (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la promoción',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre de la promoción',
    descripcion TEXT COMMENT 'Descripción de la promoción',
    descuento DECIMAL(5,2) NOT NULL COMMENT 'Porcentaje de descuento',
    fecha_inicio DATE NOT NULL COMMENT 'Fecha de inicio de la promoción',
    fecha_fin DATE NOT NULL COMMENT 'Fecha de finalización de la promoción',
    activa BOOLEAN DEFAULT TRUE COMMENT 'Indica si la promoción está vigente'
) COMMENT='Promociones disponibles en el cine';
