"""Script para verificar directamente el stock en la base de datos."""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# Verificar stock total por producto
cursor.execute("""
    SELECT p.id, p.sku, p.nombre, p.stock_minimo, 
           COALESCE(SUM(i.cantidad), 0) as stock_total
    FROM productos p
    LEFT JOIN inventario i ON p.id = i.producto_id
    WHERE p.activo = 1
    GROUP BY p.id
    HAVING stock_total <= p.stock_minimo
    ORDER BY stock_total ASC
""")

results = cursor.fetchall()
print(f"Productos con stock bajo en la base de datos: {len(results)}")
for row in results:
    row_dict = dict(row)
    print(f"SKU: {row_dict['sku']}, Nombre: {row_dict['nombre']}, "
          f"Stock total: {row_dict['stock_total']}, Mínimo: {row_dict['stock_minimo']}")

conn.close()
