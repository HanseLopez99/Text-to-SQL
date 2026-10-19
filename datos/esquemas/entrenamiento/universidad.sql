-- ============================================
-- Esquema: universidad
-- Entrenamiento
-- ============================================

CREATE TABLE departamentos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del departamento académico',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del departamento',
    edificio VARCHAR(100) COMMENT 'Edificio donde se ubica el departamento',
    director VARCHAR(150) COMMENT 'Nombre del director del departamento'
) COMMENT='Departamentos académicos de la universidad';

CREATE TABLE profesores (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del profesor',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del profesor',
    email VARCHAR(150) UNIQUE COMMENT 'Correo electrónico institucional',
    departamento_id INT NOT NULL COMMENT 'Departamento al que pertenece',
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
) COMMENT='Profesores de la universidad';

CREATE TABLE estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del estudiante',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del estudiante',
    email VARCHAR(150) UNIQUE COMMENT 'Correo electrónico institucional',
    fecha_ingreso DATE NOT NULL COMMENT 'Fecha de ingreso a la universidad',
    carrera VARCHAR(100) NOT NULL COMMENT 'Carrera que estudia el estudiante',
    promedio DECIMAL(3,2) COMMENT 'Promedio acumulado del estudiante'
) COMMENT='Estudiantes matriculados en la universidad';

CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del curso',
    codigo VARCHAR(20) NOT NULL UNIQUE COMMENT 'Código asignado al curso',
    nombre VARCHAR(200) NOT NULL COMMENT 'Nombre del curso',
    creditos INT NOT NULL COMMENT 'Número de créditos del curso',
    departamento_id INT NOT NULL COMMENT 'Departamento que ofrece el curso',
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
) COMMENT='Cursos ofrecidos por la universidad';

CREATE TABLE inscripciones (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la inscripción',
    estudiante_id INT NOT NULL COMMENT 'Estudiante inscrito',
    curso_id INT NOT NULL COMMENT 'Curso en el que se inscribió',
    profesor_id INT NOT NULL COMMENT 'Profesor que imparte el curso',
    semestre VARCHAR(20) NOT NULL COMMENT 'Semestre en que se toma el curso',
    calificacion DECIMAL(3,2) COMMENT 'Calificación obtenida por el estudiante',
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (curso_id) REFERENCES cursos(id),
    FOREIGN KEY (profesor_id) REFERENCES profesores(id)
) COMMENT='Inscripciones de estudiantes en cursos';
