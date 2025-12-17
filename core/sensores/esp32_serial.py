import json
import time
import math
import random
import threading
import serial
from queue import Queue
from typing import Dict, Union

class ESP32Serial:
    CAMPOS = ["ID", "T_Amb", "T_Sonda", "Hum", "Luz", "Rocío", "Bat", "Acc"]

    def __init__(self):
        self.ser = None
        self.simulacion = False

        self.puerto = None
        self.baudios = None

        self._sim_nodos = [0, 1, 2]
        self._cola_sim = Queue()
        self._hilos_sim = []
        self._stop_event = threading.Event()


    # CONFIGURACIÓN DE CONEXIÓN
  
    def configurar_conexion(self, puerto: Union[str, int], baudios: Union[int, float]) -> bool:
        self.puerto = puerto
        self.baudios = baudios

        if puerto == -1 and baudios == -1:
            print("[INFO] Modo de simulación activado.")
            self.simulacion = True
            self._iniciar_simulacion()
            return True

        try:
            self.ser = serial.Serial(puerto, baudios, timeout=1)
            self.simulacion = False
            print(f"[INFO] Conectado a {puerto}")
            return True
        except serial.SerialException as e:
            print(f"[ERROR] No se pudo abrir el puerto {puerto}: {e}")
            return False

    
    # RECONEXIÓN AUTOMÁTICA
  
    def _reconectar(self):
        if self.simulacion:
            return

        print("[INFO] Intentando reconectar...")
        try:
            if self.ser:
                self.ser.close()
            time.sleep(2)
            self.ser = serial.Serial(self.puerto, self.baudios, timeout=1)
            print("[INFO] Reconexión exitosa.")
        except serial.SerialException:
            print("[ERROR] Reconexión fallida.")

    
    # RECEPCIÓN DE DATOS
    
    def recibir_datos(self) -> Dict[str, Union[int, float]]:
        if self.simulacion:
            try:
                return self._cola_sim.get(timeout=1)
            except:
                return {}

        if not self.ser or not self.ser.is_open:
            self._reconectar()
            return {}

        try:
            linea = self.ser.readline().decode(errors="ignore").strip()
            if linea:
                datos_raw = json.loads(linea)
                return self._normalizar_datos(datos_raw)
            return {}

        except (serial.SerialException, OSError):
            print("[ADVERTENCIA] Conexión perdida.")
            self._reconectar()
            return {}

        except json.JSONDecodeError:
            print("[ADVERTENCIA] JSON inválido.")
            return {}

    
    # NORMALIZACIÓN DE DATOS
    
    def _normalizar_datos(self, datos_raw: dict) -> Dict[str, Union[int, float]]:
        datos_norm = {}
        for campo in self.CAMPOS:
            clave_json = self._mapear_clave(campo)
            datos_norm[campo] = datos_raw.get(clave_json, -255)
        return datos_norm

    def _mapear_clave(self, campo: str) -> str:
        return {
            "ID": "id",
            "T_Amb": "ta",
            "T_Sonda": "ts",
            "Hum": "h",
            "Luz": "lz",
            "Rocío": "roc",
            "Bat": "bat",
            "Acc": "a"
        }.get(campo, campo)

    # SIMULACIÓN
   
    def _iniciar_simulacion(self):
        self._stop_event.clear()
        for nodo_id in self._sim_nodos:
            hilo = threading.Thread(target=self._hilo_sim_nodo, args=(nodo_id,))
            hilo.daemon = True
            hilo.start()
            self._hilos_sim.append(hilo)

    def _hilo_sim_nodo(self, nodo_id: int):
        fase_base = random.uniform(0, 2 * math.pi)
        contador = 0

        while not self._stop_event.is_set():
            fase = fase_base + contador * 0.1

            T_Amb = 22 + 3 * math.sin(fase)
            T_Sonda = T_Amb + 2 + 0.5 * math.sin(fase + 1.5)
            Hum = 45 + 10 * math.sin(fase - 1)
            Luz = 300 + 150 * math.sin(fase + 0.5)
            Rocio = T_Sonda - ((100 - Hum) / 5.0)
            Bat = 80 + 10 * math.sin(fase / 2)
            Acc = 0.3 + 0.2 * math.sin(fase * 3.1 + nodo_id) + random.uniform(-0.05, 0.05)

            datos = {
                "ID": nodo_id,
                "T_Amb": round(T_Amb, 2),
                "T_Sonda": round(T_Sonda, 2),
                "Hum": round(Hum, 2),
                "Luz": round(Luz, 2),
                "Rocío": round(Rocio, 2),
                "Bat": round(Bat, 2),
                "Acc": round(Acc, 3)
            }

            self._cola_sim.put(datos)
            contador += 1
            time.sleep(10 + random.uniform(-2, 2))

    # ENVÍO DE TEXTO
    
    def enviar_texto(self, mensaje: str) -> bool:
        if self.simulacion:
            print(f"[SIMULACIÓN] Enviando: {mensaje}")
            return True

        if not self.ser or not self.ser.is_open:
            self._reconectar()
            return False

        try:
            self.ser.write(mensaje.encode())
            return True
        except serial.SerialException:
            print("[ERROR] Error al enviar.")
            self._reconectar()
            return False

    
    # RECEPCIÓN DE TEXTO
   
    def recibir_texto(self) -> str:
        if self.simulacion:
            return "[SIMULACIÓN] texto recibido"

        if not self.ser or not self.ser.is_open:
            self._reconectar()
            return ""

        try:
            return self.ser.readline().decode(errors="ignore").strip()
        except serial.SerialException:
            print("[ERROR] Error al recibir texto.")
            self._reconectar()
            return ""

  
    # CIERRE
   
    def cerrar_conexion(self):
        self._stop_event.set()
        if self.ser and self.ser.is_open:
            self.ser.close()
        print("[INFO] Conexión cerrada.")


