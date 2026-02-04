from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout,
    QPushButton
)

from database.vehiculos_db import fetch_vehiculos
from database.ruta_db import fetch_rutas
from database.users_db import fetch_all_users
from database.asignaciones_db import finalizar_asignacion


def vehiculo_nombre(vid):
    for v in fetch_vehiculos():
        if v["id"] == vid:
            return f"{v['placa']} - {v['modelo']}"
    return vid


def ruta_nombre(rid):
    for r in fetch_rutas():
        if r["id"] == rid:
            return f"{r['origen']} → {r['destino']}"
    return rid


def chofer_nombre(cid):
    for u in fetch_all_users():
        if u["id"] == cid:
            return u["nombre"]
    return cid


class AsignacionCard(QFrame):

    def __init__(self, data, on_finish=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.on_finish = on_finish

        self.setFixedSize(300, 210)
        self.setFrameShape(QFrame.Shape.Box)

        lay = QVBoxLayout(self)

        lay.addWidget(QLabel(f"<b>Asignación {data['id']}</b>"))
        lay.addWidget(QLabel(f" Vehículo: {vehiculo_nombre(data['vehiculo_id'])}"))
        lay.addWidget(QLabel(f" Ruta: {ruta_nombre(data['ruta_id'])}"))
        lay.addWidget(QLabel(f" Chofer: {chofer_nombre(data['chofer_id'])}"))
        lay.addWidget(QLabel(f"Estado: {data['estado']}"))

        if data["estado"] == "Activa":
            btn = QPushButton("Finalizar")
            btn.clicked.connect(self._finish)
            lay.addWidget(btn)

    def _finish(self):
        finalizar_asignacion(self.data["id"])
        if self.on_finish:
            self.on_finish(self.data)
