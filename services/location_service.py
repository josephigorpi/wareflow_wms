"""Lógica de negocio de ubicaciones para WareFlow WMS."""

from database.db_manager import fetch_all, fetch_one


def get_all_locations():
    return fetch_all("SELECT * FROM ubicaciones WHERE activo = 1")


def get_location_by_id(location_id):
    return fetch_one("SELECT * FROM ubicaciones WHERE id = ?", (location_id,))


def get_all_zones():
    return fetch_all("SELECT * FROM zonas WHERE activo = 1")


def get_zone_by_id(zone_id):
    return fetch_one("SELECT * FROM zonas WHERE id = ?", (zone_id,))


def get_locations_by_zone(zone_id):
    return fetch_all("SELECT * FROM ubicaciones WHERE zona_id = ? AND activo = 1", (zone_id,))
