import time
from PyQt6.QtCore import QThread, pyqtSignal
from core.sensores.esp32_serial import ESP32Serial
import math

# Calcula punto de rocío, regresa "E" si t o h es "E"
#def roc(t, h):
    #if isinstance(t, str) or isinstance(h, str):
        #return "E"
    #a, b = (17.27, 237.7) if t >= 0 else (22.452, 272.55)
    #g = math.log(h / 100.0) + (a * t) / (b + t)
    #return round((b * g) / (a - g), 1)

def roc(t, h):
    if t is None or h is None:
        return None

    if h <= 0:
        return None  

    a = 17.27
    b = 237.7

    g = math.log(h / 100.0) + (a * t) / (b + t)
    return (b * g) / (a - g)


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

    def _normalizar(self, d: dict) -> dict:
        return {
            "ID": str(d.get("id")).strip(),
            "T_Sonda": self._num(d.get("ts")),
            "T_Amb": self._num(d.get("ta")),
            "Hum": self._num(d.get("h")),
            "Luz": self._num(d.get("lz")),
            "seq": self._num(d.get("seq")),
            "Aceleracion": self._num(d.get("a")),
            "Bat": self._num(d.get("bat")),
            "Activo": d.get("bat") == "E",
            "Alarma": d.get("a", "N"),
            "Rocio": roc(self._num(d.get("ts")), self._num(d.get("h")))
        }
    
    def run(self):
        if not self._config:
            self.error.emit("ESP32 sin configuración")
            return

        puerto, baudios = self._config
        intentos = 0
        max_reintentos = 5

        while self._running:
            if not self.serial.conectado:
                if intentos < max_reintentos:
                    print(f"[ESP32] Dispositivo {puerto} reconectando (intento {intentos + 1}/{max_reintentos})")
                    self.estado.emit(f"Reconectando ESP32 ({intentos + 1}/{max_reintentos})...")
                    if self.serial.conectar(puerto, baudios):
                        intentos = 0
                        self.estado.emit("ESP32 conectado")
                    else:
                        intentos += 1
                        espera = min(16, 2 ** (intentos - 1))
                        time.sleep(espera)
                        continue
                else:
                    self.estado.emit("ESP32: máx reintentos alcanzado, esperando...")
                    time.sleep(30)
                    intentos = 0
                    continue

            datos = self.serial.leer()
            if datos:
                normalizado = self._normalizar(datos)
                if normalizado.get("ID"):
                    self.data_received.emit(normalizado)
            else:
                if not self.serial.conectado:
                    intentos = 0

            time.sleep(0.1)
    
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
