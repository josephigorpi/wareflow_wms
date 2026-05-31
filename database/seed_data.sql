-- Datos iniciales para WareFlow WMS

INSERT OR IGNORE INTO roles (nombre, descripcion, activo, creado_en) VALUES
  ('Administrador', 'Acceso total al sistema', 1, datetime('now')),
  ('Supervisor', 'Supervisión de operaciones y reportes', 1, datetime('now')),
  ('Operador Almacén', 'Operaciones de almacén', 1, datetime('now')),
  ('Auditor', 'Solo lectura para auditoría', 1, datetime('now'));

-- El hash de contraseña debe generarse en tiempo de inicialización.
-- Contraseña por defecto: admin123. Cambiar en producción.
INSERT OR IGNORE INTO usuarios (nombre_completo, username, password_hash, rol_id, activo, creado_en)
VALUES ('Administrador Sistema', 'admin', '1000006e5d07d815052e9db8a82cfd060d3d7e4003aa8669e4ba8875f3bcc85f9a9f5976ae2225b8bbef9262676cc71364778a', 1, 1, datetime('now'));

INSERT OR IGNORE INTO zonas (codigo, nombre, tipo, descripcion, activo) VALUES
  ('Z-REC', 'Zona de Recepción', 'RECEPCION', 'Zona de recepción de mercancía', 1),
  ('Z-ALM', 'Zona de Almacenaje', 'ALMACEN', 'Zona principal de almacenamiento', 1),
  ('Z-DES', 'Zona de Despacho', 'DESPACHO', 'Zona de despacho y salida', 1),
  ('Z-CUA', 'Zona de Cuarentena', 'CUARENTENA', 'Zona de cuarentena', 1);
