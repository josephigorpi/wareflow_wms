"""Script para crear productos con stock bajo y próximos a vencer."""

from database.connection import get_connection
from datetime import datetime, timedelta

conn = get_connection()
cursor = conn.cursor()

# Fecha actual
today = datetime.now()
date_30_days = today + timedelta(days=30)
date_15_days = today + timedelta(days=15)
date_7_days = today + timedelta(days=7)

# Reducir stock de algunos productos para que estén por debajo del mínimo
updates = [
    # SKU-002: Monitor Samsung - reducir de 8 a 2 (mínimo: 3)
    ("UPDATE inventario SET cantidad = 2 WHERE producto_id = 2", 2),
    # SKU-005: Disco Duro - reducir de 12 a 3 (mínimo: 5)
    ("UPDATE inventario SET cantidad = 3 WHERE producto_id = 5", 3),
    # SKU-009: Chaqueta Impermeable - reducir de 8 a 2 (mínimo: 5)
    ("UPDATE inventario SET cantidad = 2 WHERE producto_id = 9", 2),
    # SKU-017: Vajilla - reducir de 10 a 1 (mínimo: 3)
    ("UPDATE inventario SET cantidad = 1 WHERE producto_id = 17", 1),
    # SKU-020: Taladro - reducir de 8 a 1 (mínimo: 3)
    ("UPDATE inventario SET cantidad = 1 WHERE producto_id = 20", 1),
    # SKU-023: LEGO - reducir de 15 a 2 (mínimo: 5)
    ("UPDATE inventario SET cantidad = 2 WHERE producto_id = 23", 2),
]

# Actualizar fechas de vencimiento para productos próximos a vencer
vencimiento_updates = [
    # SKU-011: Aceite Oliva - vence en 30 días
    ("UPDATE inventario SET fecha_vencimiento = ? WHERE producto_id = 11", (date_30_days.strftime("%Y-%m-%d"),)),
    # SKU-012: Harina - vence en 15 días
    ("UPDATE inventario SET fecha_vencimiento = ? WHERE producto_id = 12", (date_15_days.strftime("%Y-%m-%d"),)),
    # SKU-016: Jugo de Naranja - vence en 7 días
    ("UPDATE inventario SET fecha_vencimiento = ? WHERE producto_id = 16", (date_7_days.strftime("%Y-%m-%d"),)),
    # SKU-014: Café - vence en 30 días
    ("UPDATE inventario SET fecha_vencimiento = ? WHERE producto_id = 14", (date_30_days.strftime("%Y-%m-%d"),)),
]

try:
    # Ejecutar actualizaciones de stock
    for query, expected in updates:
        cursor.execute(query)
        print(f"Stock actualizado: {cursor.rowcount} filas afectadas")
    
    # Ejecutar actualizaciones de vencimiento
    for query, params in vencimiento_updates:
        cursor.execute(query, params)
        print(f"Vencimiento actualizado: {cursor.rowcount} filas afectadas")
    
    conn.commit()
    print("\n✅ Datos de stock bajo y próximos a vencer creados exitosamente.")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
finally:
    conn.close()

# Verificar los resultados
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT p.sku, p.nombre, i.cantidad, p.stock_minimo, i.fecha_vencimiento,
           CASE WHEN i.cantidad <= p.stock_minimo THEN 'STOCK BAJO' ELSE 'OK' END as estado_stock,
           CASE WHEN i.fecha_vencimiento IS NOT NULL AND DATE(i.fecha_vencimiento) <= DATE('now', '+30 days') 
                THEN 'PRÓXIMO A VENCER' ELSE 'OK' END as estado_vencimiento
    FROM inventario i
    JOIN productos p ON i.producto_id = p.id
    WHERE i.cantidad <= p.stock_minimo 
       OR (i.fecha_vencimiento IS NOT NULL AND DATE(i.fecha_vencimiento) <= DATE('now', '+30 days'))
    ORDER BY i.cantidad ASC
""")

results = cursor.fetchall()
print("\nProductos con alertas:")
for row in results:
    row_dict = dict(row)
    print(f"SKU: {row_dict['sku']}, Nombre: {row_dict['nombre']}, Stock: {row_dict['cantidad']}/{row_dict['stock_minimo']}, "
          f"Vencimiento: {row_dict['fecha_vencimiento']}, Stock: {row_dict['estado_stock']}, Vencimiento: {row_dict['estado_vencimiento']}")

conn.close()
