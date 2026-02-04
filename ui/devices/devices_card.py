from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


class TarjetaDispositivo(QFrame):
    def __init__(self, datos: dict, parent=None):
        super().__init__(parent)

        self.datos = datos

        
        self.setFixedSize(260, 170)   
        self.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(6)

       
        header = QHBoxLayout()

        self.lbl_img = QLabel()
        self.lbl_img.setFixedSize(48, 48)
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_img.setStyleSheet("""
            QLabel {
                background: #f2f2f2;
                border-radius: 6px;
            }
        """)
        header.addWidget(self.lbl_img)

        self.lbl_nombre = QLabel()
        self.lbl_nombre.setStyleSheet("""
            font-weight: 600;
            font-size: 13px;
        """)
        header.addWidget(self.lbl_nombre)
        header.addStretch()

        root.addLayout(header)

       
        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet("""
            font-size: 11px;
            color: #555;
        """)
        root.addWidget(self.lbl_info)

       
        self.lbl_estado = QLabel()
        self.lbl_estado.setStyleSheet("""
            font-size: 10px;
            color: #888;
        """)
        root.addWidget(self.lbl_estado)

        acciones = QHBoxLayout()

        self.btn_toggle = QPushButton()
        self.btn_toggle.setFixedHeight(24)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 11px;
                padding: 2px 8px;
            }
        """)

        self.btn_edit = QPushButton("✏️")
        self.btn_edit.setFixedSize(28, 24)

        self.btn_del = QPushButton("🗑️")
        self.btn_del.setFixedSize(28, 24)

        acciones.addWidget(self.btn_toggle)
        acciones.addStretch()
        acciones.addWidget(self.btn_edit)
        acciones.addWidget(self.btn_del)

        root.addLayout(acciones)

        self.actualizar_visual(datos, "Sin datos")

 
    def actualizar_visual(self, datos: dict, texto_estado: str):
        self.datos = datos

        self.lbl_nombre.setText(
            datos.get("name") or f"Dispositivo {datos.get('id', '')}"
        )

        self.lbl_info.setText(
            f" {datos.get('battery', '--')}%   "
            f" {datos.get('temp', '--')}°C   "
            f" {datos.get('hum', '--')}%"
        )

        self.lbl_estado.setText(f"📡 {texto_estado}")

        
        ruta = datos.get("foto")
        if ruta:
            pix = QPixmap(ruta)
            if not pix.isNull():
                self.lbl_img.setPixmap(
                    pix.scaled(
                        self.lbl_img.size(),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
        else:
            self.lbl_img.setPixmap(QPixmap())

        
        activo = datos.get("active", True)

        self.btn_toggle.setText("Desactivar" if activo else "Activar")

        self.setStyleSheet("""
            QFrame {
                background: %s;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }
        """ % ("#ffffff" if activo else "#f2f2f2"))
