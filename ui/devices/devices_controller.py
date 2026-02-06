from PyQt6.QtCore import QObject, pyqtSignal
from database.devices_service import get_device_service
from database.device_adapter import get_device_adapter


class DevicesController(QObject):
    """
    Controlador de dispositivos con integración de BD.
    
    Flujo:
    1. ESP32 envía datos → handle_esp32_data()
    2. Se guardan en la BD
    3. Se envían a UI con fallback automático
    """
    devices_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.devices: list[dict] = []
        self.device_service = get_device_service()
        self.device_adapter = get_device_adapter()


    def handle_esp32_data(self, data: dict):
        """
        Maneja datos recibidos del ESP32.
        Guarda en BD y actualiza UI.
        """
        if "ID" not in data:
            return

        device_id = str(data["ID"]).strip()
        
        # 1. GUARDAR EN BD
        try:
            self.device_service.save_device_data(data)
        except Exception as e:
            print(f"[DEVICES] Error guardando datos de {device_id}: {e}")
        
        # 2. ACTUALIZAR EN MEMORIA Y UI
        idx = self._idx(device_id)

        if idx != -1 and not self.devices[idx].get("active", True):
            return

        if idx == -1:
            self.devices.append(self._nuevo(device_id, data))
        else:
            self._actualizar(idx, data)

        self.devices_updated.emit(self.devices)

    def _nuevo(self, dev_id, data):
        """Crea un nuevo registro de dispositivo con datos iniciales"""
        return {
            "id": dev_id,
            "name": f"Dispositivo {dev_id}",
            "connections": "",
            "location": "",
            "battery": int(data.get("Bat", 100)) if isinstance(data.get("Bat"), (int, float)) else 100,
            "active": True,
            "foto": None,
            "temp_amb": data.get("T_Amb"),
            "humedad": data.get("Hum"),
            "golpe": data.get("Aceleracion"),
            "luz": data.get("Luz"),
            "temp_sonda": data.get("T_Sonda"),
            "punto_condensacion": data.get("Rocio"),
            "_source": "realtime",
            "_synced": False
        }

    def _actualizar(self, idx, data):
        """Actualiza datos de un dispositivo existente"""
        d = self.devices[idx]
        mapa = {
            "T_Amb": "temp_amb",
            "Hum": "humedad",
            "Aceleracion": "golpe",
            "Luz": "luz",
            "T_Sonda": "temp_sonda",
            "Rocio": "punto_condensacion",
            "Bat": "battery",
        }
        for k_in, k_out in mapa.items():
            if k_in in data:
                valor = data[k_in]
                # Convertir a int si es batería
                if k_out == "battery" and isinstance(valor, (int, float)):
                    valor = int(valor)
                d[k_out] = valor
        
        d["_source"] = "realtime"
        d["_synced"] = False


    def add_manual(self):
        """Añade un dispositivo creado manualmente"""
        new_id = f"DVC-{len(self.devices)+1}"
        self.devices.append({
            "id": new_id,
            "name": f"Dispositivo {len(self.devices)+1}",
            "connections": "",
            "location": "",
            "battery": 100,
            "active": True,
            "foto": None,
            "temp_amb": None,
            "humedad": None,
            "golpe": None,
            "luz": None,
            "temp_sonda": None,
            "punto_condensacion": None,
            "_source": "manual",
            "_synced": True
        })
        self.devices_updated.emit(self.devices)

    def update(self, dev_id, datos):
        """Actualiza datos completos de un dispositivo"""
        idx = self._idx(dev_id)
        if idx != -1:
            self.devices[idx] = datos
            self.devices_updated.emit(self.devices)

    def toggle_active(self, dev_id):
        """Activa/desactiva un dispositivo"""
        idx = self._idx(dev_id)
        if idx != -1:
            self.devices[idx]["active"] = not self.devices[idx]["active"]
            self.devices_updated.emit(self.devices)

    def delete(self, dev_id):
        """Elimina un dispositivo"""
        idx = self._idx(dev_id)
        if idx != -1:
            self.devices.pop(idx)
            self.devices_updated.emit(self.devices)

    def get_device_history(self, dev_id: str, limit: int = 100) -> list:
        """Obtiene historial de un dispositivo desde BD"""
        return self.device_service.get_device_history(dev_id, limit)
    
    def get_device_stats(self, dev_id: str = None) -> dict:
        """Obtiene estadísticas de un dispositivo"""
        return self.device_service.get_device_stats(dev_id)
    
    def restore_from_database(self):
        """
        Restaura dispositivos desde la BD (para inicialización o recuperación).
        Mantiene en memoria los últimos datos de cada dispositivo.
        """
        latest_data = self.device_service.get_latest_all_devices()
        
        device_map = {}
        for record in latest_data:
            dev_id = record["device_id"]
            if dev_id not in device_map:
                device_map[dev_id] = {
                    "id": dev_id,
                    "name": f"Dispositivo {dev_id}",
                    "connections": "",
                    "location": "",
                    "battery": int(record.get("bateria", 100)) if record.get("bateria") else 100,
                    "active": True,
                    "foto": None,
                    "temp_amb": record.get("temp_amb"),
                    "humedad": record.get("humedad"),
                    "golpe": record.get("aceleracion"),
                    "luz": record.get("luz"),
                    "temp_sonda": record.get("temp_sonda"),
                    "punto_condensacion": record.get("punto_rocio"),
                    "_source": "database",
                    "_synced": True
                }
        
        self.devices = list(device_map.values())
        self.devices_updated.emit(self.devices)

    def _idx(self, dev_id):
        """Encuentra índice de un dispositivo por ID"""
        for i, d in enumerate(self.devices):
            if d["id"] == dev_id:
                return i
        return -1
