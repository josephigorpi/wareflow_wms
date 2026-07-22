"""Script para eliminar movimientos con fechas incorrectas y recargar los datos."""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# Eliminar movimientos con fecha 2026-07-22 (mañana)
cursor.execute("DELETE FROM movimientos WHERE DATE(fecha_movimiento) = '2026-07-22'")
deleted = cursor.rowcount
conn.commit()

print(f"Eliminados {deleted} movimientos con fecha incorrecta.")
conn.close()

# Recargar los datos de prueba
from database.db_manager import execute_script
print("Recargando datos de prueba...")
execute_script("database/seed_data.sql")
print("✅ Datos recargados exitosamente.")
