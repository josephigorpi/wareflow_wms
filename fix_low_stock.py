"""Script para corregir el stock bajo de productos."""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# Actualizar stock de productos para que estén por debajo del mínimo
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

try:
    for query, expected in updates:
        cursor.execute(query)
        affected = cursor.rowcount
        print(f"Query ejecutado: {affected} filas afectadas")
    
    conn.commit()
    print("\n✅ Stock actualizado correctamente.")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
finally:
    conn.close()

# Verificar los resultados
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT p.sku, p.nombre, COALESCE(SUM(i.cantidad), 0) as stock_total, p.stock_minimo
    FROM productos p
    LEFT JOIN inventario i ON p.id = i.producto_id
    WHERE p.id IN (2, 5, 9, 17, 20, 23)
    GROUP BY p.id
""")

results = cursor.fetchall()
print("\nProductos actualizados:")
for row in results:
    row_dict = dict(row)
    print(f"SKU: {row_dict['sku']}, Nombre: {row_dict['nombre']}, "
          f"Stock total: {row_dict['stock_total']}, Mínimo: {row_dict['stock_minimo']}")

conn.close()
