from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton,
    QComboBox, QFileDialog
)


class VehiculoDialog(QDialog):

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vehículo")

        self.data = data or {}

        lay = QVBoxLayout(self)

        self.placa = QLineEdit(self.data.get("placa", ""))
        self.modelo = QLineEdit(self.data.get("modelo", ""))
        self.capacidad = QLineEdit(str(self.data.get("capacidad", "")))

        self.estado = QComboBox()
        self.estado.addItems(["Disponible", "En ruta", "Mantenimiento"])
        self.estado.setCurrentText(self.data.get("estado", "Disponible"))

        self.tarjeta = QLineEdit(self.data.get("tarjeta_circulacion", ""))
        btn_img = QPushButton("Subir tarjeta")
        btn_img.clicked.connect(self._pick_image)

        lay.addWidget(QLabel("Placa"))
        lay.addWidget(self.placa)

        lay.addWidget(QLabel("Modelo"))
        lay.addWidget(self.modelo)

        lay.addWidget(QLabel("Capacidad (kg)"))
        lay.addWidget(self.capacidad)

        lay.addWidget(QLabel("Estado"))
        lay.addWidget(self.estado)

        lay.addWidget(QLabel("Tarjeta de circulación"))
        lay.addWidget(self.tarjeta)
        lay.addWidget(btn_img)

        btn = QPushButton("Guardar")
        btn.clicked.connect(self.accept)
        lay.addWidget(btn)

        if self.data.get("estado") == "En ruta":
            self._lock_fields()

    def _lock_fields(self):
        for w in (self.placa, self.modelo, self.capacidad, self.estado):
            w.setEnabled(False)

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg)"
        )
        if path:
            self.tarjeta.setText(path)

    def get_data(self):
        return {
            "id": self.data.get("id"),
            "placa": self.placa.text(),
            "modelo": self.modelo.text(),
            "capacidad": int(self.capacidad.text()),
            "estado": self.estado.currentText(),
            "tarjeta_circulacion": self.tarjeta.text()
        }
