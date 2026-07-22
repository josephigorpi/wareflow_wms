"""Script para verificar las fechas de los movimientos en la base de datos."""

from database.connection import get_connection
from datetime import datetime

conn = get_connection()
cursor = conn.cursor()

# Verificar fecha actual
today = datetime.now().strftime("%Y-%m-%d")
print(f"Fecha actual (Python): {today}")

# Verificar fechas en la base de datos
cursor.execute("""
    SELECT tipo, fecha_movimiento, DATE(fecha_movimiento) as fecha_solo
    FROM movimientos
    ORDER BY fecha_movimiento DESC
    LIMIT 20
""")

results = cursor.fetchall()
print("\nMovimientos recientes:")
for row in results:
    row_dict = dict(row)
    print(f"Tipo: {row_dict['tipo']}, Fecha completa: {row_dict['fecha_movimiento']}, Fecha solo: {row_dict['fecha_solo']}")

# Contar movimientos de hoy por tipo
cursor.execute("""
    SELECT tipo, COUNT(*) as count
    FROM movimientos
    WHERE DATE(fecha_movimiento) = ?
    GROUP BY tipo
""", (today,))

counts = cursor.fetchall()
print(f"\nConteo de movimientos de hoy ({today}):")
for row in counts:
    row_dict = dict(row)
    print(f"Tipo: {row_dict['tipo']}, Cantidad: {row_dict['count']}")

conn.close()
