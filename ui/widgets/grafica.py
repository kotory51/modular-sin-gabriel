# ui/widgets/grafica.py

from collections import deque
import numpy as np

from PyQt6.QtWidgets import QFrame, QVBoxLayout
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.IA.regresion import regresion_lineal


class RealtimeChart(QFrame):
    def __init__(self, titulo: str, unidad: str, max_points=30):
        super().__init__()

        self.titulo = titulo
        self.unidad = unidad
        self.data = deque(maxlen=max_points)

        self._build()

    def _build(self):
        self.setStyleSheet("background:white; border-radius:18px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.fig = Figure(figsize=(6, 3))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)

        self.ax.set_title(self.titulo)
        self.ax.set_xlabel("Tiempo (muestras)")
        self.ax.set_ylabel(self.unidad)
        self.ax.grid(True)

        layout.addWidget(self.canvas)

    # ==========================
    # ACTUALIZAR CON DATOS REALES
    # ==========================
    def update_value(self, value: float):
        self.data.append(value)

        y = np.array(self.data)
        x = np.arange(len(y))

        self.ax.clear()
        self.ax.grid(True)
        self.ax.set_title(self.titulo)
        self.ax.set_xlabel("Tiempo (muestras)")
        self.ax.set_ylabel(self.unidad)

        # ==========================
        # DATOS REALES
        # ==========================
        self.ax.plot(
            x,
            y,
            "o",
            label="Datos"
        )

        # ==========================
        # REGRESIÓN LINEAL
        # ==========================
        if len(y) >= 3:
            pendiente, r2 = regresion_lineal(y.tolist())
            y_fit = pendiente * x + y.mean()

            self.ax.plot(
                x,
                y_fit,
                "-",
                label="Regresión lineal"
            )

            
            texto = (
                f"Pendiente = {pendiente:.4f}\n"
                f"R² = {r2:.4f}"
            )

            self.ax.text(
                0.02,
                0.98,
                texto,
                transform=self.ax.transAxes,
                ha="left",
                va="top",
                fontsize=9,
                bbox=dict(
                    facecolor="white",
                    alpha=0.85,
                    edgecolor="gray"
                )
            )

        self.ax.legend(loc="lower right")

        self.canvas.draw_idle()
