from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel,
    QFileDialog, QHBoxLayout, QComboBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
import serial.tools.list_ports


class DispositivoDialog(QDialog):
    def __init__(self, datos: dict | None = None, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Dispositivo")
        self.setMinimumWidth(380)

        self.datos = datos if isinstance(datos, dict) else {}

        root = QVBoxLayout(self)
        form = QFormLayout()

       
        self.input_id = QLineEdit()
        self.input_nombre = QLineEdit()

        form.addRow("ID:", self.input_id)
        form.addRow("Nombre:", self.input_nombre)

        self.combo_com = QComboBox()
        self.combo_baud = QComboBox()

        self._cargar_puertos()
        self.combo_baud.addItems([
            "9600", "19200", "38400", "57600", "115200"
        ])

        form.addRow("Puerto COM:", self.combo_com)
        form.addRow("Baudios:", self.combo_baud)

        root.addLayout(form)


        self.lbl_img = QLabel("Sin imagen")
        self.lbl_img.setFixedSize(260, 140)
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_img.setStyleSheet("""
            QLabel {
                border: 1px dashed #aaa;
                border-radius: 6px;
                background: #fafafa;
            }
        """)
        root.addWidget(self.lbl_img, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_img = QPushButton("Seleccionar imagen")
        self.btn_img.clicked.connect(self.seleccionar_imagen)
        root.addWidget(self.btn_img)

        botones = QHBoxLayout()
        btn_ok = QPushButton("Guardar")
        btn_cancel = QPushButton("Cancelar")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        botones.addStretch()
        botones.addWidget(btn_ok)
        botones.addWidget(btn_cancel)

        root.addLayout(botones)

        self._cargar_datos()

    def _cargar_puertos(self):
        self.combo_com.clear()
        puertos = serial.tools.list_ports.comports()

        for p in puertos:
            self.combo_com.addItem(p.device)

        if not puertos:
            self.combo_com.addItem("N/A")

   
    def _cargar_datos(self):
        self.input_id.setText(self.datos.get("id", ""))
        self.input_nombre.setText(self.datos.get("name", ""))

        
        com = self.datos.get("com")
        if com:
            idx = self.combo_com.findText(com)
            if idx >= 0:
                self.combo_com.setCurrentIndex(idx)

       
        baud = str(self.datos.get("baud", "115200"))
        idx = self.combo_baud.findText(baud)
        if idx >= 0:
            self.combo_baud.setCurrentIndex(idx)

      
        ruta = self.datos.get("foto")
        if ruta and os.path.exists(ruta):
            pix = QPixmap(ruta)
            self.lbl_img.setPixmap(
                pix.scaled(
                    self.lbl_img.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

   
    def seleccionar_imagen(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "",
            "Imágenes (*.png *.jpg *.jpeg)"
        )

        if not path:
            return

        self.datos["foto"] = path
        pix = QPixmap(path)
        self.lbl_img.setPixmap(
            pix.scaled(
                self.lbl_img.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

   
    def get_datos(self) -> dict:
        return {
            "id": self.input_id.text().strip(),
            "name": self.input_nombre.text().strip(),
            "foto": self.datos.get("foto"),
            "com": self.combo_com.currentText(),
            "baud": int(self.combo_baud.currentText()),
            "active": self.datos.get("active", True)
        }
