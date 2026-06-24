-- DDL completo del esquema del núcleo compartido WareFlow WMS

-- Tabla roles
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    activo INTEGER NOT NULL DEFAULT 1,
    creado_en TEXT NOT NULL
);

-- Tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE,
    rol_id INTEGER,
    activo INTEGER NOT NULL DEFAULT 1,
    creado_en TEXT NOT NULL,
    ultimo_acceso TEXT,
    FOREIGN KEY (rol_id) REFERENCES roles(id)
);

-- Tabla categorias_producto
CREATE TABLE IF NOT EXISTS categorias_producto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    activo INTEGER DEFAULT 1
);

-- Tabla productos
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    categoria_id INTEGER,
    unidad_medida TEXT NOT NULL,
    peso_kg REAL,
    volumen_m3 REAL,
    stock_minimo INTEGER DEFAULT 0,
    stock_maximo INTEGER,
    activo INTEGER DEFAULT 1,
    creado_en TEXT NOT NULL,
    creado_por INTEGER,
    FOREIGN KEY (categoria_id) REFERENCES categorias_producto(id),
    FOREIGN KEY (creado_por) REFERENCES usuarios(id)
);

-- Tabla zonas
CREATE TABLE IF NOT EXISTS zonas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,
    descripcion TEXT,
    activo INTEGER DEFAULT 1
);

-- Tabla ubicaciones
CREATE TABLE IF NOT EXISTS ubicaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    zona_id INTEGER,
    pasillo TEXT NOT NULL,
    estante TEXT NOT NULL,
    nivel TEXT NOT NULL,
    posicion TEXT NOT NULL,
    capacidad_kg REAL,
    capacidad_m3 REAL,
    ocupada INTEGER DEFAULT 0,
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (zona_id) REFERENCES zonas(id)
);

-- Tabla inventario
CREATE TABLE IF NOT EXISTS inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER,
    ubicacion_id INTEGER,
    cantidad INTEGER NOT NULL DEFAULT 0,
    lote TEXT,
    fecha_vencimiento TEXT,
    actualizado_en TEXT NOT NULL,
    actualizado_por INTEGER,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (ubicacion_id) REFERENCES ubicaciones(id),
    FOREIGN KEY (actualizado_por) REFERENCES usuarios(id),
    UNIQUE (producto_id, ubicacion_id, lote)
);

-- Tabla movimientos
CREATE TABLE IF NOT EXISTS movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    producto_id INTEGER,
    ubicacion_origen_id INTEGER,
    ubicacion_destino_id INTEGER,
    cantidad INTEGER NOT NULL,
    referencia TEXT,
    observaciones TEXT,
    estado TEXT DEFAULT 'PENDIENTE',
    usuario_id INTEGER,
    fecha_movimiento TEXT NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (ubicacion_origen_id) REFERENCES ubicaciones(id),
    FOREIGN KEY (ubicacion_destino_id) REFERENCES ubicaciones(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla sesiones_log
CREATE TABLE IF NOT EXISTS sesiones_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    accion TEXT NOT NULL,
    ip_address TEXT,
    fecha_hora TEXT NOT NULL,
    detalle TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    contacto TEXT,
    telefono TEXT,
    email TEXT,
    ciudad TEXT,
    direccion TEXT,
    activo INTEGER DEFAULT 1,
    creado_en TEXT NOT NULL
);

-- Tabla ordenes_compra
CREATE TABLE IF NOT EXISTS ordenes_compra (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_oc TEXT NOT NULL UNIQUE,
    proveedor_id INTEGER NOT NULL,
    fecha_emision TEXT NOT NULL,
    fecha_entrega_esperada TEXT NOT NULL,
    estado TEXT DEFAULT 'PENDIENTE',
    total_items INTEGER DEFAULT 0,
    creado_en TEXT NOT NULL,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

-- Tabla ordenes_compra_items
CREATE TABLE IF NOT EXISTS ordenes_compra_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_compra_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad_ordenada INTEGER NOT NULL,
    cantidad_recibida INTEGER DEFAULT 0,
    precio_unitario REAL,
    FOREIGN KEY (orden_compra_id) REFERENCES ordenes_compra(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Tabla anomalias_inspeccion
CREATE TABLE IF NOT EXISTS anomalias_inspeccion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movimiento_id INTEGER NOT NULL,
    tipo_anomalia TEXT NOT NULL,
    cantidad_danada INTEGER DEFAULT 0,
    severidad TEXT NOT NULL,
    descripcion TEXT,
    foto_path TEXT,
    registrado_en TEXT NOT NULL,
    FOREIGN KEY (movimiento_id) REFERENCES movimientos(id)
);

-- Alter table movimientos para agregar referencias a proveedor y OC
ALTER TABLE movimientos ADD COLUMN proveedor_id INTEGER;
ALTER TABLE movimientos ADD COLUMN orden_compra_id INTEGER;
ALTER TABLE movimientos ADD COLUMN hora_movimiento TEXT;
