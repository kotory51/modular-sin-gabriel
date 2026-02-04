from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QComboBox, QPushButton, QHBoxLayout
)
import serial.tools.list_ports


class Puertos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar ESP32")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.cmb_port = QComboBox()
        self.cmb_baud = QComboBox()

        self.cmb_baud.addItems(["115200"])
        self._cargar_puertos()

        form.addRow("Puerto COM:", self.cmb_port)
        form.addRow("Baudios:", self.cmb_baud)

        layout.addLayout(form)

        botones = QHBoxLayout()
        btn_ok = QPushButton("Conectar")
        btn_cancel = QPushButton("Cancelar")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        botones.addStretch()
        botones.addWidget(btn_cancel)
        botones.addWidget(btn_ok)
        layout.addLayout(botones)

    def _cargar_puertos(self):
        self.cmb_port.clear()
        for p in serial.tools.list_ports.comports():
            self.cmb_port.addItem(p.device)

    def get_config(self):
        return self.cmb_port.currentText(), int(self.cmb_baud.currentText())
