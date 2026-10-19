-- ============================================
-- Esquema: gimnasio
-- Entrenamiento
-- ============================================

CREATE TABLE membresias (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la membresía',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del plan de membresía',
    duracion_meses INT NOT NULL COMMENT 'Duración del plan en meses',
    precio DECIMAL(8,2) NOT NULL COMMENT 'Precio total del plan en dólares',
    descripcion TEXT COMMENT 'Descripción de los beneficios de la membresía'
) COMMENT='Planes de membresía disponibles en el gimnasio';

CREATE TABLE miembros (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del miembro',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del miembro',
    email VARCHAR(150) UNIQUE COMMENT 'Correo electrónico del miembro',
    telefono VARCHAR(20) COMMENT 'Teléfono del miembro',
    fecha_inscripcion DATE NOT NULL COMMENT 'Fecha en que se inscribió',
    membresia_id INT NOT NULL COMMENT 'Plan de membresía contratado',
    fecha_vencimiento DATE NOT NULL COMMENT 'Fecha de vencimiento de la membresía',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Indica si la membresía está activa',
    FOREIGN KEY (membresia_id) REFERENCES membresias(id)
) COMMENT='Miembros inscritos en el gimnasio';

CREATE TABLE entrenadores (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del entrenador',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del entrenador',
    especialidad VARCHAR(100) COMMENT 'Especialidad del entrenador: pesas, cardio, yoga, crossfit',
    telefono VARCHAR(20) COMMENT 'Teléfono de contacto del entrenador'
) COMMENT='Entrenadores que trabajan en el gimnasio';

CREATE TABLE clases (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la clase',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre de la clase',
    descripcion TEXT COMMENT 'Descripción de la clase',
    entrenador_id INT NOT NULL COMMENT 'Entrenador que imparte la clase',
    dia_semana VARCHAR(10) NOT NULL COMMENT 'Día de la semana: lunes, martes, etc.',
    hora TIME NOT NULL COMMENT 'Hora de inicio de la clase',
    duracion_min INT NOT NULL COMMENT 'Duración de la clase en minutos',
    capacidad INT NOT NULL COMMENT 'Cupo máximo de la clase',
    FOREIGN KEY (entrenador_id) REFERENCES entrenadores(id)
) COMMENT='Clases grupales ofrecidas en el gimnasio';

CREATE TABLE reservas_clase (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la reserva',
    miembro_id INT NOT NULL COMMENT 'Miembro que reservó el lugar',
    clase_id INT NOT NULL COMMENT 'Clase reservada',
    fecha DATE NOT NULL COMMENT 'Fecha de la clase',
    asistio BOOLEAN DEFAULT FALSE COMMENT 'Indica si el miembro asistió a la clase',
    FOREIGN KEY (miembro_id) REFERENCES miembros(id),
    FOREIGN KEY (clase_id) REFERENCES clases(id)
) COMMENT='Reservas de miembros en clases grupales';

CREATE TABLE pagos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del pago',
    miembro_id INT NOT NULL COMMENT 'Miembro que realizó el pago',
    monto DECIMAL(8,2) NOT NULL COMMENT 'Monto pagado en dólares',
    fecha_pago DATE NOT NULL COMMENT 'Fecha en que se realizó el pago',
    metodo VARCHAR(20) NOT NULL COMMENT 'Método de pago: efectivo, tarjeta, transferencia',
    concepto VARCHAR(100) NOT NULL COMMENT 'Concepto del pago',
    FOREIGN KEY (miembro_id) REFERENCES miembros(id)
) COMMENT='Pagos realizados por los miembros del gimnasio';
