from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt


class VehiculoCard(QFrame):

    def __init__(self, data, on_edit=None, on_delete=None, parent=None):
        super().__init__(parent)
        self.data = data

     
        self.setFixedSize(260, 210)

        self.setStyleSheet("""
        QFrame {
            border: 1px solid #dcdcdc;
            border-radius: 10px;
            background: white;
        }
        """)

        lay = QVBoxLayout(self)
        lay.setSpacing(6)

        lbl_title = QLabel(f"{data['placa']}")
        lbl_title.setStyleSheet("font-weight:bold;font-size:14px;")
        lay.addWidget(lbl_title)

        lay.addWidget(QLabel(f"Modelo: {data['modelo']}"))
        lay.addWidget(QLabel(f"Capacidad: {data['capacidad']} kg"))
        lay.addWidget(QLabel(f"Estado: {data['estado']}"))

        lay.addStretch()

        btns = QHBoxLayout()

        if on_edit:
            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(lambda: on_edit(self.data))
            btns.addWidget(btn_edit)

        if on_delete:
            btn_del = QPushButton("Eliminar")
            btn_del.clicked.connect(lambda: on_delete(self.data))
            btns.addWidget(btn_del)

        lay.addLayout(btns)
