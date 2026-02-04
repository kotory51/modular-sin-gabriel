import serial
import json
import time


class ESP32Serial:
    def __init__(self):
        self.ser: serial.Serial | None = None
        self.conectado = False

    def conectar(self, puerto: str, baudios: int) -> bool:
        self.cerrar()
        time.sleep(0.5)  

        try:
            self.ser = serial.Serial(
                port=puerto,
                baudrate=baudios,
                timeout=1
            )
            time.sleep(2)  
            self.conectado = True
            print(f"[ESP32] Conectado a {puerto}")
            return True

        except Exception as e:
            print(f"[ESP32] Error conexión: {e}")
            self.conectado = False
            self.ser = None
            return False

   
    def leer(self) -> dict | None:
        if not self.conectado or not self.ser or not self.ser.is_open:
            return None

        try:
            linea = self.ser.readline()
            if not linea:
                return None

            return json.loads(linea.decode(errors="ignore").strip())

        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

        except Exception as e:
            print(f"[ESP32] Desconectado ({e})")
            self.conectado = False
            self.cerrar()
            return None

   
    def cerrar(self):
        try:
            if self.ser:
                if self.ser.is_open:
                    self.ser.close()
                    time.sleep(0.2)
        except Exception:
            pass

        self.ser = None
        self.conectado = False
