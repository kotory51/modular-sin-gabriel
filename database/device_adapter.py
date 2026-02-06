"""
Adaptador de datos de dispositivos con soporte de fallback.
Implementa la lógica: BD → datos en tiempo real
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from database.devices_service import get_device_service


class DeviceDataAdapter:
    """
    Adaptador que proporciona datos de dispositivos con fallback inteligente.
    
    Prioridad:
    1. Datos en tiempo real (en parámetro realtime_data)
    2. Datos de la BD (si están recientes)
    3. Último registro de la BD (offline fallback)
    """
    
    def __init__(self, freshness_threshold_minutes: int = 5):
        """
        Args:
            freshness_threshold_minutes: tiempo máximo que se considera "fresco" un dato de BD
        """
        self.device_service = get_device_service()
        self.freshness_threshold = timedelta(minutes=freshness_threshold_minutes)
    
    def get_device_data(
        self, 
        device_id: str,
        realtime_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Obtiene datos de un dispositivo con fallback inteligente.
        
        Args:
            device_id: ID del dispositivo
            realtime_data: datos en tiempo real del dispositivo (opcional)
        
        Returns:
            Dict con datos del dispositivo o None si no hay datos disponibles
        """
        # 1. Si hay datos en tiempo real, usarlos con prioridad
        if realtime_data:
            return {
                **realtime_data,
                "_source": "realtime",
                "_timestamp": datetime.now().isoformat()
            }
        
        # 2. Intentar obtener datos recientes de la BD
        latest = self.device_service.get_latest_data(device_id)
        if latest:
            latest_dict = dict(latest)
            timestamp = datetime.fromisoformat(latest_dict.get("timestamp", ""))
            time_diff = datetime.now() - timestamp
            
            if time_diff <= self.freshness_threshold:
                # Datos frescos de la BD
                return {
                    **latest_dict,
                    "_source": "database_fresh",
                    "_age_seconds": int(time_diff.total_seconds())
                }
            else:
                # Datos antiguos, pero es lo que tenemos
                return {
                    **latest_dict,
                    "_source": "database_stale",
                    "_age_seconds": int(time_diff.total_seconds())
                }
        
        # 3. Sin datos disponibles
        return None
    
    def get_all_devices_data(
        self,
        realtime_devices: Optional[Dict[str, Dict]] = None
    ) -> Dict[str, Dict]:
        """
        Obtiene datos de todos los dispositivos con fallback.
        
        Args:
            realtime_devices: dict {device_id: realtime_data} (opcional)
        
        Returns:
            Dict {device_id: device_data}
        """
        realtime_devices = realtime_devices or {}
        result = {}
        
        # Obtener IDs de todos los dispositivos
        all_ids = set(self.device_service.get_all_device_ids())
        all_ids.update(realtime_devices.keys())
        
        for device_id in all_ids:
            data = self.get_device_data(
                device_id,
                realtime_devices.get(device_id)
            )
            if data:
                result[device_id] = data
        
        return result
    
    def is_data_fresh(self, device_id: str) -> bool:
        """Verifica si los datos de un dispositivo están frescos"""
        latest = self.device_service.get_latest_data(device_id)
        if not latest:
            return False
        
        timestamp = datetime.fromisoformat(latest["timestamp"])
        return (datetime.now() - timestamp) <= self.freshness_threshold
    
    def get_data_status(self, device_id: str) -> Dict[str, str]:
        """Obtiene estado de los datos de un dispositivo"""
        latest = self.device_service.get_latest_data(device_id)
        
        if not latest:
            return {
                "status": "no_data",
                "message": "Sin datos registrados"
            }
        
        timestamp = datetime.fromisoformat(latest["timestamp"])
        time_diff = datetime.now() - timestamp
        
        if time_diff <= self.freshness_threshold:
            return {
                "status": "fresh",
                "message": f"Datos frescos ({int(time_diff.total_seconds())}s)",
                "age_seconds": int(time_diff.total_seconds())
            }
        else:
            return {
                "status": "stale",
                "message": f"Datos del {timestamp.strftime('%H:%M:%S')}",
                "age_seconds": int(time_diff.total_seconds())
            }


# Instancia global
_adapter: Optional[DeviceDataAdapter] = None

def get_device_adapter(freshness_minutes: int = 5) -> DeviceDataAdapter:
    """Obtiene la instancia global del adaptador de dispositivos"""
    global _adapter
    if _adapter is None:
        _adapter = DeviceDataAdapter(freshness_minutes)
    return _adapter
