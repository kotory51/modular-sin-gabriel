from datetime import datetime


class HistorialBuffer:
    _registros = []

    @classmethod
    def agregar(cls, sensor: str, nivel: str, mensaje: str):
        if nivel not in ("warn", "alert"):
            return

        cls._registros.append({
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sensor": sensor, 
            "nivel": nivel,     
            "mensaje": mensaje
        })

        # límite de seguridad
        if len(cls._registros) > 500:
            cls._registros.pop(0)

    @classmethod
    def obtener_por_sensor(cls):
        """
        Retorna:
        {
            "temperatura": [ ... ],
            "humedad": [ ... ]
        }
        """
        resultado = {}

        for r in reversed(cls._registros):
            sensor = r["sensor"]
            resultado.setdefault(sensor, []).append(r)

        return resultado

    @classmethod
    def limpiar(cls):
        cls._registros.clear()
