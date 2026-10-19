-- ============================================
-- Esquema: tienda_online
-- Entrenamiento
-- ============================================

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de categoría',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre de la categoría de productos',
    descripcion TEXT COMMENT 'Descripción de la categoría',
    activa BOOLEAN DEFAULT TRUE COMMENT 'Indica si la categoría está activa'
) COMMENT='Categorías de productos disponibles en la tienda';

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de cliente',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo del cliente',
    email VARCHAR(150) NOT NULL UNIQUE COMMENT 'Correo electrónico del cliente',
    telefono VARCHAR(20) COMMENT 'Número de teléfono del cliente',
    ciudad VARCHAR(100) COMMENT 'Ciudad de residencia del cliente',
    fecha_registro DATE NOT NULL COMMENT 'Fecha en que el cliente se registró'
) COMMENT='Clientes registrados en la tienda en línea';

CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del producto',
    nombre VARCHAR(200) NOT NULL COMMENT 'Nombre del producto',
    descripcion TEXT COMMENT 'Descripción detallada del producto',
    precio DECIMAL(10,2) NOT NULL COMMENT 'Precio unitario del producto en dólares',
    stock INT NOT NULL DEFAULT 0 COMMENT 'Cantidad disponible en inventario',
    categoria_id INT NOT NULL COMMENT 'Categoría a la que pertenece el producto',
    fecha_creacion DATE NOT NULL COMMENT 'Fecha de creación del producto en el catálogo',
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
) COMMENT='Productos disponibles para la venta';

CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del pedido',
    cliente_id INT NOT NULL COMMENT 'Cliente que realizó el pedido',
    fecha_pedido DATETIME NOT NULL COMMENT 'Fecha y hora en que se realizó el pedido',
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' COMMENT 'Estado del pedido: pendiente, enviado, entregado, cancelado',
    total DECIMAL(12,2) NOT NULL COMMENT 'Monto total del pedido',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
) COMMENT='Pedidos realizados por los clientes';

CREATE TABLE detalles_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del detalle',
    pedido_id INT NOT NULL COMMENT 'Pedido al que pertenece este detalle',
    producto_id INT NOT NULL COMMENT 'Producto comprado',
    cantidad INT NOT NULL COMMENT 'Cantidad del producto comprada',
    precio_unitario DECIMAL(10,2) NOT NULL COMMENT 'Precio unitario al momento de la compra',
    subtotal DECIMAL(12,2) NOT NULL COMMENT 'Subtotal (cantidad × precio_unitario)',
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
) COMMENT='Detalle de productos en cada pedido';

CREATE TABLE envios (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del envío',
    pedido_id INT NOT NULL COMMENT 'Pedido asociado al envío',
    direccion VARCHAR(300) NOT NULL COMMENT 'Dirección de entrega del envío',
    transportista VARCHAR(100) COMMENT 'Empresa transportista',
    fecha_envio DATE COMMENT 'Fecha en que se despachó el envío',
    fecha_entrega DATE COMMENT 'Fecha estimada o real de entrega',
    estado VARCHAR(20) NOT NULL DEFAULT 'en_transito' COMMENT 'Estado: en_transito, entregado, devuelto',
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
) COMMENT='Envíos asociados a los pedidos';
