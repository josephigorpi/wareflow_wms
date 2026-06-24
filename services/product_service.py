"""Lógica de negocio de productos para WareFlow WMS."""

from database.db_manager import fetch_all, fetch_one, insert, update


def get_all_products():
    return fetch_all("SELECT * FROM productos WHERE activo = 1")


def get_product_by_id(product_id):
    return fetch_one("SELECT * FROM productos WHERE id = ?", (product_id,))


def get_product_by_sku(sku):
    return fetch_one("SELECT * FROM productos WHERE sku = ?", (sku,))


def get_all_categories():
    return fetch_all("SELECT * FROM categorias_producto WHERE activo = 1")
