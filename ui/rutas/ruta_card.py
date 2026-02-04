from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout
)


class RutaCard(QFrame):

    def __init__(self, data, on_edit=None, on_delete=None, parent=None):
        super().__init__(parent)
        self.data = data

        self.setFixedSize(260, 190)

        base_style = """
        QFrame {
            border: 1px solid #dcdcdc;
            border-radius: 10px;
            background: white;
        }
        """

        if data["estado"] == "Activa":
            base_style = """
            QFrame {
                border: 1px solid #f0ad4e;
                border-radius: 10px;
                background: #fff3cd;
            }
            """

        self.setStyleSheet(base_style)

        lay = QVBoxLayout(self)
        lay.setSpacing(6)

        lbl = QLabel(f"{data['origen']} → {data['destino']}")
        lbl.setStyleSheet("font-weight:bold;")
        lay.addWidget(lbl)

        lay.addWidget(QLabel(f"Distancia: {data.get('distancia', 'N/A')} km"))
        lay.addWidget(QLabel(f"Estado: {data['estado']}"))

        lay.addStretch()

        btns = QHBoxLayout()

        if on_edit:
            btn_edit = QPushButton("Editar")
            btn_edit.setEnabled(data["estado"] != "Activa")
            btn_edit.clicked.connect(lambda: on_edit(self.data))
            btns.addWidget(btn_edit)

        if on_delete:
            btn_del = QPushButton("Eliminar")
            btn_del.setEnabled(data["estado"] != "Activa")
            btn_del.clicked.connect(lambda: on_delete(self.data))
            btns.addWidget(btn_del)

        lay.addLayout(btns)
