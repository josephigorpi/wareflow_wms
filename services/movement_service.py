"""Lógica de negocio de movimientos de inventario para WareFlow WMS."""

from database.connection import get_connection
from datetime import datetime


def get_recent_movements(limit: int = 50):
    """Obtiene los movimientos recientes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.tipo, m.producto_id, m.ubicacion_origen_id, m.ubicacion_destino_id,
               m.cantidad, m.referencia, m.observaciones, m.estado, m.usuario_id,
               m.fecha_movimiento,
               p.sku, p.nombre as producto_nombre,
               u.username as usuario_nombre
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.fecha_movimiento DESC LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_movements_with_details():
    """Obtiene movimientos con detalles completos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.tipo, m.producto_id, m.ubicacion_origen_id, m.ubicacion_destino_id,
               m.cantidad, m.referencia, m.observaciones, m.estado, m.usuario_id,
               m.fecha_movimiento,
               p.sku, p.nombre as producto_nombre,
               u.username as usuario_nombre
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.fecha_movimiento DESC
    """)
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def count_movements_by_type_today():
    """Cuenta movimientos de hoy por tipo."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM movimientos 
        WHERE tipo = 'ENTRADA' AND DATE(fecha_movimiento) = ?
    """, (today,))
    entradas = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*) FROM movimientos 
        WHERE tipo = 'SALIDA' AND DATE(fecha_movimiento) = ?
    """, (today,))
    salidas = cursor.fetchone()[0]
    conn.close()
    return {"entradas": entradas, "salidas": salidas}


def get_movements_by_date_range(start_date: str, end_date: str, tipo: str = None):
    """Obtiene movimientos por rango de fechas."""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.id, m.tipo, m.producto_id, m.ubicacion_origen_id, m.ubicacion_destino_id,
               m.cantidad, m.referencia, m.observaciones, m.estado, m.usuario_id,
               m.fecha_movimiento,
               p.sku, p.nombre as producto_nombre,
               u.username as usuario_nombre
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        WHERE DATE(m.fecha_movimiento) BETWEEN ? AND ?
    """
    params = [start_date, end_date]
    if tipo:
        query += " AND m.tipo = ?"
        params.append(tipo)
    query += " ORDER BY m.fecha_movimiento DESC"
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_movements_grouped_by_day(start_date: str, end_date: str):
    """Obtiene movimientos agrupados por día."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            DATE(fecha_movimiento) as fecha,
            tipo,
            COUNT(*) as cantidad
        FROM movimientos
        WHERE DATE(fecha_movimiento) BETWEEN ? AND ?
        GROUP BY DATE(fecha_movimiento), tipo
        ORDER BY fecha
    """, (start_date, end_date))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_movements_by_type(tipo: str, limit: int = None):
    """
    Obtiene movimientos filtrados por tipo.
    
    Args:
        tipo (str): Tipo de movimiento (PICKING, ENTRADA, SALIDA, etc.)
        limit (int, optional): Límite de registros a retornar
        
    Returns:
        list: Lista de movimientos del tipo especificado como diccionarios
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT m.id, m.tipo, m.producto_id, m.ubicacion_origen_id, m.ubicacion_destino_id,
               m.cantidad, m.referencia, m.observaciones, m.estado, m.usuario_id,
               m.fecha_movimiento,
               p.sku, p.nombre as producto_nombre,
               u.username as usuario_nombre,
               uo.codigo as origen_codigo,
               ud.codigo as destino_codigo
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        LEFT JOIN ubicaciones uo ON m.ubicacion_origen_id = uo.id
        LEFT JOIN ubicaciones ud ON m.ubicacion_destino_id = ud.id
        WHERE m.tipo = ?
        ORDER BY m.fecha_movimiento DESC
    """
    
    if limit:
        query += " LIMIT ?"
        cursor.execute(query, (tipo, limit))
    else:
        cursor.execute(query, (tipo,))
    
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def create_picking_order(producto_id: int, cantidad: int, ubicacion_origen_id: int, 
                         referencia: str = None, observaciones: str = None, 
                         usuario_id: int = None):
    """
    Crea una orden de picking (movimiento de tipo PICKING en estado PENDIENTE).
    
    Args:
        producto_id (int): ID del producto a recoger
        cantidad (int): Cantidad a recoger
        ubicacion_origen_id (int): ID de la ubicación de origen
        referencia (str, optional): Referencia de la orden
        observaciones (str, optional): Observaciones adicionales
        usuario_id (int, optional): ID del usuario que crea la orden
        
    Returns:
        int: ID del movimiento creado
        
    Raises:
        ValueError: Si la cantidad es menor o igual a 0
        ValueError: Si no hay suficiente stock en la ubicación
    """
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar stock disponible en la ubicación
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0) as stock_disponible
            FROM inventario
            WHERE producto_id = ? AND ubicacion_id = ?
        """, (producto_id, ubicacion_origen_id))
        result = cursor.fetchone()
        stock_disponible = dict(result)['stock_disponible'] if result else 0
        
        if stock_disponible < cantidad:
            raise ValueError(f"Stock insuficiente en la ubicación. Disponible: {stock_disponible}, Requerido: {cantidad}")
        
        # Crear el movimiento de picking
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO movimientos (
                tipo, producto_id, ubicacion_origen_id, cantidad, 
                referencia, observaciones, estado, usuario_id, fecha_movimiento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'PICKING', 
            producto_id, 
            ubicacion_origen_id, 
            cantidad,
            referencia, 
            observaciones, 
            'PENDIENTE', 
            usuario_id, 
            now
        ))
        
        movimiento_id = cursor.lastrowid
        conn.commit()
        return movimiento_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def process_picking(movimiento_id: int, usuario_id: int = None):
    """
    Procesa una orden de picking, completándola y actualizando el inventario.
    
    Args:
        movimiento_id (int): ID del movimiento de picking a procesar
        usuario_id (int, optional): ID del usuario que procesa la orden
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener el movimiento de picking
        cursor.execute("""
            SELECT m.id, m.tipo, m.producto_id, m.ubicacion_origen_id, m.ubicacion_destino_id,
                   m.cantidad, m.referencia, m.observaciones, m.estado, m.usuario_id,
                   m.fecha_movimiento,
                   p.sku, p.nombre as producto_nombre
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            WHERE m.id = ? AND m.tipo = 'PICKING'
        """, (movimiento_id,))
        movimiento = cursor.fetchone()
        
        if not movimiento:
            return False, "Movimiento no encontrado"
        
        movimiento_dict = dict(movimiento)
        
        if movimiento_dict['estado'] != 'PENDIENTE':
            return False, f"El movimiento ya está en estado: {movimiento_dict['estado']}"
        
        # Verificar nuevamente el stock disponible
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0) as stock_disponible
            FROM inventario
            WHERE producto_id = ? AND ubicacion_id = ?
        """, (movimiento_dict['producto_id'], movimiento_dict['ubicacion_origen_id']))
        result = cursor.fetchone()
        stock_disponible = dict(result)['stock_disponible'] if result else 0
        
        if stock_disponible < movimiento_dict['cantidad']:
            return False, f"Stock insuficiente. Disponible: {stock_disponible}, Requerido: {movimiento_dict['cantidad']}"
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Actualizar el inventario (reducir stock de la ubicación de origen)
        cursor.execute("""
            SELECT id, cantidad
            FROM inventario
            WHERE producto_id = ? AND ubicacion_id = ?
            ORDER BY fecha_vencimiento NULLS LAST, id
        """, (movimiento_dict['producto_id'], movimiento_dict['ubicacion_origen_id']))
        
        inventario_registros = cursor.fetchall()
        cantidad_restante = movimiento_dict['cantidad']
        
        for registro in inventario_registros:
            if cantidad_restante <= 0:
                break
            
            registro_dict = dict(registro)
            cantidad_a_reducir = min(registro_dict['cantidad'], cantidad_restante)
            nueva_cantidad = registro_dict['cantidad'] - cantidad_a_reducir
            
            if nueva_cantidad <= 0:
                cursor.execute("DELETE FROM inventario WHERE id = ?", (registro_dict['id'],))
            else:
                cursor.execute("""
                    UPDATE inventario 
                    SET cantidad = ?, actualizado_en = ?, actualizado_por = ?
                    WHERE id = ?
                """, (nueva_cantidad, now, usuario_id, registro_dict['id']))
            
            cantidad_restante -= cantidad_a_reducir
        
        # Actualizar el estado del movimiento a COMPLETADO
        cursor.execute("""
            UPDATE movimientos 
            SET estado = 'COMPLETADO', 
                observaciones = COALESCE(observaciones || ' ', '') || 'Procesado el ' || ?
            WHERE id = ?
        """, (now, movimiento_id))
        
        # Registrar el movimiento de salida real
        cursor.execute("""
            INSERT INTO movimientos (
                tipo, producto_id, ubicacion_origen_id, cantidad, 
                referencia, observaciones, estado, usuario_id, fecha_movimiento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'SALIDA',
            movimiento_dict['producto_id'],
            movimiento_dict['ubicacion_origen_id'],
            movimiento_dict['cantidad'],
            f"PICKING-{movimiento_id}",
            f"Salida por picking - Orden #{movimiento_id}",
            'COMPLETADO',
            usuario_id,
            now
        ))
        
        conn.commit()
        return True, "Picking completado exitosamente"
        
    except Exception as e:
        conn.rollback()
        return False, f"Error al procesar el picking: {str(e)}"
    finally:
        conn.close()


def create_despacho(movement_ids: list, referencia: str = None, observaciones: str = None, usuario_id: int = None):
    """
    Crea un despacho a partir de una lista de movimientos de picking completados.
    
    Args:
        movement_ids (list): Lista de IDs de movimientos de picking a consolidar
        referencia (str, optional): Referencia del despacho
        observaciones (str, optional): Observaciones adicionales
        usuario_id (int, optional): ID del usuario que crea el despacho
        
    Returns:
        int: ID del movimiento de despacho creado
        
    Raises:
        ValueError: Si no se proporcionan movement_ids
        ValueError: Si algún movimiento no existe o no está en estado COMPLETADO
        ValueError: Si algún movimiento ya fue despachado
    """
    if not movement_ids:
        raise ValueError("Debe seleccionar al menos un movimiento para despachar")
    
    if not isinstance(movement_ids, list):
        movement_ids = [movement_ids]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar que todos los movimientos existan y estén en estado COMPLETADO
        placeholders = ','.join('?' * len(movement_ids))
        cursor.execute(f"""
            SELECT m.id, m.tipo, m.producto_id, m.ubicacion_origen_id, m.ubicacion_destino_id,
                   m.cantidad, m.referencia, m.observaciones, m.estado, m.usuario_id,
                   m.fecha_movimiento,
                   p.sku, p.nombre as producto_nombre
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            WHERE m.id IN ({placeholders})
        """, movement_ids)
        
        movimientos = cursor.fetchall()
        movimientos_dict = [dict(row) for row in movimientos] if movimientos else []
        
        if len(movimientos_dict) != len(movement_ids):
            found_ids = [m['id'] for m in movimientos_dict]
            missing_ids = [id for id in movement_ids if id not in found_ids]
            raise ValueError(f"Movimientos no encontrados: {missing_ids}")
        
        # Verificar que todos estén en estado COMPLETADO y no despachados
        for movimiento in movimientos_dict:
            if movimiento['estado'] != 'COMPLETADO':
                raise ValueError(f"El movimiento #{movimiento['id']} no está completado. Estado actual: {movimiento['estado']}")
            
            # Verificar si ya fue despachado
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM movimientos
                WHERE tipo = 'DESPACHO' 
                AND referencia = ?
            """, (f"PICKING-{movimiento['id']}",))
            result = cursor.fetchone()
            if dict(result)['count'] > 0:
                raise ValueError(f"El movimiento #{movimiento['id']} ya fue despachado")
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear el movimiento de despacho consolidado
        productos = {}
        detalles = []
        
        for movimiento in movimientos_dict:
            key = movimiento['producto_id']
            if key in productos:
                productos[key]['cantidad'] += movimiento['cantidad']
            else:
                productos[key] = {
                    'producto_id': movimiento['producto_id'],
                    'sku': movimiento['sku'],
                    'producto_nombre': movimiento['producto_nombre'],
                    'cantidad': movimiento['cantidad'],
                    'movimiento_id': movimiento['id']
                }
            
            detalles.append(f"Picking #{movimiento['id']}: {movimiento['sku']} x {movimiento['cantidad']}")
        
        # Crear el registro de despacho
        referencia_despacho = referencia or f"DESPACHO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        observaciones_despacho = observaciones or ""
        observaciones_completa = f"{observaciones_despacho}\n\nPedidos consolidados:\n" + "\n".join(detalles)
        
        primer_producto = list(productos.values())[0]
        
        cursor.execute("""
            INSERT INTO movimientos (
                tipo, producto_id, cantidad, referencia, observaciones, 
                estado, usuario_id, fecha_movimiento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'DESPACHO',
            primer_producto['producto_id'],
            sum(p['cantidad'] for p in productos.values()),
            referencia_despacho,
            observaciones_completa,
            'COMPLETADO',
            usuario_id,
            now
        ))
        
        despacho_id = cursor.lastrowid
        
        # Actualizar los movimientos de picking
        for movimiento in movimientos_dict:
            cursor.execute("""
                UPDATE movimientos 
                SET observaciones = COALESCE(observaciones || ' ', '') || '| Despachado en DESPACHO-' || ?
                WHERE id = ?
            """, (despacho_id, movimiento['id']))
        
        conn.commit()
        return despacho_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def create_recepcion(producto_id: int, cantidad: int, ubicacion_id: int = None, 
                     lote: str = None, fecha_vencimiento: str = None, 
                     referencia: str = None, observaciones: str = None, 
                     usuario_id: int = None):
    """
    Registra una recepción de mercancía.
    """
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar que el producto existe y está activo
        cursor.execute("SELECT id, nombre, sku FROM productos WHERE id = ? AND activo = 1", (producto_id,))
        producto = cursor.fetchone()
        if not producto:
            raise ValueError(f"Producto con ID {producto_id} no encontrado o inactivo")
        
        producto_dict = dict(producto)
        
        # Si no se especificó ubicación, buscar una automáticamente
        if ubicacion_id is None:
            ubicacion_id = _find_available_location(cursor, producto_id)
            if ubicacion_id is None:
                raise ValueError("No hay ubicaciones disponibles para este producto")
        
        # Verificar que la ubicación existe y está activa
        cursor.execute("SELECT id, codigo FROM ubicaciones WHERE id = ? AND activo = 1", (ubicacion_id,))
        ubicacion = cursor.fetchone()
        if not ubicacion:
            raise ValueError(f"Ubicación con ID {ubicacion_id} no encontrada o inactiva")
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear el movimiento de recepción
        cursor.execute("""
            INSERT INTO movimientos (
                tipo, producto_id, ubicacion_destino_id, cantidad, 
                referencia, observaciones, estado, usuario_id, fecha_movimiento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'ENTRADA',
            producto_id,
            ubicacion_id,
            cantidad,
            referencia or f"REC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            observaciones or f"Recepción de {producto_dict['nombre']} - {cantidad} unidades",
            'COMPLETADO',
            usuario_id,
            now
        ))
        
        movimiento_id = cursor.lastrowid
        
        # Actualizar el inventario
        _update_inventory_for_recepcion(cursor, producto_id, ubicacion_id, cantidad, lote, fecha_vencimiento, usuario_id)
        
        conn.commit()
        return movimiento_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def _find_available_location(cursor, producto_id: int):
    """
    Encuentra una ubicación disponible para un producto.
    """
    # Buscar ubicaciones que ya tienen este producto
    cursor.execute("""
        SELECT DISTINCT i.ubicacion_id, u.codigo
        FROM inventario i
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        WHERE i.producto_id = ? AND u.activo = 1
        ORDER BY u.codigo
        LIMIT 1
    """, (producto_id,))
    result = cursor.fetchone()
    if result:
        return dict(result)['ubicacion_id']
    
    # Buscar ubicaciones vacías
    cursor.execute("""
        SELECT u.id, u.codigo
        FROM ubicaciones u
        LEFT JOIN inventario i ON u.id = i.ubicacion_id
        WHERE u.activo = 1 
        AND i.id IS NULL
        AND u.ocupada = 0
        ORDER BY u.codigo
        LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        return dict(result)['id']
    
    # Buscar ubicaciones con capacidad disponible
    cursor.execute("""
        SELECT u.id, u.codigo
        FROM ubicaciones u
        LEFT JOIN inventario i ON u.id = i.ubicacion_id
        WHERE u.activo = 1 
        GROUP BY u.id
        HAVING COUNT(i.id) < 5
        ORDER BY COUNT(i.id)
        LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        return dict(result)['id']
    
    return None


def _update_inventory_for_recepcion(cursor, producto_id: int, ubicacion_id: int, 
                                    cantidad: int, lote: str = None, 
                                    fecha_vencimiento: str = None, usuario_id: int = None):
    """
    Actualiza el inventario después de una recepción.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Verificar si ya existe un registro de inventario para esta combinación
    if lote:
        cursor.execute("""
            SELECT id, cantidad
            FROM inventario
            WHERE producto_id = ? AND ubicacion_id = ? AND lote = ?
        """, (producto_id, ubicacion_id, lote))
    else:
        cursor.execute("""
            SELECT id, cantidad
            FROM inventario
            WHERE producto_id = ? AND ubicacion_id = ? AND lote IS NULL
        """, (producto_id, ubicacion_id))
    
    registro = cursor.fetchone()
    
    if registro:
        registro_dict = dict(registro)
        nueva_cantidad = registro_dict['cantidad'] + cantidad
        cursor.execute("""
            UPDATE inventario 
            SET cantidad = ?, actualizado_en = ?, actualizado_por = ?
            WHERE id = ?
        """, (nueva_cantidad, now, usuario_id, registro_dict['id']))
    else:
        cursor.execute("""
            INSERT INTO inventario (
                producto_id, ubicacion_id, cantidad, lote, fecha_vencimiento,
                actualizado_en, actualizado_por
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (producto_id, ubicacion_id, cantidad, lote, fecha_vencimiento, now, usuario_id))


def get_recepciones_recientes(limit: int = 50):
    """
    Obtiene las recepciones recientes.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.tipo, m.producto_id, m.ubicacion_origen_id, m.ubicacion_destino_id, 
               m.cantidad, m.referencia, m.observaciones, m.estado, m.usuario_id, 
               m.fecha_movimiento,
               p.sku, p.nombre as producto_nombre,
               u.username as usuario_nombre,
               ud.codigo as destino_codigo,
               uo.codigo as origen_codigo
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        LEFT JOIN ubicaciones ud ON m.ubicacion_destino_id = ud.id
        LEFT JOIN ubicaciones uo ON m.ubicacion_origen_id = uo.id
        WHERE m.tipo = 'ENTRADA'
        ORDER BY m.fecha_movimiento DESC
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_recepciones_pendientes():
    """
    Obtiene las recepciones pendientes de inspección.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.tipo, m.producto_id, m.ubicacion_origen_id, m.ubicacion_destino_id, 
               m.cantidad, m.referencia, m.observaciones, m.estado, m.usuario_id, 
               m.fecha_movimiento,
               p.sku, p.nombre as producto_nombre,
               u.username as usuario_nombre
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        WHERE m.tipo = 'ENTRADA' 
        AND m.ubicacion_destino_id IS NULL
        ORDER BY m.fecha_movimiento DESC
    """)
    
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def update_recepcion_with_inspection(movimiento_id: int, ubicacion_id: int, 
                                     lote: str = None, fecha_vencimiento: str = None,
                                     observaciones: str = None, usuario_id: int = None,
                                     aprobado: bool = True):
    """
    Actualiza una recepción con los resultados de la inspección.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener el movimiento
        cursor.execute("SELECT * FROM movimientos WHERE id = ? AND tipo = 'ENTRADA'", (movimiento_id,))
        movimiento = cursor.fetchone()
        if not movimiento:
            raise ValueError(f"Movimiento con ID {movimiento_id} no encontrado")
        
        movimiento_dict = dict(movimiento)
        
        if not aprobado:
            cursor.execute("""
                UPDATE movimientos 
                SET estado = 'RECHAZADO', 
                    observaciones = COALESCE(observaciones || ' ', '') || ? || ' - Inspección rechazada'
                WHERE id = ?
            """, (observaciones or '', movimiento_id))
            conn.commit()
            return False
        
        # Verificar ubicación
        cursor.execute("SELECT id FROM ubicaciones WHERE id = ? AND activo = 1", (ubicacion_id,))
        if not cursor.fetchone():
            raise ValueError(f"Ubicación con ID {ubicacion_id} no encontrada o inactiva")
        
        # Actualizar el movimiento con la ubicación
        cursor.execute("""
            UPDATE movimientos 
            SET ubicacion_destino_id = ?,
                estado = 'COMPLETADO',
                observaciones = COALESCE(observaciones || ' ', '') || ?
            WHERE id = ?
        """, (ubicacion_id, observaciones or 'Inspección aprobada', movimiento_id))
        
        # Actualizar inventario
        _update_inventory_for_recepcion(
            cursor, 
            movimiento_dict['producto_id'], 
            ubicacion_id, 
            movimiento_dict['cantidad'], 
            lote, 
            fecha_vencimiento, 
            usuario_id
        )
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
