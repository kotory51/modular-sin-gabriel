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
                timeout=2,
                write_timeout=2
            )
            time.sleep(2.5)  # Esperar a que ESP32 esté listo
            self.conectado = True
            print(f"[ESP32] Conectado a {puerto}")
            return True

        except FileNotFoundError as e:
            print(f"[ESP32] Puerto {puerto} no encontrado: {e}")
            self.conectado = False
            self.ser = None
            return False
        except PermissionError as e:
            print(f"[ESP32] Permiso denegado en {puerto}: {e}")
            self.conectado = False
            self.ser = None
            return False
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

        except serial.SerialException as e:
            # Error de conexión real (puerto desconectado, etc)
            print(f"[ESP32] Desconectado ({e})")
            self.conectado = False
            self.cerrar()
            return None
        
        except Exception as e:
            # Errores críticos del puerto (ClearCommError, PermissionError, etc)
            # que requieren reconexión
            if "ClearCommError" in str(e) or "PermissionError" in str(e):
                print(f"[ESP32] Error crítico, reconectando ({e})")
                self.conectado = False
                self.cerrar()
            else:
                # Otros errores transitorios - no marcar como desconectado
                print(f"[ESP32] Error temporal (ignorado): {e}")
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
