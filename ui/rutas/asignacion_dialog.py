from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QComboBox,
    QPushButton, QLabel, QMessageBox
)
from datetime import datetime

from database.vehiculos_db import fetch_vehiculos
from database.ruta_db import fetch_rutas
from database.users_db import fetch_all_users
from database.asignaciones_db import (
    vehiculo_disponible,
    chofer_disponible
)


class AsignacionDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva asignación")

        lay = QVBoxLayout(self)

        # ================= VEHÍCULOS =================
        self.cb_vehiculo = QComboBox()
        for v in fetch_vehiculos():
            if v["estado"] == "Disponible":
                self.cb_vehiculo.addItem(
                    f"{v['placa']} - {v['modelo']}",
                    v["id"]
                )

        # ================= RUTAS =====================
        self.cb_ruta = QComboBox()
        for r in fetch_rutas():
            self.cb_ruta.addItem(
                f"{r['origen']} → {r['destino']}",
                r["id"]
            )

        # ================= CHOFERES ==================
        self.cb_chofer = QComboBox()
        for u in fetch_all_users():
            if u.get("rol") == "Chofer":
                self.cb_chofer.addItem(
                    u["nombre"],
                    u["id"]
                )

        lay.addWidget(QLabel("Vehículo"))
        lay.addWidget(self.cb_vehiculo)

        lay.addWidget(QLabel("Ruta"))
        lay.addWidget(self.cb_ruta)

        lay.addWidget(QLabel("Chofer"))
        lay.addWidget(self.cb_chofer)

        btn = QPushButton("Crear asignación")
        btn.clicked.connect(self._validate)
        lay.addWidget(btn)

    # ================= VALIDACIONES =================
    def _validate(self):
        vehiculo_id = self.cb_vehiculo.currentData()
        chofer_id = self.cb_chofer.currentData()

        if not vehiculo_disponible(vehiculo_id):
            QMessageBox.warning(
                self, "Error",
                "Este vehículo ya tiene una asignación activa"
            )
            return

        if not chofer_disponible(chofer_id):
            QMessageBox.warning(
                self, "Error",
                "Este chofer ya tiene una asignación activa"
            )
            return

        self.accept()

    def get_data(self):
        return {
            "vehiculo_id": self.cb_vehiculo.currentData(),
            "ruta_id": self.cb_ruta.currentData(),
            "chofer_id": self.cb_chofer.currentData(),
            "estado": "Activa",
            "fecha_inicio": datetime.now().isoformat()
        }
