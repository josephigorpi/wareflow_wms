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
