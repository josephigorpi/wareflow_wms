"""Script para verificar la función get_products_low_stock."""

from services.product_service import get_products_low_stock

products = get_products_low_stock()
print(f"Productos con stock bajo encontrados: {len(products)}")
for p in products:
    print(f"SKU: {p['sku']}, Nombre: {p['nombre']}, Stock total: {p['stock_total']}, Mínimo: {p['stock_minimo']}")
