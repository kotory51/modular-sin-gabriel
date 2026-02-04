from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox
)

ESTADOS = ("Activa", "Suspendida", "Finalizada")


class RutaDialog(QDialog):

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ruta")

        self._data = data or {}

        root = QVBoxLayout(self)

        self.in_origen = QLineEdit(self._data.get("origen", ""))
        self.in_destino = QLineEdit(self._data.get("destino", ""))
        self.in_distancia = QLineEdit(
            str(self._data.get("distancia", "")))

        self.cb_estado = QComboBox()
        self.cb_estado.addItems(ESTADOS)
        if data:
            self.cb_estado.setCurrentText(data["estado"])

        root.addWidget(QLabel("Origen"))
        root.addWidget(self.in_origen)

        root.addWidget(QLabel("Destino"))
        root.addWidget(self.in_destino)

        root.addWidget(QLabel("Distancia (km)"))
        root.addWidget(self.in_distancia)

        root.addWidget(QLabel("Estado"))
        root.addWidget(self.cb_estado)

        actions = QHBoxLayout()
        actions.addStretch()

        btn_ok = QPushButton("Guardar")
        btn_ok.clicked.connect(self.accept)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)

        actions.addWidget(btn_cancel)
        actions.addWidget(btn_ok)

        root.addLayout(actions)

    def get_data(self):
        return {
            "origen": self.in_origen.text(),
            "destino": self.in_destino.text(),
            "distancia": int(self.in_distancia.text() or 0),
            "estado": self.cb_estado.currentText()
        }
