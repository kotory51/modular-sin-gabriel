from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import deque


class RealtimeChart(QWidget):
    def __init__(self, title: str, ylabel: str, max_points=60):
        super().__init__()

        self.data = deque(maxlen=max_points)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = Figure(figsize=(5, 2.5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(title, fontsize=11, fontweight="bold")
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True)

        self.line, = self.ax.plot([], [])

    def update_value(self, value: float):
        self.data.append(float(value))

        x = range(len(self.data))
        self.line.set_data(x, self.data)

        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw_idle()
