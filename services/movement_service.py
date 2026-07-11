"""Lógica de negocio de movimientos de inventario para WareFlow WMS."""

from database.connection import get_connection
from datetime import datetime


def get_recent_movements(limit: int = 50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.*, p.sku, p.nombre as producto_nombre, u.username as usuario_nombre
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.fecha_movimiento DESC LIMIT ?
    """, (limit,))
    return cursor.fetchall()


def get_movements_with_details():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.*, p.sku, p.nombre as producto_nombre, u.username as usuario_nombre
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.fecha_movimiento DESC
    """)
    return cursor.fetchall()


def count_movements_by_type_today():
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
    return {"entradas": entradas, "salidas": salidas}


def get_movements_by_date_range(start_date: str, end_date: str, tipo: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.*, p.sku, p.nombre as producto_nombre, u.username as usuario_nombre
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
    return cursor.fetchall()


def get_movements_grouped_by_day(start_date: str, end_date: str):
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
    return cursor.fetchall()


def get_movements_by_type(tipo: str, limit: int = None):
    """
    Obtiene movimientos filtrados por tipo.
    
    Args:
        tipo (str): Tipo de movimiento (PICKING, ENTRADA, SALIDA, etc.)
        limit (int, optional): Límite de registros a retornar
        
    Returns:
        list: Lista de movimientos del tipo especificado
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT m.*, 
               p.sku, 
               p.nombre as producto_nombre,
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
    
    return cursor.fetchall()


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
        stock_disponible = result['stock_disponible'] if result else 0
        
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
            SELECT m.*, p.sku, p.nombre as producto_nombre
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            WHERE m.id = ? AND m.tipo = 'PICKING'
        """, (movimiento_id,))
        movimiento = cursor.fetchone()
        
        if not movimiento:
            return False, "Movimiento no encontrado"
        
        if movimiento['estado'] != 'PENDIENTE':
            return False, f"El movimiento ya está en estado: {movimiento['estado']}"
        
        # Verificar nuevamente el stock disponible
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0) as stock_disponible
            FROM inventario
            WHERE producto_id = ? AND ubicacion_id = ?
        """, (movimiento['producto_id'], movimiento['ubicacion_origen_id']))
        result = cursor.fetchone()
        stock_disponible = result['stock_disponible'] if result else 0
        
        if stock_disponible < movimiento['cantidad']:
            return False, f"Stock insuficiente. Disponible: {stock_disponible}, Requerido: {movimiento['cantidad']}"
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Actualizar el inventario (reducir stock de la ubicación de origen)
        # Primero, obtener los registros de inventario para esta ubicación y producto
        cursor.execute("""
            SELECT id, cantidad
            FROM inventario
            WHERE producto_id = ? AND ubicacion_id = ?
            ORDER BY fecha_vencimiento NULLS LAST, id
        """, (movimiento['producto_id'], movimiento['ubicacion_origen_id']))
        
        inventario_registros = cursor.fetchall()
        cantidad_restante = movimiento['cantidad']
        
        for registro in inventario_registros:
            if cantidad_restante <= 0:
                break
                
            cantidad_a_reducir = min(registro['cantidad'], cantidad_restante)
            nueva_cantidad = registro['cantidad'] - cantidad_a_reducir
            
            if nueva_cantidad <= 0:
                # Eliminar el registro si la cantidad llega a 0
                cursor.execute("DELETE FROM inventario WHERE id = ?", (registro['id'],))
            else:
                # Actualizar la cantidad
                cursor.execute("""
                    UPDATE inventario 
                    SET cantidad = ?, actualizado_en = ?, actualizado_por = ?
                    WHERE id = ?
                """, (nueva_cantidad, now, usuario_id, registro['id']))
            
            cantidad_restante -= cantidad_a_reducir
        
        # Actualizar el estado del movimiento a COMPLETADO
        cursor.execute("""
            UPDATE movimientos 
            SET estado = 'COMPLETADO', 
                observaciones = COALESCE(observaciones || ' ', '') || 'Procesado el ' || ?
            WHERE id = ?
        """, (now, movimiento_id))
        
        # Registrar el movimiento de salida real (opcional pero recomendado)
        # Esto crea un registro adicional de tipo SALIDA para el tracking
        cursor.execute("""
            INSERT INTO movimientos (
                tipo, producto_id, ubicacion_origen_id, cantidad, 
                referencia, observaciones, estado, usuario_id, fecha_movimiento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'SALIDA',
            movimiento['producto_id'],
            movimiento['ubicacion_origen_id'],
            movimiento['cantidad'],
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
            SELECT m.*, p.sku, p.nombre as producto_nombre
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            WHERE m.id IN ({placeholders})
        """, movement_ids)
        
        movimientos = cursor.fetchall()
        
        if len(movimientos) != len(movement_ids):
            found_ids = [m['id'] for m in movimientos]
            missing_ids = [id for id in movement_ids if id not in found_ids]
            raise ValueError(f"Movimientos no encontrados: {missing_ids}")
        
        # Verificar que todos estén en estado COMPLETADO y no despachados
        for movimiento in movimientos:
            if movimiento['estado'] != 'COMPLETADO':
                raise ValueError(f"El movimiento #{movimiento['id']} no está completado. Estado actual: {movimiento['estado']}")
            
            # Verificar si ya fue despachado (buscando un movimiento de DESPACHO relacionado)
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM movimientos
                WHERE tipo = 'DESPACHO' 
                AND referencia = ?
            """, (f"PICKING-{movimiento['id']}",))
            
            if cursor.fetchone()['count'] > 0:
                raise ValueError(f"El movimiento #{movimiento['id']} ya fue despachado")
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear el movimiento de despacho consolidado
        # Agrupar todos los productos y cantidades para el despacho
        productos = {}
        detalles = []
        
        for movimiento in movimientos:
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
        
        # Agregar detalles de los pickings consolidados a las observaciones
        observaciones_completa = f"{observaciones_despacho}\n\nPedidos consolidados:\n" + "\n".join(detalles)
        
        # Como el despacho puede incluir múltiples productos, creamos un movimiento por cada producto
        # o podemos crear un solo movimiento con un producto "consolidado"
        # Voy a crear un solo movimiento con el primer producto como referencia
        primer_producto = list(productos.values())[0]
        
        cursor.execute("""
            INSERT INTO movimientos (
                tipo, producto_id, cantidad, referencia, observaciones, 
                estado, usuario_id, fecha_movimiento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'DESPACHO',
            primer_producto['producto_id'],
            sum(p['cantidad'] for p in productos.values()),  # Cantidad total
            referencia_despacho,
            observaciones_completa,
            'COMPLETADO',  # Los despachos se crean directamente como COMPLETADOS
            usuario_id,
            now
        ))
        
        despacho_id = cursor.lastrowid
        
        # Actualizar los movimientos de picking para marcar que fueron despachados
        # Podríamos agregar un campo o actualizar la referencia
        for movimiento in movimientos:
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
