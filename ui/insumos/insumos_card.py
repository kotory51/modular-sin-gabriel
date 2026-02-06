from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from typing import Optional

def evaluar_stock(insumo: dict) -> str:
    stock = insumo.get("stock_actual", 0)
    minimo = insumo.get("stock_minimo", 10)

    if stock < minimo:
        return "CRITICO"
    elif stock == minimo:
        return "BAJO"
    return "OK"

class InsumoCard(QFrame):

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)   # 1️⃣ SIEMPRE PRIMERO

        # 2️⃣ Guardar datos
        self._data = data
        self.setProperty("data", data)

        # 3️⃣ Configuración base
        self.setStyleSheet("""
            QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 8px; }
            QLabel { color: #222; }
            QPushButton { padding: 4px 8px; border-radius: 6px; }
        """)
        self.setFixedSize(280, 280)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # 4️⃣ Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Título
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_title)

        # Foto
        self.lbl_img = QLabel()
        self.lbl_img.setFixedSize(100, 100)
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_img, 0, Qt.AlignmentFlag.AlignHCenter)

        # Subtítulo
        self.lbl_sub = QLabel()
        layout.addWidget(self.lbl_sub)

        # Detalles
        self.lbl_row1 = QLabel()
        self.lbl_row2 = QLabel()
        layout.addWidget(self.lbl_row1)
        layout.addWidget(self.lbl_row2)

        # Stock
        self.lbl_stock = QLabel()
        self.lbl_stock.setStyleSheet("font-size:11px;color:#555;")
        layout.addWidget(self.lbl_stock)

        layout.addStretch()

        # Botones
        btns = QHBoxLayout()
        self.btn_edit = QPushButton("Editar")
        self.btn_del = QPushButton("Eliminar")
        self.btn_stock = QPushButton("Stock")
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_del)
        btns.addWidget(self.btn_stock)
        layout.addLayout(btns)

        # 5️⃣ AHORA SÍ → aplicar datos y alertas
        self.update_visual(self._data)


    def _subtitle(self) -> str:
        return self._data.get("tipo", "")

    def _short_row1(self) -> str:
        t = self._data.get("tipo", "")
        if t == "Medicamento":
            return f"Lote: {self._data.get('lote','')}"
        if t == "Dispositivo Médico":
            return f"Marca/Modelo: {self._data.get('marca','')} {self._data.get('modelo','')}"
        return f"Fabricante: {self._data.get('fabricante','')}"

    def _short_row2(self) -> str:
        t = self._data.get("tipo", "")
        if t == "Medicamento":
            return f"Cad: {self._data.get('fecha_caducidad','')}"
        if t == "Dispositivo Médico":
            return f"Fabr: {self._data.get('fecha_fabricacion','')}"
        return f"Dosis: {self._data.get('dosis','')}"

    def _update_image(self, path: Optional[str]):
        if path:
            try:
                pm = QPixmap(path).scaled(
                    160, 100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.lbl_img.setPixmap(pm)
            except Exception:
                self.lbl_img.setText("Sin imagen")
        else:
            self.lbl_img.setText("Sin imagen")
            self.lbl_img.setStyleSheet("color: #999; font-style: italic;")

    def update_visual(self, data: dict):
        self._data = data
        self.setProperty("data", data)

        self.lbl_title.setText(data.get("nombre", "Sin nombre"))
        self.lbl_sub.setText(self._subtitle())
        self.lbl_row1.setText(self._short_row1())
        self.lbl_row2.setText(self._short_row2())
        self.lbl_stock.setText(f"Stock: {data.get('stock_actual', 0)}")
        self._update_image(data.get("foto"))

        # ===== ALERTA DE STOCK =====
        estado = evaluar_stock(data)

        if estado == "CRITICO":
            self.setStyleSheet("""
                QFrame {
                    background: #ffebee;
                    border: 2px solid #c62828;
                    border-radius: 8px;
                }
                QLabel { color: #b71c1c; }
            """)
            self.lbl_stock.setText(f" Stock crítico ({data.get('stock_actual', 0)})")

        elif estado == "BAJO":
            self.setStyleSheet("""
                QFrame {
                    background: #fffde7;
                    border: 2px solid #f9a825;
                    border-radius: 8px;
                }
                QLabel { color: #6d4c41; }
            """)
            self.lbl_stock.setText(f" Stock mínimo ({data.get('stock_actual', 0)})")

        else:
            self.setStyleSheet("""
                QFrame {
                    background: #e8f5e9;
                    border: 2px solid #2e7d32;
                    border-radius: 8px;
                }
                QLabel { color: #1b5e20; }
            """)
            self.lbl_stock.setText(f" Stock OK ({data.get('stock_actual', 0)})")


