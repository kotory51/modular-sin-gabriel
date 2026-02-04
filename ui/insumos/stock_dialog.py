from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSpinBox, QLineEdit, QPushButton, QHBoxLayout
from database.insumos_db import add_stock

class StockDialog(QDialog):

    def __init__(self, insumo: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Stock - {insumo['nombre']}")
        self.insumo = insumo

        lay = QVBoxLayout(self)

        lay.addWidget(QLabel(f"Stock actual: {insumo.get('stock_actual',0)}"))

        self.spn = QSpinBox()
        self.spn.setRange(-100000, 100000)
        lay.addWidget(self.spn)

        self.motivo = QLineEdit()
        self.motivo.setPlaceholderText("Motivo")
        lay.addWidget(self.motivo)

        btns = QHBoxLayout()
        ok = QPushButton("Aplicar")
        ok.clicked.connect(self._save)
        btns.addStretch()
        btns.addWidget(ok)
        lay.addLayout(btns)

    def _save(self):
        if self.spn.value() != 0:
            add_stock(self.insumo["id"], self.spn.value(), self.motivo.text())
        self.accept()
