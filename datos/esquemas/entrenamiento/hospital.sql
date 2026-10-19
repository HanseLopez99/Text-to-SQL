-- ============================================
-- Esquema: hospital
-- Entrenamiento
-- ============================================

CREATE TABLE departamentos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del departamento',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del departamento hospitalario',
    piso INT COMMENT 'Piso donde se ubica el departamento',
    telefono VARCHAR(20) COMMENT 'Teléfono de contacto del departamento'
) COMMENT='Departamentos del hospital';

CREATE TABLE doctores (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del doctor',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del doctor',
    especialidad VARCHAR(100) NOT NULL COMMENT 'Especialidad médica del doctor',
    departamento_id INT NOT NULL COMMENT 'Departamento donde trabaja el doctor',
    telefono VARCHAR(20) COMMENT 'Teléfono de contacto del doctor',
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
) COMMENT='Doctores que trabajan en el hospital';

CREATE TABLE pacientes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del paciente',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del paciente',
    fecha_nacimiento DATE NOT NULL COMMENT 'Fecha de nacimiento del paciente',
    genero CHAR(1) COMMENT 'Género del paciente: M o F',
    telefono VARCHAR(20) COMMENT 'Teléfono de contacto del paciente',
    direccion VARCHAR(300) COMMENT 'Dirección de residencia del paciente'
) COMMENT='Pacientes atendidos en el hospital';

CREATE TABLE citas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la cita',
    paciente_id INT NOT NULL COMMENT 'Paciente que asiste a la cita',
    doctor_id INT NOT NULL COMMENT 'Doctor que atiende la cita',
    fecha_cita DATETIME NOT NULL COMMENT 'Fecha y hora de la cita',
    motivo TEXT COMMENT 'Motivo de la cita',
    estado VARCHAR(20) NOT NULL DEFAULT 'programada' COMMENT 'Estado: programada, completada, cancelada',
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
    FOREIGN KEY (doctor_id) REFERENCES doctores(id)
) COMMENT='Citas médicas programadas';

CREATE TABLE diagnosticos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del diagnóstico',
    cita_id INT NOT NULL COMMENT 'Cita en que se realizó el diagnóstico',
    paciente_id INT NOT NULL COMMENT 'Paciente diagnosticado',
    doctor_id INT NOT NULL COMMENT 'Doctor que emitió el diagnóstico',
    descripcion TEXT NOT NULL COMMENT 'Descripción del diagnóstico',
    fecha_diagnostico DATE NOT NULL COMMENT 'Fecha del diagnóstico',
    FOREIGN KEY (cita_id) REFERENCES citas(id),
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
    FOREIGN KEY (doctor_id) REFERENCES doctores(id)
) COMMENT='Diagnósticos emitidos a los pacientes';

CREATE TABLE tratamientos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del tratamiento',
    diagnostico_id INT NOT NULL COMMENT 'Diagnóstico asociado al tratamiento',
    descripcion TEXT NOT NULL COMMENT 'Descripción del tratamiento indicado',
    medicamentos TEXT COMMENT 'Medicamentos recetados en el tratamiento',
    fecha_inicio DATE NOT NULL COMMENT 'Fecha de inicio del tratamiento',
    fecha_fin DATE COMMENT 'Fecha estimada o real de finalización',
    FOREIGN KEY (diagnostico_id) REFERENCES diagnosticos(id)
) COMMENT='Tratamientos indicados para los diagnósticos';
