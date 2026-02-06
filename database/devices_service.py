"""
Servicio unificado de dispositivos.
Maneja: guardar datos → recuperar datos → fallback en tiempo real
"""

from datetime import datetime
from typing import Dict, List, Optional
from database.db_service import get_db_service

class DeviceDataService:
    """Servicio unificado para gestión de datos de dispositivos"""
    
    def __init__(self):
        self.db = get_db_service("data/device_data.db")
        self._init_db()
    
    def _init_db(self):
        """Inicializa la estructura de la base de datos"""
        with self.db.get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS device_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                temp_sonda REAL,
                temp_amb REAL,
                humedad REAL,
                luz REAL,
                aceleracion REAL,
                bateria REAL,
                alarma TEXT,
                activo INTEGER,
                punto_rocio REAL,
                seq INTEGER,
                timestamp TEXT NOT NULL,
                synced INTEGER DEFAULT 0,
                last_sync TEXT
            )
            """)
            
            conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_timestamp
            ON device_data (device_id, timestamp DESC)
            """)
            
            conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_latest
            ON device_data (device_id, id DESC)
            """)
            
            conn.commit()
    
    # ==================== INSERCIÓN ====================
    def save_device_data(self, data: dict, timestamp: Optional[str] = None) -> int:
        """
        Guarda datos de un dispositivo en la BD.
        
        Args:
            data: dict con campos {ID, T_Sonda, T_Amb, Hum, Luz, Aceleracion, Bat, Alarma, Activo, Rocio, seq}
            timestamp: timestamp personalizado (por defecto ahora)
        
        Returns:
            ID del registro insertado
        """
        payload = {
            "device_id": str(data.get("ID", "")).strip(),
            "temp_sonda": data.get("T_Sonda"),
            "temp_amb": data.get("T_Amb"),
            "humedad": data.get("Hum"),
            "luz": data.get("Luz"),
            "aceleracion": data.get("Aceleracion"),
            "bateria": data.get("Bat"),
            "alarma": data.get("Alarma"),
            "activo": int(bool(data.get("Activo"))),
            "punto_rocio": data.get("Rocio"),
            "seq": data.get("seq"),
            "timestamp": timestamp or datetime.now().isoformat(),
            "synced": 0,
            "last_sync": None
        }
        
        query = """
        INSERT INTO device_data (
            device_id, temp_sonda, temp_amb, humedad, luz,
            aceleracion, bateria, alarma, activo, punto_rocio, seq,
            timestamp, synced, last_sync
        ) VALUES (
            :device_id, :temp_sonda, :temp_amb, :humedad, :luz,
            :aceleracion, :bateria, :alarma, :activo, :punto_rocio, :seq,
            :timestamp, :synced, :last_sync
        )
        """
        
        return self.db.execute_insert(query, payload)
    
    def save_device_data_batch(self, data_list: List[dict]) -> int:
        """Guarda múltiples registros en una transacción"""
        with self.db.get_connection() as conn:
            for data in data_list:
                self.save_device_data(data)
            return len(data_list)
    
    # ==================== CONSULTAS ====================
    def get_latest_data(self, device_id: str) -> Optional[Dict]:
        """
        Obtiene el último registro de un dispositivo.
        Usa para fallback en caso de que el dispositivo esté offline.
        """
        query = """
        SELECT * FROM device_data
        WHERE device_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
        """
        return self.db.execute_one(query, (device_id,))
    
    def get_device_history(self, device_id: str, limit: int = 100) -> List[Dict]:
        """Obtiene el historial de un dispositivo"""
        query = """
        SELECT * FROM device_data
        WHERE device_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """
        return self.db.execute_query(query, (device_id, limit))
    
    def get_latest_all_devices(self) -> List[Dict]:
        """Obtiene el último registro de cada dispositivo"""
        query = """
        SELECT d1.* 
        FROM device_data d1
        WHERE d1.id = (
            SELECT id FROM device_data d2 
            WHERE d2.device_id = d1.device_id
            ORDER BY d2.timestamp DESC
            LIMIT 1
        )
        ORDER BY d1.device_id
        """
        return self.db.execute_query(query)
    
    def get_all_device_ids(self) -> List[str]:
        """Obtiene lista única de IDs de dispositivos"""
        query = "SELECT DISTINCT device_id FROM device_data ORDER BY device_id"
        results = self.db.execute_query(query)
        return [row["device_id"] for row in results]
    
    def get_data_range(self, device_id: str, start_time: str, end_time: str) -> List[Dict]:
        """Obtiene datos dentro de un rango de tiempo"""
        query = """
        SELECT * FROM device_data
        WHERE device_id = ? 
        AND timestamp BETWEEN ? AND ?
        ORDER BY timestamp
        """
        return self.db.execute_query(query, (device_id, start_time, end_time))
    
    def get_device_stats(self, device_id: Optional[str] = None) -> Dict:
        """Obtiene estadísticas de un dispositivo o de todos"""
        if device_id:
            query = """
            SELECT COUNT(*) as total,
                   MIN(timestamp) as primer,
                   MAX(timestamp) as ultimo
            FROM device_data
            WHERE device_id = ?
            """
            return self.db.execute_one(query, (device_id,)) or {}
        else:
            query = """
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT device_id) as dispositivos,
                   MIN(timestamp) as primer,
                   MAX(timestamp) as ultimo
            FROM device_data
            """
            return self.db.execute_one(query) or {}
    
    # ==================== ACTUALIZACIONES ====================
    def mark_as_synced(self, row_id: int) -> int:
        """Marca un registro como sincronizado"""
        query = """
        UPDATE device_data
        SET synced = 1, last_sync = ?
        WHERE id = ?
        """
        return self.db.execute_update(query, (datetime.now().isoformat(), row_id))
    
    def mark_device_as_synced(self, device_id: str) -> int:
        """Marca todos los registros de un dispositivo como sincronizados"""
        query = """
        UPDATE device_data
        SET synced = 1, last_sync = ?
        WHERE device_id = ? AND synced = 0
        """
        return self.db.execute_update(query, (datetime.now().isoformat(), device_id))
    
    # ==================== MANTENIMIENTO ====================
    def delete_device_history(self, device_id: str) -> int:
        """Elimina todo el historial de un dispositivo"""
        query = "DELETE FROM device_data WHERE device_id = ?"
        return self.db.execute_update(query, (device_id,))
    
    def delete_old_data(self, days: int = 30) -> int:
        """Elimina datos más antiguos que N días"""
        query = """
        DELETE FROM device_data
        WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')
        """
        return self.db.execute_update(query, (days,))
    
    def clear_all(self) -> int:
        """⚠️ Limpia TODOS los datos"""
        query = "DELETE FROM device_data"
        return self.db.execute_update(query)


# Instancia global
_device_service: Optional[DeviceDataService] = None

def get_device_service() -> DeviceDataService:
    """Obtiene la instancia global del servicio de dispositivos"""
    global _device_service
    if _device_service is None:
        _device_service = DeviceDataService()
    return _device_service
