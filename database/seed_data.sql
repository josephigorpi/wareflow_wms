-- Datos iniciales para WareFlow WMS

INSERT OR IGNORE INTO roles (nombre, descripcion, activo, creado_en) VALUES
  ('Administrador', 'Acceso total al sistema', 1, datetime('now')),
  ('Supervisor', 'Supervisión de operaciones y reportes', 1, datetime('now')),
  ('Operador Almacén', 'Operaciones de almacén', 1, datetime('now')),
  ('Auditor', 'Solo lectura para auditoría', 1, datetime('now'));

-- Hash generado con: python generate_password_hash.py
-- Contraseña: admin123
INSERT OR IGNORE INTO usuarios (nombre_completo, username, password_hash, rol_id, activo, creado_en)
VALUES ('Administrador Sistema', 'admin', '100000$fb5bf2990ab17b3baedae08b5db0f19e$2fa1060cb4c8f24bfedef24b68beb4b4cb25596f7fb108f59aff87b5aeccf9b8', 1, 1, datetime('now'));

INSERT OR IGNORE INTO zonas (codigo, nombre, tipo, descripcion, activo) VALUES
  ('Z-REC', 'Zona de Recepción', 'RECEPCION', 'Zona de recepción de mercancía', 1),
  ('Z-ALM', 'Zona de Almacenaje', 'ALMACEN', 'Zona principal de almacenamiento', 1),
  ('Z-DES', 'Zona de Despacho', 'DESPACHO', 'Zona de despacho y salida', 1),
  ('Z-CUA', 'Zona de Cuarentena', 'CUARENTENA', 'Zona de cuarentena', 1);

INSERT OR IGNORE INTO categorias_producto (nombre, descripcion, activo) VALUES
  ('Electrónica', 'Productos electrónicos', 1),
  ('Alimentos', 'Productos alimenticios', 1),
  ('Ropa', 'Prendas de vestir', 1);

INSERT OR IGNORE INTO productos (sku, nombre, descripcion, categoria_id, unidad_medida, peso_kg, volumen_m3, stock_minimo, stock_maximo, activo, creado_en) VALUES
  ('SKU-001', 'Laptop X1', 'Laptop de alta gama', 1, 'Unidad', 2.5, 0.01, 5, 50, 1, datetime('now')),
  ('SKU-002', 'Mouse Inalámbrico', 'Mouse para computadora', 1, 'Unidad', 0.2, 0.001, 10, 100, 1, datetime('now')),
  ('SKU-003', 'Café Molido', 'Café molido 500g', 2, 'Bolsa', 0.5, 0.0005, 20, 100, 1, datetime('now'));

INSERT OR IGNORE INTO ubicaciones (codigo, zona_id, pasillo, estante, nivel, posicion, capacidad_kg, capacidad_m3, ocupada, activo) VALUES
  ('REC-01', 1, 'R01', 'E01', 'N1', 'P01', 500, 2, 0, 1),
  ('ALM-A01', 2, 'A01', 'E01', 'N1', 'P01', 1000, 5, 0, 1),
  ('ALM-A02', 2, 'A01', 'E01', 'N1', 'P02', 1000, 5, 0, 1),
  ('CUA-01', 4, 'C01', 'E01', 'N1', 'P01', 200, 1, 0, 1);
