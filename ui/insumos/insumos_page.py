from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QTabWidget, QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QFileDialog
)
from PyQt6.QtCore import Qt
from functools import partial
import csv
from typing import Optional

from ui.insumos.insumos_card import InsumoCard
from ui.insumos.insumos_form import InsumoDialog
from ui.insumos.stock_dialog import StockDialog  

from database.insumos_db import (
    init_db,
    fetch_all,
    insert,
    update,
    delete,
    next_id
)


class InsumosPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = {
            "Medicamento": [],
            "Dispositivo Médico": [],
            "Biológico": []
        }

        self.cards = {
            "Medicamento": {},
            "Dispositivo Médico": {},
            "Biológico": {}
        }

        self.setStyleSheet("""
            QWidget { background: #ffffff; font-family: 'Segoe UI'; color: #222; }
            QLineEdit { border: 1px solid #d0d0d0; padding: 6px; border-radius: 6px; }
            QPushButton { background: #e6e6e6; border: 1px solid #ccc; padding: 6px 10px; border-radius: 6px; }
            QPushButton:hover { background:#dedede; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # Top
        top = QHBoxLayout()
        self.search_input = QLineEdit(placeholderText="Buscar insumo por nombre, lote, registro sanitario...")
        self.search_input.textChanged.connect(self._on_search_changed)
        top.addWidget(self.search_input)

        self.btn_add = QPushButton("Agregar insumo", clicked=self._add_inline)
        top.addWidget(self.btn_add)

        self.btn_export = QPushButton("Exportar CSV ", clicked=self._export_csv_current)
        top.addWidget(self.btn_export)

        top.addStretch()
        root.addLayout(top)

        # Tabs
        self.tabs = QTabWidget()
        self._setup_tab("Medicamento")
        self._setup_tab("Dispositivo Médico")
        self._setup_tab("Biológico")
        root.addWidget(self.tabs)

        self._counters = {"Medicamento": 1, "Dispositivo Médico": 1, "Biológico": 1}

        init_db()
        self._load_from_db()

    def _load_from_db(self):
        for k in self.data:
            self.data[k].clear()
            self.cards[k].clear()

        for insumo in fetch_all():
            if insumo["tipo"] in self.data:
                self.data[insumo["tipo"]].append(insumo)

        for tipo in self.data:
            self._refresh_tab(tipo)

   

    def _setup_tab(self, tipo: str):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        scroll = QScrollArea(widgetResizable=True)
        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setSpacing(12)
        scroll.setWidget(container)

        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Lote / Modelo",
            "Caducidad / Fab", "Registro Sanitario", "Acción", "Eliminar"
        ])
        header = table.horizontalHeader()
        for col in range(table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        table.hide()

        layout.addWidget(scroll)
        layout.addWidget(table)

        page.scroll = scroll
        page.container = container
        page.grid = grid
        page.table = table

        self.tabs.addTab(page, tipo)



    def _on_search_changed(self, text: str):
        text = text.lower()
        idx = self.tabs.currentIndex()
        tipo = self.tabs.tabText(idx)

        for card in self.cards[tipo].values():
            d = card.property("data") or {}
            hay = any(text in str(d.get(k, "")).lower()
                      for k in ("nombre", "lote", "registro_sanitario", "modelo"))
            card.setVisible(hay)

        page = self.tabs.widget(idx)
        for row in range(page.table.rowCount()):
            visible = False
            for col in range(page.table.columnCount()):
                item = page.table.item(row, col)
                if item and text in item.text().lower():
                    visible = True
                    break
            page.table.setRowHidden(row, not visible)

  

    def _add_inline(self):
        tipo = self.tabs.tabText(self.tabs.currentIndex())
        uid = f"{tipo[:3].upper()}-{next_id(tipo):03d}"

        base = {
            "id": uid,
            "tipo": tipo,
            "nombre": f"{tipo} {uid}",
            "lote": "",
            "fecha_caducidad": "",
            "fecha_fabricacion": "",
            "registro_sanitario": "",
            "foto": None,
            "stock_actual": 0
        }

        insert(base)
        self.data[tipo].append(base)
        self._refresh_tab(tipo)

    def _edit_by_id(self, tipo: str, insumo_id: str):
        idx = next((i for i, it in enumerate(self.data[tipo]) if it["id"] == insumo_id), -1)
        if idx == -1:
            return

        dlg = InsumoDialog(self.data[tipo][idx], parent=self)
        if dlg.exec():
            nuevo = dlg.get_data()
            self.data[tipo][idx].update(nuevo)
            update(self.data[tipo][idx])

            if insumo_id in self.cards[tipo]:
                self.cards[tipo][insumo_id].update_visual(self.data[tipo][idx])

            self._refresh_tab(tipo)

    def _delete_by_id(self, tipo: str, insumo_id: str):
        idx = next((i for i, it in enumerate(self.data[tipo]) if it["id"] == insumo_id), -1)
        if idx == -1:
            return

        if QMessageBox.question(
            self, "Eliminar insumo",
            f"Eliminar '{self.data[tipo][idx].get('nombre','')}'?"
        ) != QMessageBox.StandardButton.Yes:
            return

        delete(insumo_id)
        self.data[tipo].pop(idx)

        if insumo_id in self.cards[tipo]:
            self.cards[tipo][insumo_id].deleteLater()
            self.cards[tipo].pop(insumo_id)

        self._refresh_tab(tipo)

   

    def _refresh_tab(self, tipo: Optional[str] = None):
        if tipo is None:
            tipo = self.tabs.tabText(self.tabs.currentIndex())

        idx = next(i for i in range(self.tabs.count()) if self.tabs.tabText(i) == tipo)
        page = self.tabs.widget(idx)

        while page.grid.count():
            item = page.grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        self.cards[tipo].clear()

        for i, it in enumerate(self.data[tipo]):
            card = InsumoCard(it, parent=page.container)
            self.cards[tipo][it["id"]] = card

            card.btn_edit.clicked.connect(partial(self._edit_by_id, tipo, it["id"]))
            card.btn_del.clicked.connect(partial(self._delete_by_id, tipo, it["id"]))
            card.btn_stock.clicked.connect(partial(self._open_stock, tipo, it["id"]))

            row, col = divmod(i, 3)
            page.grid.addWidget(card, row, col)

        tbl = page.table
        tbl.setRowCount(len(self.data[tipo]))

        for row, it in enumerate(self.data[tipo]):
            tbl.setItem(row, 0, QTableWidgetItem(it.get("id", "")))
            tbl.setItem(row, 1, QTableWidgetItem(it.get("nombre", "")))
            tbl.setItem(row, 2, QTableWidgetItem(it.get("tipo", "")))
            tbl.setItem(row, 3, QTableWidgetItem(it.get("lote") or it.get("modelo") or ""))
            tbl.setItem(row, 4, QTableWidgetItem(it.get("fecha_caducidad") or it.get("fecha_fabricacion") or ""))
            tbl.setItem(row, 5, QTableWidgetItem(it.get("registro_sanitario", "")))

            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(partial(self._edit_by_id, tipo, it["id"]))
            tbl.setCellWidget(row, 6, btn_edit)

            btn_del = QPushButton("Eliminar")
            btn_del.clicked.connect(partial(self._delete_by_id, tipo, it["id"]))
            tbl.setCellWidget(row, 7, btn_del)

   

    def _open_stock(self, tipo: str, insumo_id: str):
        insumo = next(i for i in self.data[tipo] if i["id"] == insumo_id)
        dlg = StockDialog(insumo, self)
        if dlg.exec():
            self._load_from_db()

   

    def _export_csv_current(self):
        tipo = self.tabs.tabText(self.tabs.currentIndex())
        path, _ = QFileDialog.getSaveFileName(self, f"Exportar {tipo} a CSV", "", "CSV (*.csv)")
        if not path:
            return

        rows = self.data[tipo]
        if not rows:
            QMessageBox.information(self, "Exportar CSV", "No hay datos para exportar.")
            return

        headers = list({k for r in rows for k in r.keys()})

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for r in rows:
                    writer.writerow([r.get(h, "") for h in headers])
            QMessageBox.information(self, "Exportar CSV", "Exportado correctamente.")
        except Exception as e:
            QMessageBox.warning(self, "Exportar CSV", f"Error exportando: {e}")
