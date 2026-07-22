"""Script para verificar el inventario completo por producto."""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# Verificar stock total por producto
cursor.execute("""
    SELECT p.id, p.sku, p.nombre, p.stock_minimo, 
           COALESCE(SUM(i.cantidad), 0) as stock_total,
           COUNT(i.id) as num_registros
    FROM productos p
    LEFT JOIN inventario i ON p.id = i.producto_id
    WHERE p.activo = 1
    GROUP BY p.id
    HAVING stock_total <= p.stock_minimo OR stock_total = 0
    ORDER BY stock_total ASC
""")

results = cursor.fetchall()
print("Productos con stock total bajo:")
for row in results:
    row_dict = dict(row)
    print(f"SKU: {row_dict['sku']}, Nombre: {row_dict['nombre']}, "
          f"Stock total: {row_dict['stock_total']}, Mínimo: {row_dict['stock_minimo']}, "
          f"Registros: {row_dict['num_registros']}")

# Verificar detalles de inventario para productos específicos
print("\nDetalles de inventario para productos actualizados:")
for product_id in [2, 5, 9, 17, 20, 23]:
    cursor.execute("""
        SELECT p.sku, p.nombre, i.id, i.ubicacion_id, i.cantidad, i.lote
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        WHERE i.producto_id = ?
    """, (product_id,))
    inv_results = cursor.fetchall()
    for row in inv_results:
        row_dict = dict(row)
        print(f"SKU: {row_dict['sku']}, Inv ID: {row_dict['id']}, "
              f"Ubicación: {row_dict['ubicacion_id']}, Cantidad: {row_dict['cantidad']}")

conn.close()
