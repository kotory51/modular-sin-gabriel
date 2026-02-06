from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSpinBox,
    QLineEdit, QPushButton, QHBoxLayout,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt

from database.stock_service import registrar_movimiento


class StockDialog(QDialog):

    def __init__(self, insumo: dict, parent=None):
        super().__init__(parent)
        self.insumo = insumo
        self.setWindowTitle(f"Stock – {insumo['nombre']}")
        self.setMinimumWidth(360)

        lay = QVBoxLayout(self)

        self.lbl_actual = QLabel(f"Stock actual: {insumo.get('stock_actual', 0)}")
        self.lbl_actual.setStyleSheet("font-weight:bold;")
        lay.addWidget(self.lbl_actual)

        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(["ENTRADA", "SALIDA", "AJUSTE", "MERMA"])
        lay.addWidget(self.cmb_tipo)

        self.spn = QSpinBox()
        self.spn.setRange(1, 100000)
        lay.addWidget(self.spn)

        self.lbl_preview = QLabel("")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.addWidget(self.lbl_preview)

        self.motivo = QLineEdit()
        self.motivo.setPlaceholderText("Motivo (obligatorio en salidas)")
        lay.addWidget(self.motivo)

        btns = QHBoxLayout()
        btns.addStretch()
        ok = QPushButton("Aplicar")
        ok.clicked.connect(self._save)
        btns.addWidget(ok)
        lay.addLayout(btns)

        self.spn.valueChanged.connect(self._update_preview)
        self.cmb_tipo.currentTextChanged.connect(self._update_preview)
        self._update_preview()

    def _update_preview(self):
        tipo = self.cmb_tipo.currentText()
        qty = self.spn.value()
        actual = self.insumo.get("stock_actual", 0)

        delta = qty if tipo in ("ENTRADA", "AJUSTE") else -qty
        self.lbl_preview.setText(
            f"Stock resultante: {actual + delta}"
        )

    def _save(self):
        tipo = self.cmb_tipo.currentText()
        qty = self.spn.value()

        cantidad = qty if tipo in ("ENTRADA", "AJUSTE") else -qty

        if tipo in ("SALIDA", "MERMA") and not self.motivo.text().strip():
            QMessageBox.warning(self, "Stock", "El motivo es obligatorio.")
            return

        try:
            registrar_movimiento(
                insumo_id=self.insumo["id"],
                cantidad=cantidad,
                tipo=tipo,
                motivo=self.motivo.text(),
                usuario="admin"  # luego login real
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
