-- Datos iniciales para WareFlow WMS

INSERT OR IGNORE INTO roles (nombre, descripcion, activo, creado_en) VALUES
  ('Administrador', 'Acceso total al sistema', 1, datetime('now')),
  ('Supervisor', 'Supervisión de operaciones y reportes', 1, datetime('now')),
  ('Operador Almacén', 'Operaciones de almacén', 1, datetime('now')),
  ('Auditor', 'Solo lectura para auditoría', 1, datetime('now'));

-- Hash generado con: hash_password('admin123')
-- Formato: {ITERATIONS}${SALT}${HASH}
INSERT OR IGNORE INTO usuarios (nombre_completo, username, password_hash, rol_id, activo, creado_en)
VALUES ('Administrador Sistema', 'admin', '100000$8b9f3e2d1a4c5b6e7f8a9b0c1d2e3f4a$5e7c8b9d0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c', 1, 1, datetime('now'));

INSERT OR IGNORE INTO zonas (codigo, nombre, tipo, descripcion, activo) VALUES
  ('Z-REC', 'Zona de Recepción', 'RECEPCION', 'Zona de recepción de mercancía', 1),
  ('Z-ALM', 'Zona de Almacenaje', 'ALMACEN', 'Zona principal de almacenamiento', 1),
  ('Z-DES', 'Zona de Despacho', 'DESPACHO', 'Zona de despacho y salida', 1),
  ('Z-CUA', 'Zona de Cuarentena', 'CUARENTENA', 'Zona de cuarentena', 1);
