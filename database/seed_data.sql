-- Datos iniciales para WareFlow WMS
-- seed_data.sql

-- ============================================
-- 1. ROLES
-- ============================================
INSERT OR IGNORE INTO roles (nombre, descripcion, activo, creado_en) VALUES
  ('Administrador', 'Acceso total al sistema', 1, datetime('now')),
  ('Supervisor', 'Supervisión de operaciones y reportes', 1, datetime('now')),
  ('Operador Almacén', 'Operaciones de almacén', 1, datetime('now')),
  ('Auditor', 'Solo lectura para auditoría', 1, datetime('now'));

-- ============================================
-- 2. USUARIOS
-- ============================================
-- Hash generado con: python generate_password_hash.py
-- Contraseña: admin123
INSERT OR IGNORE INTO usuarios (nombre_completo, username, password_hash, email, rol_id, activo, creado_en) VALUES
  ('Administrador Sistema', 'admin', '100000$fb5bf2990ab17b3baedae08b5db0f19e$2fa1060cb4c8f24bfedef24b68beb4b4cb25596f7fb108f59aff87b5aeccf9b8', 'admin@wareflow.com', 1, 1, datetime('now'));

-- Contraseña: supervisor123
INSERT OR IGNORE INTO usuarios (nombre_completo, username, password_hash, email, rol_id, activo, creado_en) VALUES
  ('Supervisor Almacén', 'supervisor', '100000$8219308316e833f7a6659873f0f08539$8a5e001c9b3082c3987c711941c6fdb6971fb4990fcb843a6c48e6242040c058', 'supervisor@wareflow.com', 2, 1, datetime('now'));

-- Contraseña: operador123
INSERT OR IGNORE INTO usuarios (nombre_completo, username, password_hash, email, rol_id, activo, creado_en) VALUES
  ('Operador Almacén 1', 'operador1', '100000$e91e1cd2d14926f453988bf5d05f00c9$1c67f10a741829bb72489769c90d2a54a16db97e0e1b113966f02387e0115297', 'operador1@wareflow.com', 3, 1, datetime('now'));

-- Contraseña: auditor123
INSERT OR IGNORE INTO usuarios (nombre_completo, username, password_hash, email, rol_id, activo, creado_en) VALUES
  ('Auditor Inventario', 'auditor', '100000$0d864517c2b4a655feacfbdb7ad54d01$e4cab3813ec57798ace06d7e9ada0d554289452dbec13707c132ffce33f1b41c', 'auditor@wareflow.com', 4, 1, datetime('now'));

-- ============================================
-- 3. CATEGORIAS DE PRODUCTOS
-- ============================================
INSERT OR IGNORE INTO categorias_producto (nombre, descripcion, activo) VALUES
  ('Electrónicos', 'Productos electrónicos y componentes', 1),
  ('Ropa y Calzado', 'Prendas de vestir y calzado', 1),
  ('Alimentos', 'Productos alimenticios no perecederos', 1),
  ('Bebidas', 'Bebidas y líquidos', 1),
  ('Hogar', 'Artículos para el hogar', 1),
  ('Herramientas', 'Herramientas y equipos', 1),
  ('Juguetes', 'Juguetes y juegos', 1),
  ('Papelería', 'Artículos de oficina y papelería', 1);

-- ============================================
-- 4. PRODUCTOS
-- ============================================
INSERT OR IGNORE INTO productos (sku, nombre, descripcion, categoria_id, unidad_medida, peso_kg, volumen_m3, stock_minimo, stock_maximo, activo, creado_en, creado_por) VALUES
  -- Electrónicos
  ('SKU-001', 'Laptop HP ProBook', 'Laptop HP ProBook 450 G10 Intel i7', 1, 'UNIDAD', 2.2, 0.005, 5, 50, 1, datetime('now'), 1),
  ('SKU-002', 'Monitor Samsung 24"', 'Monitor Samsung LED 24 pulgadas Full HD', 1, 'UNIDAD', 3.5, 0.008, 3, 30, 1, datetime('now'), 1),
  ('SKU-003', 'Teclado Logitech', 'Teclado inalámbrico Logitech K380', 1, 'UNIDAD', 0.5, 0.001, 10, 100, 1, datetime('now'), 1),
  ('SKU-004', 'Mouse Inalámbrico', 'Mouse óptico inalámbrico Logitech M185', 1, 'UNIDAD', 0.1, 0.0005, 15, 150, 1, datetime('now'), 1),
  ('SKU-005', 'Disco Duro Externo', 'Disco duro externo WD 2TB USB 3.0', 1, 'UNIDAD', 0.3, 0.001, 5, 40, 1, datetime('now'), 1),

  -- Ropa y Calzado
  ('SKU-006', 'Camisa Polo Hombre', 'Camisa polo algodón para hombre, talla M', 2, 'UNIDAD', 0.2, 0.002, 20, 200, 1, datetime('now'), 1),
  ('SKU-007', 'Jeans Hombre', 'Jeans rectos para hombre, talle 32', 2, 'UNIDAD', 0.8, 0.004, 15, 150, 1, datetime('now'), 1),
  ('SKU-008', 'Zapatillas Running', 'Zapatillas deportivas para running, talle 42', 2, 'PAR', 0.6, 0.006, 10, 100, 1, datetime('now'), 1),
  ('SKU-009', 'Chaqueta Impermeable', 'Chaqueta impermeable para exterior', 2, 'UNIDAD', 0.9, 0.005, 5, 50, 1, datetime('now'), 1),

  -- Alimentos
  ('SKU-010', 'Arroz Blanco 5kg', 'Arroz blanco de grano largo, bolsa 5kg', 3, 'BOLSA', 5.0, 0.008, 20, 200, 1, datetime('now'), 1),
  ('SKU-011', 'Aceite Oliva 1L', 'Aceite de oliva virgen extra, botella 1L', 3, 'BOTELLA', 0.9, 0.002, 15, 120, 1, datetime('now'), 1),
  ('SKU-012', 'Harina de Trigo 1kg', 'Harina de trigo todo uso, paquete 1kg', 3, 'PAQUETE', 1.0, 0.002, 25, 250, 1, datetime('now'), 1),
  ('SKU-013', 'Lentejas 1kg', 'Lentejas secas, bolsa 1kg', 3, 'BOLSA', 1.0, 0.002, 20, 180, 1, datetime('now'), 1),

  -- Bebidas
  ('SKU-014', 'Café Molido 500g', 'Café molido premium 100% arábica', 4, 'BOLSA', 0.5, 0.001, 10, 80, 1, datetime('now'), 1),
  ('SKU-015', 'Té Verde 100g', 'Té verde en hojas, 100g', 4, 'CAJA', 0.1, 0.001, 10, 100, 1, datetime('now'), 1),
  ('SKU-016', 'Jugo de Naranja 1L', 'Jugo de naranja natural, botella 1L', 4, 'BOTELLA', 1.0, 0.001, 10, 60, 1, datetime('now'), 1),

  -- Hogar
  ('SKU-017', 'Vajilla 12 Piezas', 'Set de vajilla 12 piezas de cerámica', 5, 'SET', 8.0, 0.015, 3, 25, 1, datetime('now'), 1),
  ('SKU-018', 'Sartén Antiadherente', 'Sartén antiadherente 28cm', 5, 'UNIDAD', 1.2, 0.003, 10, 80, 1, datetime('now'), 1),
  ('SKU-019', 'Toalla de Baño', 'Toalla de baño algodón 70x140cm', 5, 'UNIDAD', 0.4, 0.003, 20, 150, 1, datetime('now'), 1),

  -- Herramientas
  ('SKU-020', 'Taladro Eléctrico', 'Taladro eléctrico 500W con accesorios', 6, 'UNIDAD', 1.5, 0.005, 3, 30, 1, datetime('now'), 1),
  ('SKU-021', 'Set de Destornilladores', 'Set 10 destornilladores de precisión', 6, 'SET', 0.3, 0.001, 8, 60, 1, datetime('now'), 1),
  ('SKU-022', 'Martillo 500g', 'Martillo de acero 500g con mango de fibra', 6, 'UNIDAD', 0.5, 0.001, 10, 70, 1, datetime('now'), 1),

  -- Juguetes
  ('SKU-023', 'LEGO City 600 piezas', 'Set LEGO City 600 piezas', 7, 'CAJA', 1.0, 0.003, 5, 40, 1, datetime('now'), 1),
  ('SKU-024', 'Muñeca Articulada', 'Muñeca articulada 30cm con accesorios', 7, 'UNIDAD', 0.4, 0.002, 10, 60, 1, datetime('now'), 1),
  ('SKU-025', 'Peluche Panda 50cm', 'Peluche de panda gigante 50cm', 7, 'UNIDAD', 0.6, 0.008, 8, 50, 1, datetime('now'), 1),

  -- Papelería
  ('SKU-026', 'Resma Papel A4', 'Resma de papel A4 500 hojas 80g', 8, 'RESMA', 2.5, 0.004, 15, 120, 1, datetime('now'), 1),
  ('SKU-027', 'Bolígrafos x12', 'Caja de 12 bolígrafos de tinta azul', 8, 'CAJA', 0.1, 0.0005, 20, 200, 1, datetime('now'), 1),
  ('SKU-028', 'Cuaderno Universitario', 'Cuaderno universitario 100 hojas cuadriculado', 8, 'UNIDAD', 0.3, 0.001, 30, 300, 1, datetime('now'), 1);

-- ============================================
-- 5. ZONAS
-- ============================================
INSERT OR IGNORE INTO zonas (codigo, nombre, tipo, descripcion, activo) VALUES
  ('Z-REC', 'Zona de Recepción', 'RECEPCION', 'Zona de recepción de mercancía', 1),
  ('Z-ALM', 'Zona de Almacenaje', 'ALMACEN', 'Zona principal de almacenamiento', 1),
  ('Z-DES', 'Zona de Despacho', 'DESPACHO', 'Zona de despacho y salida', 1),
  ('Z-CUA', 'Zona de Cuarentena', 'CUARENTENA', 'Zona de cuarentena y productos en revisión', 1),
  ('Z-REF', 'Zona de Refrigeración', 'REFRIGERACION', 'Zona de productos refrigerados', 1),
  ('Z-CON', 'Zona de Consolidación', 'CONSOLIDACION', 'Zona para consolidación de pedidos', 1);

-- ============================================
-- 6. UBICACIONES
-- ============================================
-- Zona de Almacenaje (Z-ALM)
INSERT OR IGNORE INTO ubicaciones (codigo, zona_id, pasillo, estante, nivel, posicion, capacidad_kg, capacidad_m3, ocupada, activo) VALUES
  ('A-01-01', 2, 'A', '01', '01', '01', 100.0, 0.5, 0, 1),
  ('A-01-02', 2, 'A', '01', '01', '02', 100.0, 0.5, 0, 1),
  ('A-01-03', 2, 'A', '01', '01', '03', 100.0, 0.5, 0, 1),
  ('A-01-04', 2, 'A', '01', '01', '04', 100.0, 0.5, 0, 1),
  ('A-01-05', 2, 'A', '01', '01', '05', 100.0, 0.5, 0, 1),
  ('A-01-06', 2, 'A', '01', '01', '06', 100.0, 0.5, 0, 1),
  ('A-02-01', 2, 'A', '02', '01', '01', 150.0, 0.8, 0, 1),
  ('A-02-02', 2, 'A', '02', '01', '02', 150.0, 0.8, 0, 1),
  ('A-02-03', 2, 'A', '02', '01', '03', 150.0, 0.8, 0, 1),
  ('A-02-04', 2, 'A', '02', '01', '04', 150.0, 0.8, 0, 1),
  ('B-01-01', 2, 'B', '01', '01', '01', 200.0, 1.0, 0, 1),
  ('B-01-02', 2, 'B', '01', '01', '02', 200.0, 1.0, 0, 1),
  ('B-01-03', 2, 'B', '01', '01', '03', 200.0, 1.0, 0, 1),
  ('B-01-04', 2, 'B', '01', '01', '04', 200.0, 1.0, 0, 1),
  ('B-02-01', 2, 'B', '02', '01', '01', 150.0, 0.7, 0, 1),
  ('B-02-02', 2, 'B', '02', '01', '02', 150.0, 0.7, 0, 1),
  ('B-02-03', 2, 'B', '02', '01', '03', 150.0, 0.7, 0, 1),
  ('B-02-04', 2, 'B', '02', '01', '04', 150.0, 0.7, 0, 1),
  ('C-01-01', 2, 'C', '01', '01', '01', 300.0, 1.5, 0, 1),
  ('C-01-02', 2, 'C', '01', '01', '02', 300.0, 1.5, 0, 1),
  ('C-01-03', 2, 'C', '01', '01', '03', 300.0, 1.5, 0, 1),
  ('C-02-01', 2, 'C', '02', '01', '01', 250.0, 1.2, 0, 1),
  ('C-02-02', 2, 'C', '02', '01', '02', 250.0, 1.2, 0, 1),
  ('C-02-03', 2, 'C', '02', '01', '03', 250.0, 1.2, 0, 1),
  ('D-01-01', 2, 'D', '01', '01', '01', 120.0, 0.6, 0, 1),
  ('D-01-02', 2, 'D', '01', '01', '02', 120.0, 0.6, 0, 1),
  ('D-01-03', 2, 'D', '01', '01', '03', 120.0, 0.6, 0, 1),
  ('D-02-01', 2, 'D', '02', '01', '01', 180.0, 0.9, 0, 1),
  ('D-02-02', 2, 'D', '02', '01', '02', 180.0, 0.9, 0, 1),
  ('D-02-03', 2, 'D', '02', '01', '03', 180.0, 0.9, 0, 1),
  ('E-01-01', 2, 'E', '01', '01', '01', 100.0, 0.5, 0, 1),
  ('E-01-02', 2, 'E', '01', '01', '02', 100.0, 0.5, 0, 1),
  ('E-01-03', 2, 'E', '01', '01', '03', 100.0, 0.5, 0, 1),
  ('E-02-01', 2, 'E', '02', '01', '01', 150.0, 0.7, 0, 1),
  ('E-02-02', 2, 'E', '02', '01', '02', 150.0, 0.7, 0, 1),
  ('E-02-03', 2, 'E', '02', '01', '03', 150.0, 0.7, 0, 1);

-- Zona de Recepción (Z-REC)
INSERT OR IGNORE INTO ubicaciones (codigo, zona_id, pasillo, estante, nivel, posicion, capacidad_kg, capacidad_m3, ocupada, activo) VALUES
  ('REC-01', 1, 'REC', '01', '01', '01', 500.0, 2.0, 0, 1),
  ('REC-02', 1, 'REC', '01', '01', '02', 500.0, 2.0, 0, 1),
  ('REC-03', 1, 'REC', '01', '01', '03', 500.0, 2.0, 0, 1);

-- Zona de Despacho (Z-DES)
INSERT OR IGNORE INTO ubicaciones (codigo, zona_id, pasillo, estante, nivel, posicion, capacidad_kg, capacidad_m3, ocupada, activo) VALUES
  ('DES-01', 3, 'DES', '01', '01', '01', 400.0, 1.8, 0, 1),
  ('DES-02', 3, 'DES', '01', '01', '02', 400.0, 1.8, 0, 1),
  ('DES-03', 3, 'DES', '01', '01', '03', 400.0, 1.8, 0, 1);

-- Zona de Cuarentena (Z-CUA)
INSERT OR IGNORE INTO ubicaciones (codigo, zona_id, pasillo, estante, nivel, posicion, capacidad_kg, capacidad_m3, ocupada, activo) VALUES
  ('CUA-01', 4, 'CUA', '01', '01', '01', 200.0, 1.0, 0, 1),
  ('CUA-02', 4, 'CUA', '01', '01', '02', 200.0, 1.0, 0, 1);

-- Zona de Refrigeración (Z-REF)
INSERT OR IGNORE INTO ubicaciones (codigo, zona_id, pasillo, estante, nivel, posicion, capacidad_kg, capacidad_m3, ocupada, activo) VALUES
  ('REF-01', 5, 'REF', '01', '01', '01', 150.0, 0.8, 0, 1),
  ('REF-02', 5, 'REF', '01', '01', '02', 150.0, 0.8, 0, 1);

-- Zona de Consolidación (Z-CON)
INSERT OR IGNORE INTO ubicaciones (codigo, zona_id, pasillo, estante, nivel, posicion, capacidad_kg, capacidad_m3, ocupada, activo) VALUES
  ('CON-01', 6, 'CON', '01', '01', '01', 300.0, 1.5, 0, 1),
  ('CON-02', 6, 'CON', '01', '01', '02', 300.0, 1.5, 0, 1);

-- ============================================
-- 7. INVENTARIO INICIAL
-- ============================================
-- Productos con stock inicial en la zona de almacenaje
INSERT OR IGNORE INTO inventario (producto_id, ubicacion_id, cantidad, lote, fecha_vencimiento, actualizado_en, actualizado_por) VALUES
  -- Electrónicos
  (1, 1, 15, 'LOTE-2024-001', NULL, datetime('now'), 1),
  (2, 2, 8, 'LOTE-2024-002', NULL, datetime('now'), 1),
  (3, 3, 50, 'LOTE-2024-003', NULL, datetime('now'), 1),
  (4, 4, 80, 'LOTE-2024-004', NULL, datetime('now'), 1),
  (5, 5, 12, 'LOTE-2024-005', NULL, datetime('now'), 1),
  
  -- Ropa y Calzado
  (6, 7, 45, 'LOTE-2024-006', NULL, datetime('now'), 1),
  (7, 8, 30, 'LOTE-2024-007', NULL, datetime('now'), 1),
  (8, 9, 20, 'LOTE-2024-008', NULL, datetime('now'), 1),
  (9, 10, 8, 'LOTE-2024-009', NULL, datetime('now'), 1),
  
  -- Alimentos
  (10, 11, 60, 'LOTE-2024-010', '2025-12-31', datetime('now'), 1),
  (11, 12, 35, 'LOTE-2024-011', '2025-10-15', datetime('now'), 1),
  (12, 13, 80, 'LOTE-2024-012', '2025-09-30', datetime('now'), 1),
  (13, 14, 55, 'LOTE-2024-013', '2025-11-20', datetime('now'), 1),
  
  -- Bebidas
  (14, 15, 25, 'LOTE-2024-014', '2025-08-15', datetime('now'), 1),
  (15, 16, 40, 'LOTE-2024-015', '2025-07-30', datetime('now'), 1),
  (16, 17, 20, 'LOTE-2024-016', '2024-12-15', datetime('now'), 1),
  
  -- Hogar
  (17, 19, 10, 'LOTE-2024-017', NULL, datetime('now'), 1),
  (18, 20, 25, 'LOTE-2024-018', NULL, datetime('now'), 1),
  (19, 21, 60, 'LOTE-2024-019', NULL, datetime('now'), 1),
  
  -- Herramientas
  (20, 22, 8, 'LOTE-2024-020', NULL, datetime('now'), 1),
  (21, 23, 30, 'LOTE-2024-021', NULL, datetime('now'), 1),
  (22, 24, 25, 'LOTE-2024-022', NULL, datetime('now'), 1),
  
  -- Juguetes
  (23, 25, 15, 'LOTE-2024-023', NULL, datetime('now'), 1),
  (24, 26, 25, 'LOTE-2024-024', NULL, datetime('now'), 1),
  (25, 27, 20, 'LOTE-2024-025', NULL, datetime('now'), 1),
  
  -- Papelería
  (26, 28, 40, 'LOTE-2024-026', NULL, datetime('now'), 1),
  (27, 29, 80, 'LOTE-2024-027', NULL, datetime('now'), 1),
  (28, 30, 100, 'LOTE-2024-028', NULL, datetime('now'), 1);

-- ============================================
-- 8. MOVIMIENTOS INICIALES
-- ============================================
-- Registro de movimientos de entrada inicial
INSERT OR IGNORE INTO movimientos (tipo, producto_id, ubicacion_destino_id, cantidad, referencia, observaciones, estado, usuario_id, fecha_movimiento) VALUES
  -- Entradas de productos electrónicos
  ('ENTRADA', 1, 1, 15, 'OC-001-2024', 'Recepción inicial de laptops', 'COMPLETADO', 1, datetime('now', '-30 days')),
  ('ENTRADA', 2, 2, 8, 'OC-002-2024', 'Recepción inicial de monitores', 'COMPLETADO', 1, datetime('now', '-28 days')),
  ('ENTRADA', 3, 3, 50, 'OC-003-2024', 'Recepción inicial de teclados', 'COMPLETADO', 1, datetime('now', '-25 days')),
  ('ENTRADA', 4, 4, 80, 'OC-004-2024', 'Recepción inicial de mouses', 'COMPLETADO', 1, datetime('now', '-22 days')),
  ('ENTRADA', 5, 5, 12, 'OC-005-2024', 'Recepción inicial de discos duros', 'COMPLETADO', 1, datetime('now', '-20 days')),
  
  -- Entradas de ropa y calzado
  ('ENTRADA', 6, 7, 45, 'OC-006-2024', 'Recepción inicial de camisas', 'COMPLETADO', 1, datetime('now', '-18 days')),
  ('ENTRADA', 7, 8, 30, 'OC-007-2024', 'Recepción inicial de jeans', 'COMPLETADO', 1, datetime('now', '-15 days')),
  ('ENTRADA', 8, 9, 20, 'OC-008-2024', 'Recepción inicial de zapatillas', 'COMPLETADO', 1, datetime('now', '-12 days')),
  
  -- Entradas de alimentos
  ('ENTRADA', 10, 11, 60, 'OC-009-2024', 'Recepción inicial de arroz', 'COMPLETADO', 1, datetime('now', '-10 days')),
  ('ENTRADA', 11, 12, 35, 'OC-010-2024', 'Recepción inicial de aceite', 'COMPLETADO', 1, datetime('now', '-8 days')),
  ('ENTRADA', 12, 13, 80, 'OC-011-2024', 'Recepción inicial de harina', 'COMPLETADO', 1, datetime('now', '-6 days')),
  
  -- Entradas de bebidas
  ('ENTRADA', 14, 15, 25, 'OC-012-2024', 'Recepción inicial de café', 'COMPLETADO', 1, datetime('now', '-5 days')),
  ('ENTRADA', 15, 16, 40, 'OC-013-2024', 'Recepción inicial de té', 'COMPLETADO', 1, datetime('now', '-4 days')),
  
  -- Entradas de hogar
  ('ENTRADA', 17, 19, 10, 'OC-014-2024', 'Recepción inicial de vajilla', 'COMPLETADO', 1, datetime('now', '-3 days')),
  ('ENTRADA', 18, 20, 25, 'OC-015-2024', 'Recepción inicial de sartenes', 'COMPLETADO', 1, datetime('now', '-2 days')),

  -- Movimientos de salida (ejemplo de despachos)
  ('SALIDA', 1, NULL, 2, 'PED-001-2024', 'Venta de laptops', 'COMPLETADO', 1, datetime('now', '-15 days')),
  ('SALIDA', 3, NULL, 10, 'PED-002-2024', 'Venta de teclados', 'COMPLETADO', 1, datetime('now', '-10 days')),
  ('SALIDA', 6, NULL, 5, 'PED-003-2024', 'Venta de camisas', 'COMPLETADO', 1, datetime('now', '-7 days')),
  ('SALIDA', 10, NULL, 10, 'PED-004-2024', 'Venta de arroz', 'COMPLETADO', 1, datetime('now', '-5 days'));

-- ============================================
-- 9. REGISTROS DE SESIÓN (ejemplos)
-- ============================================
INSERT OR IGNORE INTO sesiones_log (usuario_id, accion, ip_address, fecha_hora, detalle) VALUES
  (1, 'LOGIN', '192.168.1.100', datetime('now', '-30 days'), 'Inicio de sesión desde administrador'),
  (1, 'CREAR_PRODUCTO', '192.168.1.100', datetime('now', '-25 days'), 'Creación de producto: Laptop HP ProBook'),
  (1, 'CREAR_UBICACION', '192.168.1.100', datetime('now', '-20 days'), 'Creación de ubicaciones en zona de almacenaje'),
  (2, 'LOGIN', '192.168.1.101', datetime('now', '-18 days'), 'Inicio de sesión desde supervisor'),
  (2, 'REVISION_INVENTARIO', '192.168.1.101', datetime('now', '-15 days'), 'Revisión de inventario general'),
  (3, 'LOGIN', '192.168.1.102', datetime('now', '-12 days'), 'Inicio de sesión desde operador'),
  (3, 'MOVIMIENTO_ENTRADA', '192.168.1.102', datetime('now', '-10 days'), 'Registro de movimiento de entrada'),
  (4, 'LOGIN', '192.168.1.103', datetime('now', '-8 days'), 'Inicio de sesión desde auditor'),
  (4, 'AUDITORIA_INVENTARIO', '192.168.1.103', datetime('now', '-5 days'), 'Auditoría de inventario realizada');
