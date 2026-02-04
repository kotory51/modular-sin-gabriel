import time
import csv
from functools import partial

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QHeaderView
)
from PyQt6.QtCore import QTimer

from ui.devices.devices_card import TarjetaDispositivo
from ui.devices.devices_form import DispositivoDialog
from ui.devices.puertos import Puertos

UMBRAL_DESCONEXION = 10


class DevicesPage(QWidget):
    def __init__(self, esp32_worker=None, parent=None):
        super().__init__(parent)

        self.worker = esp32_worker
        self.devices: dict[str, dict] = {}
        self.cards = {}

        root = QVBoxLayout(self)

      
        barra = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar dispositivo…")
        self.search.textChanged.connect(self.filter_devices)
        barra.addWidget(self.search)

        self.btn_config = QPushButton("Agregar un dispositivo")
        self.btn_config.clicked.connect(self.configurar_esp32)
        barra.addWidget(self.btn_config)

        self.btn_view = QPushButton("Cambiar a Tabla")
        self.btn_view.clicked.connect(self.toggle_view)
        barra.addWidget(self.btn_view)

        self.btn_export = QPushButton("Exportar CSV")
        self.btn_export.clicked.connect(self.exportar_csv)
        barra.addWidget(self.btn_export)

        barra.addStretch()
        root.addLayout(barra)

       
        self.scroll = QScrollArea(widgetResizable=True)
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.scroll.setWidget(self.cards_container)
        root.addWidget(self.scroll)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Batería", "Temp", "Hum", "Luz",
            "Última señal", "Estado", "Editar", "Eliminar"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.hide()
        root.addWidget(self.table)

   
        if self.worker:
            self.worker.data_received.connect(self._on_esp32_data)
            self.worker.error.connect(self._on_esp32_error)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_vistas)
        self.timer.start(1000)

   
    def configurar_esp32(self):
        dlg = Puertos(self)
        if not dlg.exec() or not self.worker:
            return

        puerto, baudios = dlg.get_config()
        self.worker.reconectar(puerto, baudios)

    def _on_esp32_error(self, msg: str):
        QMessageBox.warning(self, "ESP32", msg)

    def _on_esp32_data(self, data: dict):
        dev_id = str(data.get("ID")).strip()
        if not dev_id:
            return

        now = time.time()

        if dev_id in self.devices:
            d = self.devices[dev_id]

            if (now - d.get("last_signal_ts", 0)) < UMBRAL_DESCONEXION:
                print(f"[ESP32] Dispositivo {dev_id} reconectando")
                d["active"] = True
        else:

            d = self.devices.setdefault(dev_id, {
                "id": dev_id,
                "name": f"Dispositivo {dev_id}",
                "active": True,
                "com": None,
                "baud": None,
                "last_signal_ts": now
            })

        if d["com"] is None and self.worker.serial.ser:
            d["com"] = self.worker.serial.ser.port
            d["baud"] = self.worker.serial.ser.baudrate

        if not d.get("active", True):
            return

        d.update({
            "battery": data.get("Bat"),
            "temp": data.get("T_Sonda"),
            "hum": data.get("Hum"),
            "luz": data.get("Luz"),
            "last_signal_ts": now
        })

 
    def actualizar_vistas(self):
        self._actualizar_tarjetas()
        self._actualizar_tabla()

    def _actualizar_tarjetas(self):
        for i, d in enumerate(self.devices.values()):
            dev_id = d["id"]

            if dev_id not in self.cards:
                card = TarjetaDispositivo(d)
                card.btn_toggle.clicked.connect(partial(self.toggle, dev_id))
                card.btn_edit.clicked.connect(partial(self.editar, dev_id))
                card.btn_del.clicked.connect(partial(self.eliminar, dev_id))
                self.cards[dev_id] = card
            else:
                card = self.cards[dev_id]

            card.actualizar_visual(d, self.texto_ultima_senal(d))
            self.cards_layout.addWidget(card, i // 3, i % 3)

    def _actualizar_tabla(self):
        self.table.setRowCount(len(self.devices))

        for row, d in enumerate(self.devices.values()):
            self.table.setItem(row, 0, QTableWidgetItem(d["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(d.get("name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(str(d.get("battery", "--"))))
            self.table.setItem(row, 3, QTableWidgetItem(str(d.get("temp", "--"))))
            self.table.setItem(row, 4, QTableWidgetItem(str(d.get("hum", "--"))))
            self.table.setItem(row, 5, QTableWidgetItem(str(d.get("luz", "--"))))
            self.table.setItem(row, 6, QTableWidgetItem(self.texto_ultima_senal(d)))
            self.table.setItem(
                row, 7,
                QTableWidgetItem("Activo" if d.get("active") else "Inactivo")
            )

            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(partial(self.editar, d["id"]))
            self.table.setCellWidget(row, 8, btn_edit)

            btn_del = QPushButton("Eliminar")
            btn_del.clicked.connect(partial(self.eliminar, d["id"]))
            self.table.setCellWidget(row, 9, btn_del)

    def texto_ultima_senal(self, d):
        ts = d.get("last_signal_ts")
        if not ts:
            return "Sin datos"

        delta = int(time.time() - ts)
        
        return "Conectado" if delta < UMBRAL_DESCONEXION else f"Hace {delta}s"

    def toggle_view(self):
        showing = self.scroll.isVisible()
        self.scroll.setVisible(not showing)
        self.table.setVisible(showing)

    def filter_devices(self, text):
        text = text.lower()
        for card in self.cards.values():
            card.setVisible(any(text in str(v).lower() for v in card.datos.values()))

    
    def agregar_dispositivo(self):
        dlg = DispositivoDialog(parent=self)
        if dlg.exec():
            d = dlg.get_datos()
            d["id"] = str(d["id"]).strip()
            d.setdefault("active", True)
            d["last_signal_ts"] = None
            self.devices[d["id"]] = d
            self.actualizar_vistas()

    def editar(self, dev_id):
        d = self.devices.get(dev_id)
        if not d:
            return

        dlg = DispositivoDialog(d, parent=self)
        if dlg.exec():
            d.update(dlg.get_datos())

    def eliminar(self, dev_id):
        self.devices.pop(dev_id, None)
        card = self.cards.pop(dev_id, None)
        if card:
            card.deleteLater()

    def toggle(self, dev_id):
        d = self.devices.get(dev_id)
        if d:
            d["active"] = not d["active"]

   
    def exportar_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar CSV", "", "CSV (*.csv)")
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Nombre", "Batería", "Temp", "Hum", "Luz"])
            for d in self.devices.values():
                writer.writerow([
                    d["id"], d.get("name"),
                    d.get("battery"), d.get("temp"),
                    d.get("hum"), d.get("luz")
                ])
