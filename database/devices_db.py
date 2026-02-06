"""
DEPRECADO: Usa database/devices_service.py en su lugar.

Este módulo mantiene compatibilidad hacia atrás pero delegaen el nuevo sistema.
"""

from database.devices_service import get_device_service
from typing import List, Dict, Optional

# Obtener el servicio unificado
_service = get_device_service()

# =========================
# COMPATIBILIDAD HACIA ATRÁS
# =========================

def init_db():
    """Inicializa la base de datos (ya se hace automáticamente)"""
    pass

def insert_device_data(data: dict):
    """Inserta datos de dispositivo (delegado a DeviceDataService)"""
    return _service.save_device_data(data)

def fetch_device_history(device_id: str, limit: int = 100) -> List[Dict]:
    """Obtiene historial de dispositivo"""
    return _service.get_device_history(device_id, limit)

def fetch_latest(device_id: str) -> Optional[Dict]:
    """Obtiene el último registro de un dispositivo"""
    return _service.get_latest_data(device_id)

def get_all_devices() -> List[str]:
    """Obtiene lista de todos los dispositivos únicos"""
    return _service.get_all_device_ids()

def get_device_stats(device_id: str = None) -> Dict:
    """Obtiene estadísticas de dispositivos"""
    return _service.get_device_stats(device_id) or {}

def get_latest_for_all_devices() -> List[Dict]:
    """Obtiene el último registro de cada dispositivo"""
    return _service.get_latest_all_devices()

def get_data_range(device_id: str, start_time: str, end_time: str) -> List[Dict]:
    """Obtiene datos dentro de un rango de tiempo"""
    return _service.get_data_range(device_id, start_time, end_time)

def fetch_unsynced():
    """
    Obtiene registros no sincronizados.
    NOTA: Requiere implementación adicional en DeviceDataService si se necesita.
    """
    # Placeholder para compatibilidad
    return []

def mark_as_synced(row_id: int):
    """Marca un registro como sincronizado"""
    return _service.mark_as_synced(row_id)

def delete_device_history(device_id: str):
    """Elimina historial de un dispositivo"""
    return _service.delete_device_history(device_id)

def clear_all():
    """Limpia todos los datos"""
    return _service.clear_all()

# ==========================================
# MENSAJE DE DEPRECACIÓN
# ==========================================
import warnings
warnings.warn(
    "database/devices_db.py está deprecado. "
    "Usa database/devices_service.py directamente.",
    DeprecationWarning,
    stacklevel=2
)