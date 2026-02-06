from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class TrendIndicator(QFrame):
    def __init__(self, titulo: str):
        super().__init__()
        self.titulo = titulo
        self._build()

    def _build(self):
        self.setFixedHeight(70)
        self.setStyleSheet("background:#eef3f7; border-radius:14px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        self.lbl_title = QLabel(self.titulo)
        self.lbl_title.setStyleSheet("font-weight:600;")

        self.lbl_trend = QLabel("Tendencia: --")
        self.lbl_r2 = QLabel("R²: --")

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_trend)
        layout.addWidget(self.lbl_r2)

    def actualizar(self, pendiente: float, r2: float):
        if pendiente > 0.02:
            texto = "↑ Ascendente"
            color = "#2ecc71"
        elif pendiente < -0.02:
            texto = "↓ Descendente"
            color = "#e74c3c"
        else:
            texto = "→ Estable"
            color = "#f1c40f"

        self.lbl_trend.setText(f"Tendencia: {texto}")
        self.lbl_r2.setText(f"R²: {r2}")

        self.setStyleSheet(f"""
            background:#eef3f7;
            border-radius:14px;
            border-left: 6px solid {color};
        """)
