from PyQt6.QtCore import QObject, pyqtSignal


class DevicesController(QObject):
    devices_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.devices: list[dict] = []


    def handle_esp32_data(self, data: dict):
        if "ID" not in data:
            return

        dev_id = str(data["ID"])
        idx = self._idx(dev_id)

        if idx != -1 and not self.devices[idx].get("active", True):
            return

        if idx == -1:
            self.devices.append(self._nuevo(dev_id, data))
        else:
            self._actualizar(idx, data)

        self.devices_updated.emit(self.devices)

    def _nuevo(self, dev_id, data):
        return {
            "id": dev_id,
            "name": f"Dispositivo {dev_id}",
            "connections": "",
            "location": "",
            "battery": int(data.get("battery", 100)),
            "active": True,
            "foto": None,
            "temp_amb": data.get("T_Amb"),
            "humedad": data.get("Hum"),
            "golpe": data.get("golpe"),
            "luz": data.get("Luz"),
            "temp_sonda": data.get("T_Sonda"),
            "punto_condensacion": data.get("Rocío"),
        }

    def _actualizar(self, idx, data):
        d = self.devices[idx]
        mapa = {
            "T_Amb": "temp_amb",
            "Hum": "humedad",
            "golpe": "golpe",
            "Luz": "luz",
            "T_Sonda": "temp_sonda",
            "Rocío": "punto_condensacion",
            "battery": "battery",
        }
        for k_in, k_out in mapa.items():
            if k_in in data:
                d[k_out] = data[k_in]


    def add_manual(self):
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
            "punto_condensacion": None
        })
        self.devices_updated.emit(self.devices)

    def update(self, dev_id, datos):
        idx = self._idx(dev_id)
        if idx != -1:
            self.devices[idx] = datos
            self.devices_updated.emit(self.devices)

    def toggle_active(self, dev_id):
        idx = self._idx(dev_id)
        if idx != -1:
            self.devices[idx]["active"] = not self.devices[idx]["active"]
            self.devices_updated.emit(self.devices)

    def delete(self, dev_id):
        idx = self._idx(dev_id)
        if idx != -1:
            self.devices.pop(idx)
            self.devices_updated.emit(self.devices)

    def _idx(self, dev_id):
        for i, d in enumerate(self.devices):
            if d["id"] == dev_id:
                return i
        return -1
