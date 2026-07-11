"""Lógica de negocio de ubicaciones para WareFlow WMS."""

from database.connection import get_connection
from database.db_manager import fetch_all, fetch_one, insert, update, delete

def get_all_locations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ubicaciones WHERE activo = 1")
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_locations_with_zones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.*, z.nombre as zona_nombre, z.codigo as zona_codigo
        FROM ubicaciones u
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE u.activo = 1
    """)
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def count_locations_by_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ubicaciones WHERE activo = 1")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ubicaciones WHERE activo = 1 AND ocupada = 1")
    occupied = cursor.fetchone()[0]
    conn.close()
    free = total - occupied
    return {"total": total, "ocupadas": occupied, "libres": free}


def count_free_locations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ubicaciones WHERE activo = 1 AND ocupada = 0")
    count = cursor.fetchone()[0]
    conn.close()
    return count


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
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_all_zones():
    """Obtiene todas las zonas activas.
    
    Returns:
        list: Lista de diccionarios con datos de zonas, o lista vacía si no hay.
    """
    query = "SELECT id, codigo, nombre, tipo, descripcion FROM zonas WHERE activo = 1 ORDER BY nombre"
    results = fetch_all(query)
    return [dict(row) for row in results] if results else []


def get_all_locations(zona_id=None, search_term=""):
    """Obtiene ubicaciones con sus zonas asociadas, opcionalmente filtradas.
    
    Args:
        zona_id (int, optional): Filtra por zona específica. Defaults to None.
        search_term (str, optional): Busca por código de ubicación (LIKE). Defaults to "".
    
    Returns:
        list: Lista de diccionarios con ubicaciones + zona_nombre, o lista vacía.
    """
    query = """
        SELECT 
            u.id, u.codigo, u.zona_id, u.pasillo, u.estante, u.nivel, 
            u.posicion, u.capacidad_kg, u.capacidad_m3, u.ocupada, u.activo,
            z.nombre AS zona_nombre, z.codigo AS zona_codigo
        FROM ubicaciones u
        JOIN zonas z ON u.zona_id = z.id
        WHERE u.activo = 1
    """
    
    params = []
    
    if zona_id is not None:
        query += " AND u.zona_id = ?"
        params.append(zona_id)
    
    if search_term and search_term.strip():
        query += " AND u.codigo LIKE ?"
        params.append(f"%{search_term.strip()}%")
    
    query += " ORDER BY u.codigo"
    
    results = fetch_all(query, tuple(params))
    return [dict(row) for row in results] if results else []


def get_location_by_id(location_id):
    """Obtiene una ubicación específica con datos de su zona.
    
    Args:
        location_id (int): ID de la ubicación.
    
    Returns:
        dict: Ubicación con zona_nombre y zona_id, o None si no existe.
    """
    query = """
        SELECT 
            u.id, u.codigo, u.zona_id, u.pasillo, u.estante, u.nivel, 
            u.posicion, u.capacidad_kg, u.capacidad_m3, u.ocupada, u.activo,
            z.nombre AS zona_nombre, z.id AS zona_id_real
        FROM ubicaciones u
        JOIN zonas z ON u.zona_id = z.id
        WHERE u.id = ?
    """
    result = fetch_one(query, (location_id,))
    return dict(result) if result else None


def create_location(zona_id, codigo, pasillo, estante, nivel, posicion, capacidad_kg=None, capacidad_m3=None):
    """Crea una nueva ubicación con validaciones internas.
    
    Validaciones:
        - Verifica que zona_id existe en zonas
        - Verifica que codigo es único en ubicaciones
    
    Args:
        zona_id (int): ID de la zona.
        codigo (str): Código único de la ubicación.
        pasillo (str): Identificación del pasillo.
        estante (str): Identificación del estante.
        nivel (str): Identificación del nivel.
        posicion (str): Identificación de la posición.
        capacidad_kg (float, optional): Capacidad en kg. Defaults to None.
        capacidad_m3 (float, optional): Capacidad en m³. Defaults to None.
    
    Returns:
        int: ID de la ubicación creada.
        
    Raises:
        ValueError: Si zona_id no existe, si codigo ya existe, o si falta un campo requerido.
    """
    # Validar campos requeridos
    if not all([zona_id, codigo, pasillo, estante, nivel, posicion]):
        raise ValueError("Todos los campos requeridos deben ser completados")
    
    # Validar que zona existe
    zona_query = "SELECT id FROM zonas WHERE id = ? AND activo = 1"
    zona_exists = fetch_one(zona_query, (zona_id,))
    if not zona_exists:
        raise ValueError(f"La zona con ID {zona_id} no existe o está inactiva")
    
    # Validar código único
    codigo_query = "SELECT id FROM ubicaciones WHERE codigo = ?"
    codigo_exists = fetch_one(codigo_query, (codigo.strip(),))
    if codigo_exists:
        raise ValueError(f"El código '{codigo}' ya existe en el sistema")
    
    # Crear ubicación
    data = {
        "zona_id": zona_id,
        "codigo": codigo.strip(),
        "pasillo": pasillo.strip(),
        "estante": estante.strip(),
        "nivel": nivel.strip(),
        "posicion": posicion.strip(),
        "capacidad_kg": capacidad_kg,
        "capacidad_m3": capacidad_m3,
        "ocupada": 0,
        "activo": 1,
    }
    
    location_id = insert("ubicaciones", data)
    return location_id


def update_location(location_id, zona_id, codigo, pasillo, estante, nivel, posicion, capacidad_kg=None, capacidad_m3=None):
    """Actualiza una ubicación existente con validaciones internas.
    
    Validaciones:
        - Verifica que la ubicación existe
        - Verifica que zona_id existe en zonas
        - Si se cambia el código, verifica que el nuevo código es único
    
    Args:
        location_id (int): ID de la ubicación a actualizar.
        zona_id (int): ID de la zona.
        codigo (str): Código de la ubicación.
        pasillo (str): Identificación del pasillo.
        estante (str): Identificación del estante.
        nivel (str): Identificación del nivel.
        posicion (str): Identificación de la posición.
        capacidad_kg (float, optional): Capacidad en kg. Defaults to None.
        capacidad_m3 (float, optional): Capacidad en m³. Defaults to None.
    
    Returns:
        int: Número de filas afectadas.
        
    Raises:
        ValueError: Si ubicación no existe, zona no existe, código duplicado, o falta un campo requerido.
    """
    # Validar campos requeridos
    if not all([location_id, zona_id, codigo, pasillo, estante, nivel, posicion]):
        raise ValueError("Todos los campos requeridos deben ser completados")
    
    # Validar que ubicación existe
    current_location_query = "SELECT id, codigo FROM ubicaciones WHERE id = ?"
    current_location = fetch_one(current_location_query, (location_id,))
    if not current_location:
        raise ValueError(f"La ubicación con ID {location_id} no existe")
    
    # Validar que zona existe
    zona_query = "SELECT id FROM zonas WHERE id = ? AND activo = 1"
    zona_exists = fetch_one(zona_query, (zona_id,))
    if not zona_exists:
        raise ValueError(f"La zona con ID {zona_id} no existe o está inactiva")
    
    # Validar código único (solo si se cambió)
    current_codigo = current_location["codigo"]
    if codigo.strip() != current_codigo:
        codigo_query = "SELECT id FROM ubicaciones WHERE codigo = ?"
        codigo_exists = fetch_one(codigo_query, (codigo.strip(),))
        if codigo_exists:
            raise ValueError(f"El código '{codigo}' ya existe en el sistema")
    
    # Actualizar ubicación
    data = {
        "zona_id": zona_id,
        "codigo": codigo.strip(),
        "pasillo": pasillo.strip(),
        "estante": estante.strip(),
        "nivel": nivel.strip(),
        "posicion": posicion.strip(),
        "capacidad_kg": capacidad_kg,
        "capacidad_m3": capacidad_m3,
    }
    
    rows_affected = update("ubicaciones", data, "id = ?", (location_id,))
    return rows_affected


def delete_location(location_id):
    """Elimina una ubicación solo si no tiene inventario asociado.
    
    Validaciones:
        - Verifica que la ubicación existe
        - Verifica que NO hay productos (inventario) en esa ubicación
    
    Args:
        location_id (int): ID de la ubicación a eliminar.
    
    Returns:
        int: Número de filas eliminadas (0 o 1).
        
    Raises:
        ValueError: Si ubicación no existe o si tiene inventario asociado.
    """
    # Validar que ubicación existe
    location_query = "SELECT id, codigo FROM ubicaciones WHERE id = ?"
    location = fetch_one(location_query, (location_id,))
    if not location:
        raise ValueError(f"La ubicación con ID {location_id} no existe")
    
    # Validar que NO hay inventario
    inventory_query = "SELECT COUNT(*) as count FROM inventario WHERE ubicacion_id = ? AND cantidad > 0"
    inventory_result = fetch_one(inventory_query, (location_id,))
    inventory_count = inventory_result["count"] if inventory_result else 0
    
    if inventory_count > 0:
        raise ValueError(
            f"No se puede eliminar la ubicación '{location['codigo']}' "
            f"porque contiene {inventory_count} producto(s) en inventario"
        )
    
    # Eliminar ubicación
    rows_deleted = delete("ubicaciones", "id = ?", (location_id,))
    return rows_deleted


def get_available_locations():
    """Obtiene todas las ubicaciones disponibles (no ocupadas) con sus zonas.
    
    Returns:
        list: Lista de diccionarios con ubicaciones disponibles, o lista vacía.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.*, z.nombre as zona_nombre, z.codigo as zona_codigo
        FROM ubicaciones u
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE u.activo = 1 AND u.ocupada = 0
        ORDER BY u.codigo
    """)
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_available_locations_with_capacity(producto_id: int = None):
    """Obtiene ubicaciones disponibles con información de capacidad.
    
    Args:
        producto_id (int, optional): Si se proporciona, filtra ubicaciones 
                                     que puedan almacenar el producto.
    
    Returns:
        list: Lista de diccionarios con ubicaciones disponibles y capacidad.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT u.*, z.nombre as zona_nombre, z.codigo as zona_codigo,
               COALESCE(SUM(i.cantidad), 0) as stock_actual
        FROM ubicaciones u
        LEFT JOIN zonas z ON u.zona_id = z.id
        LEFT JOIN inventario i ON u.id = i.ubicacion_id
        WHERE u.activo = 1 AND u.ocupada = 0
    """
    
    params = []
    
    if producto_id:
        query += " AND (u.id NOT IN (SELECT ubicacion_id FROM inventario WHERE producto_id != ?) OR u.id NOT IN (SELECT ubicacion_id FROM inventario))"
        params.append(producto_id)
    
    query += """ 
        GROUP BY u.id
        ORDER BY stock_actual ASC, u.codigo
    """
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_available_locations_by_zone(zona_id: int):
    """Obtiene ubicaciones disponibles en una zona específica.
    
    Args:
        zona_id (int): ID de la zona.
    
    Returns:
        list: Lista de diccionarios con ubicaciones disponibles en la zona.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.*, z.nombre as zona_nombre, z.codigo as zona_codigo
        FROM ubicaciones u
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE u.activo = 1 AND u.ocupada = 0 AND u.zona_id = ?
        ORDER BY u.codigo
    """, (zona_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def mark_location_occupied(location_id: int, occupied: bool = True):
    """Marca una ubicación como ocupada o libre.
    
    Args:
        location_id (int): ID de la ubicación.
        occupied (bool): True para marcar como ocupada, False para libre.
    
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ubicaciones 
            SET ocupada = ? 
            WHERE id = ?
        """, (1 if occupied else 0, location_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_location_occupancy_details(location_id: int):
    """Obtiene detalles de ocupación de una ubicación específica.
    
    Args:
        location_id (int): ID de la ubicación.
    
    Returns:
        dict: Detalles de ocupación incluyendo productos y cantidades.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtener información de la ubicación
    cursor.execute("""
        SELECT u.*, z.nombre as zona_nombre
        FROM ubicaciones u
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE u.id = ?
    """, (location_id,))
    location = cursor.fetchone()
    
    if not location:
        conn.close()
        return None
    
    location_dict = dict(location)
    
    # Obtener productos en esta ubicación
    cursor.execute("""
        SELECT i.*, p.sku, p.nombre as producto_nombre
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        WHERE i.ubicacion_id = ? AND i.cantidad > 0
    """, (location_id,))
    products = cursor.fetchall()
    products_dict = [dict(row) for row in products] if products else []
    
    conn.close()
    
    return {
        "location": location_dict,
        "products": products_dict,
        "total_products": len(products_dict),
        "total_units": sum(p['cantidad'] for p in products_dict) if products_dict else 0
    }
