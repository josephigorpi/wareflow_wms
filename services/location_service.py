"""Lógica de negocio de ubicaciones para WareFlow WMS."""

from database.connection import get_connection


def get_all_locations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ubicaciones WHERE activo = 1")
    return cursor.fetchall()


def get_locations_with_zones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.*, z.nombre as zona_nombre, z.codigo as zona_codigo
        FROM ubicaciones u
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE u.activo = 1
    """)
    return cursor.fetchall()


def count_locations_by_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ubicaciones WHERE activo = 1")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ubicaciones WHERE activo = 1 AND ocupada = 1")
    occupied = cursor.fetchone()[0]
    free = total - occupied
    return {"total": total, "ocupadas": occupied, "libres": free}


def count_free_locations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ubicaciones WHERE activo = 1 AND ocupada = 0")
    return cursor.fetchone()[0]


def get_location_occupation_by_zone():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            z.nombre as zona,
            COUNT(*) as total,
            SUM(CASE WHEN u.ocupada = 1 THEN 1 ELSE 0 END) as ocupadas
        FROM ubicaciones u
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE u.activo = 1
        GROUP BY z.id, z.nombre
    """)
    return cursor.fetchall()
