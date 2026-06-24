"""Servicio de gestión de anomalías en inspección."""

from database.db_manager import fetch_all, fetch_one, insert, update
from datetime import datetime


def create_anomaly(movimiento_id: int, tipo_anomalia: str, cantidad_danada: int, 
                  severidad: str, descripcion: str = "", foto_path: str = ""):
    """Registra una anomalía de inspección.
    
    Args:
        movimiento_id: ID del movimiento asociado
        tipo_anomalia: Tipo de anomalía (Físico, Oxidación, Vencido, Otro)
        cantidad_danada: Cantidad de productos dañados
        severidad: Nivel de severidad (Leve, Moderado, Grave)
        descripcion: Descripción detallada
        foto_path: Ruta de la foto evidencia
    """
    recorded_at = datetime.now().isoformat()
    
    query = """
        INSERT INTO anomalias_inspeccion 
        (movimiento_id, tipo_anomalia, cantidad_danada, severidad, descripcion, foto_path, registrado_en)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (movimiento_id, tipo_anomalia, cantidad_danada, severidad, descripcion, foto_path, recorded_at)
    return insert(query, params)


def get_anomalies_by_movement(movimiento_id: int):
    """Obtiene todas las anomalías de un movimiento."""
    query = "SELECT * FROM anomalias_inspeccion WHERE movimiento_id = ? ORDER BY registrado_en DESC"
    return fetch_all(query, (movimiento_id,))


def get_anomaly_by_id(anomaly_id: int):
    """Obtiene una anomalía por ID."""
    query = "SELECT * FROM anomalias_inspeccion WHERE id = ?"
    return fetch_one(query, (anomaly_id,))


def get_all_anomalies():
    """Obtiene todas las anomalías registradas."""
    query = """
        SELECT a.*, m.referencia, m.fecha_movimiento, p.sku, p.nombre 
        FROM anomalias_inspeccion a
        LEFT JOIN movimientos m ON a.movimiento_id = m.id
        LEFT JOIN productos p ON m.producto_id = p.id
        ORDER BY a.registrado_en DESC
    """
    return fetch_all(query)


def get_anomalies_by_severity(severidad: str):
    """Obtiene anomalías por nivel de severidad."""
    query = """
        SELECT a.*, m.referencia, m.fecha_movimiento, p.sku, p.nombre 
        FROM anomalias_inspeccion a
        LEFT JOIN movimientos m ON a.movimiento_id = m.id
        LEFT JOIN productos p ON m.producto_id = p.id
        WHERE a.severidad = ?
        ORDER BY a.registrado_en DESC
    """
    return fetch_all(query, (severidad,))


def get_anomalies_summary():
    """Obtiene resumen de anomalías por tipo y severidad."""
    query = """
        SELECT tipo_anomalia, severidad, COUNT(*) as total, SUM(cantidad_danada) as total_danado
        FROM anomalias_inspeccion
        GROUP BY tipo_anomalia, severidad
        ORDER BY total DESC
    """
    return fetch_all(query)


def update_anomaly_foto(anomaly_id: int, foto_path: str):
    """Actualiza la ruta de la foto de una anomalía."""
    query = "UPDATE anomalias_inspeccion SET foto_path = ? WHERE id = ?"
    return update(query, (foto_path, anomaly_id))
