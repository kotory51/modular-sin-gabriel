import time
from PyQt6.QtCore import QThread, pyqtSignal
from core.sensores.esp32_serial import ESP32Serial
import math

# Calcula punto de rocío, refresa "E" si t o h es "E"
def roc(t, h):
    if isinstance(t, str) or isinstance(h, str):
        return "E"
    a, b = (17.27, 237.7) if t >= 0 else (22.452, 272.55)
    g = math.log(h / 100.0) + (a * t) / (b + t)
    return round((b * g) / (a - g), 1)

class ESP32Worker(QThread):
    data_received = pyqtSignal(dict)
    error = pyqtSignal(str)          
    estado = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial = ESP32Serial()
        self._running = False
        self._config = None


    def reconectar(self, puerto: str, baudios: int):
        self._config = (puerto, baudios)
        if not self.isRunning():
            self._running = True
            self.start()

    def run(self):
        if not self._config:
            self.error.emit("ESP32 sin configuración")
            return

        puerto, baudios = self._config
        intentos = 0

        while self._running:
            if not self.serial.conectado:
                self.estado.emit("Reconectando ESP32...")
                if self.serial.conectar(puerto, baudios):
                    intentos = 0
                    self.estado.emit("ESP32 conectado")
                else:
                    intentos += 1
                    time.sleep(min(5, intentos))
                    continue

            datos = self.serial.leer()
            if datos:
                normalizado = self._normalizar(datos)
                if normalizado.get("ID"):
                    self.data_received.emit(normalizado)

            time.sleep(0.1)
    
    def _normalizar(self, d: dict) -> dict:
        return {
            "ID": str(d.get("id")).strip(),
            "T_Sonda": self._num(d.get("ts")),
            "Hum": self._num(d.get("h")),
            "Luz": self._num(d.get("lz")),
            "seq": self._num(d.get("seq")),
            "Bat": self._num(d.get("bat")),
            "Activo": d.get("bat") == "E",
            "Alarma": d.get("a", "N"),
            "Rocío": roc(self._num(d.get("ts")), self._num(d.get("h")))
        }
    
    def _num(self, v):
        try:
            return float(v)
        except Exception:
            return None

    def stop(self):
        self._running = False
        self.serial.cerrar()
        self.quit()
        self.wait()
