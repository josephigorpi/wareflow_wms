"""Script para actualizar el stock bajo con commit explícito."""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    # Actualizar stock de productos para que estén por debajo del mínimo
    updates = [
        (2, 2),   # SKU-002: Monitor Samsung - reducir a 2 (mínimo: 3)
        (5, 3),   # SKU-005: Disco Duro - reducir a 3 (mínimo: 5)
        (9, 2),   # SKU-009: Chaqueta - reducir a 2 (mínimo: 5)
        (17, 1),  # SKU-017: Vajilla - reducir a 1 (mínimo: 3)
        (20, 1),  # SKU-020: Taladro - reducir a 1 (mínimo: 3)
        (23, 2),  # SKU-023: LEGO - reducir a 2 (mínimo: 5)
    ]
    
    for product_id, new_quantity in updates:
        cursor.execute(
            "UPDATE inventario SET cantidad = ? WHERE producto_id = ?",
            (new_quantity, product_id)
        )
        print(f"Producto ID {product_id}: actualizado a {new_quantity}")
    
    conn.commit()
    print("\n✅ Commit realizado exitosamente.")
    
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
    print(f"SKU: {row_dict['sku']}, Stock total: {row_dict['stock_total']}, Mínimo: {row_dict['stock_minimo']}")

conn.close()
