"""Script para verificar el stock actual de los productos."""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# Verificar stock actual de los productos que intenté actualizar
cursor.execute("""
    SELECT p.id, p.sku, p.nombre, p.stock_minimo, i.cantidad
    FROM productos p
    JOIN inventario i ON p.id = i.producto_id
    WHERE p.id IN (2, 5, 9, 17, 20, 23)
    ORDER BY p.id
""")

results = cursor.fetchall()
print("Stock actual de productos objetivo:")
for row in results:
    row_dict = dict(row)
    print(f"ID: {row_dict['id']}, SKU: {row_dict['sku']}, Nombre: {row_dict['nombre']}, "
          f"Stock: {row_dict['cantidad']}, Mínimo: {row_dict['stock_minimo']}")

conn.close()
