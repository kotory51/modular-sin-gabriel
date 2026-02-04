from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt

from ui.historial.historial_buffer import HistorialBuffer


class HistorialPage(QWidget):
    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        title = QLabel("Alertas del Dispositivo por Sensor")
        title.setStyleSheet("font-size:24px; font-weight:700;")
        root.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setSpacing(20)

        scroll.setWidget(self.container)
        root.addWidget(scroll, 1)

        self.refrescar()

    def refrescar(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        data = HistorialBuffer.obtener_por_sensor()

        if not data:
            lbl = QLabel("No hay advertencias ni alertas registradas.")
            lbl.setStyleSheet("font-size:14px; color:#666;")
            self.list_layout.addWidget(lbl)
            self.list_layout.addStretch()
            return

        for sensor, registros in data.items():
            self.list_layout.addWidget(self._build_sensor_section(sensor, registros))

        self.list_layout.addStretch()

    def _build_sensor_section(self, sensor, registros):
        section = QFrame()
        section.setStyleSheet("""
            background:white;
            border-radius:18px;
        """)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title = QLabel(sensor.upper())
        title.setStyleSheet("font-size:18px; font-weight:700;")
        layout.addWidget(title)

        for r in registros:
            layout.addWidget(
                self._build_item(
                    r["fecha"],
                    r["nivel"],
                    r["mensaje"]
                )
            )

        return section

    def _build_item(self, fecha, nivel, mensaje):
        card = QFrame()
        card.setStyleSheet("""
            background:#f4f6fa;
            border-radius:14px;
        """)
        card.setMinimumHeight(70)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)

        color = "#ff9800" if nivel == "warn" else "#f44336"
        icon = "🟠" if nivel == "warn" else "🔴"

        header = QLabel(f"{icon} {fecha}")
        header.setStyleSheet(f"""
            font-size:13px;
            font-weight:600;
            color:{color};
        """)

        body = QLabel(mensaje)
        body.setStyleSheet("font-size:13px;")
        body.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(body)

        return card
