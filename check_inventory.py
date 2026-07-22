"""Script para verificar el inventario actual."""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# Verificar inventario actual con detalles de productos
cursor.execute("""
    SELECT i.id, i.producto_id, i.ubicacion_id, i.cantidad, i.lote, i.fecha_vencimiento,
           p.sku, p.nombre, p.stock_minimo, p.stock_maximo
    FROM inventario i
    JOIN productos p ON i.producto_id = p.id
    ORDER BY i.producto_id
""")

results = cursor.fetchall()
print("Inventario actual:")
for row in results:
    row_dict = dict(row)
    print(f"SKU: {row_dict['sku']}, Nombre: {row_dict['nombre']}, Stock: {row_dict['cantidad']}, "
          f"Mínimo: {row_dict['stock_minimo']}, Vencimiento: {row_dict['fecha_vencimiento']}")

conn.close()
