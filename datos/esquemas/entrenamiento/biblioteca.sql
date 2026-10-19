-- ============================================
-- Esquema: biblioteca
-- Entrenamiento
-- ============================================

CREATE TABLE editoriales (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la editorial',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre de la editorial',
    pais VARCHAR(100) COMMENT 'País de origen de la editorial'
) COMMENT='Editoriales que publican libros';

CREATE TABLE autores (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del autor',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del autor',
    nacionalidad VARCHAR(100) COMMENT 'Nacionalidad del autor',
    fecha_nacimiento DATE COMMENT 'Fecha de nacimiento del autor'
) COMMENT='Autores de los libros de la biblioteca';

CREATE TABLE libros (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del libro',
    titulo VARCHAR(300) NOT NULL COMMENT 'Título del libro',
    isbn VARCHAR(20) UNIQUE COMMENT 'Código ISBN del libro',
    anio_publicacion INT COMMENT 'Año de publicación del libro',
    genero VARCHAR(50) COMMENT 'Género literario del libro',
    editorial_id INT COMMENT 'Editorial que publicó el libro',
    FOREIGN KEY (editorial_id) REFERENCES editoriales(id)
) COMMENT='Libros disponibles en la biblioteca';

CREATE TABLE libro_autores (
    libro_id INT NOT NULL COMMENT 'Libro escrito por el autor',
    autor_id INT NOT NULL COMMENT 'Autor del libro',
    PRIMARY KEY (libro_id, autor_id),
    FOREIGN KEY (libro_id) REFERENCES libros(id),
    FOREIGN KEY (autor_id) REFERENCES autores(id)
) COMMENT='Relación muchos a muchos entre libros y autores';

CREATE TABLE miembros (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del miembro',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre completo del miembro',
    email VARCHAR(150) UNIQUE COMMENT 'Correo electrónico del miembro',
    telefono VARCHAR(20) COMMENT 'Teléfono del miembro',
    fecha_inscripcion DATE NOT NULL COMMENT 'Fecha en que se inscribió el miembro',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Indica si el miembro está activo'
) COMMENT='Miembros registrados en la biblioteca';

CREATE TABLE prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del préstamo',
    libro_id INT NOT NULL COMMENT 'Libro prestado',
    miembro_id INT NOT NULL COMMENT 'Miembro que recibió el préstamo',
    fecha_prestamo DATE NOT NULL COMMENT 'Fecha en que se realizó el préstamo',
    fecha_devolucion DATE COMMENT 'Fecha en que se devolvió el libro',
    fecha_limite DATE NOT NULL COMMENT 'Fecha límite para devolver el libro',
    FOREIGN KEY (libro_id) REFERENCES libros(id),
    FOREIGN KEY (miembro_id) REFERENCES miembros(id)
) COMMENT='Préstamos de libros a miembros';
