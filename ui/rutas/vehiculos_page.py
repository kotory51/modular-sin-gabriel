from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QScrollArea,
    QGridLayout, QLineEdit, QMessageBox
)


from database.vehiculos_db import (
    init_db as init_vehiculos_db,
    fetch_vehiculos,
    insert_vehiculo,
    update_vehiculo,
    delete_vehiculo,
    next_vehiculo_id,
    set_estado_vehiculo
)

from database.ruta_db import (
    init_db as init_rutas_db,
    fetch_rutas,
    insert_ruta,
    update_ruta,
    delete_ruta,
    next_ruta_id,
    set_estado_ruta
)

from database.asignaciones_db import (
    init_db as init_asignaciones_db,
    fetch_asignaciones,
    insert_asignacion,
    finalizar_asignacion,
    next_asignacion_id,
    vehiculo_disponible,
    ruta_disponible,
    chofer_disponible
)


from ui.rutas.vehiculo_card import VehiculoCard
from ui.rutas.vehiculos_dialog import VehiculoDialog

from ui.rutas.ruta_card import RutaCard
from ui.rutas.ruta_dialog import RutaDialog

from ui.rutas.asignacion_card import AsignacionCard
from ui.rutas.asignacion_dialog import AsignacionDialog


class VehiculosPage(QWidget):

    def __init__(self):
        super().__init__()

        init_vehiculos_db()
        init_rutas_db()
        init_asignaciones_db()

        root = QVBoxLayout(self)
        root.setSpacing(10)

        # ===================== TOP BAR =====================
        top = QHBoxLayout()

        self.search = QLineEdit()
        self.search.textChanged.connect(self._apply_filter)
        top.addWidget(self.search)

        self.btn_action = QPushButton()
        self.btn_action.clicked.connect(self._on_action)
        top.addWidget(self.btn_action)

        root.addLayout(top)

        
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_tab_changed)
        root.addWidget(self.tabs)

        self._build_tab("Vehículos")
        self._build_tab("Rutas")
        self._build_tab("Asignaciones")

        self.refresh()
        self._on_tab_changed(0)

    
    def _build_tab(self, name):
        page = QWidget()
        lay = QVBoxLayout(page)

        scroll = QScrollArea(widgetResizable=True)
        cont = QWidget()
        grid = QGridLayout(cont)
        grid.setSpacing(12)
        grid.setContentsMargins(10, 10, 10, 10)

        scroll.setWidget(cont)
        lay.addWidget(scroll)

        page.grid = grid
        page.cards = []

        self.tabs.addTab(page, name)

  
    def refresh(self):
        self._load_vehiculos()
        self._load_rutas()
        self._load_asignaciones()

    
    def _load_vehiculos(self):
        self._clear_tab(0)

        for i, v in enumerate(fetch_vehiculos()):
            card = VehiculoCard(
                v,
                on_edit=self._edit_vehiculo,
                on_delete=self._delete_vehiculo
            )
            self._add_card(0, card, i)

    
    def _load_rutas(self):
        self._clear_tab(1)

        for i, r in enumerate(fetch_rutas()):
            card = RutaCard(
                r,
                on_edit=self._edit_ruta,
                on_delete=self._delete_ruta
            )
            self._add_card(1, card, i)

  
    def _load_asignaciones(self):
        self._clear_tab(2)

        for i, a in enumerate(fetch_asignaciones()):
            card = AsignacionCard(
                a,
                on_finish=self._finalizar_asignacion
            )
            self._add_card(2, card, i)

    
    def _clear_tab(self, idx):
        page = self.tabs.widget(idx)
        while page.grid.count():
            w = page.grid.takeAt(0).widget()
            if w:
                w.deleteLater()
        page.cards.clear()

    def _add_card(self, idx, card, i):
        page = self.tabs.widget(idx)
        page.cards.append(card)
        r, c = divmod(i, 3)  
        page.grid.addWidget(card, r, c)

   
    def _apply_filter(self, text):
        page = self.tabs.currentWidget()
        text = text.lower()

        for card in page.cards:
            card.setVisible(
                any(text in str(v).lower() for v in card.data.values())
            )

    
    def _on_tab_changed(self, idx):
        name = self.tabs.tabText(idx)
        self.search.clear()

        if name == "Vehículos":
            self.search.setPlaceholderText("Buscar vehículos")
            self.btn_action.setText("Agregar vehículo")

        elif name == "Rutas":
            self.search.setPlaceholderText("Buscar rutas")
            self.btn_action.setText("Crear ruta")

        else:
            self.search.setPlaceholderText("Buscar asignaciones")
            self.btn_action.setText("Crear asignación")

  
    def _on_action(self):
        tab = self.tabs.tabText(self.tabs.currentIndex())

        if tab == "Vehículos":
            self._add_vehiculo()
        elif tab == "Rutas":
            self._add_ruta()
        else:
            self._add_asignacion()

    
    def _add_vehiculo(self):
        dlg = VehiculoDialog(parent=self)
        if dlg.exec():
            data = dlg.get_data()
            data["id"] = next_vehiculo_id()
            insert_vehiculo(data)
            self.refresh()

    def _edit_vehiculo(self, data):
        if data["estado"] == "En ruta":
            QMessageBox.warning(
                self,
                "Vehículo en ruta",
                "No se puede editar un vehículo que está en ruta"
            )
            return

        dlg = VehiculoDialog(data, self)
        if dlg.exec():
            update_vehiculo(dlg.get_data())
            self.refresh()

    def _delete_vehiculo(self, data):
        if data["estado"] == "En ruta":
            QMessageBox.warning(
                self,
                "Vehículo en ruta",
                "No se puede eliminar un vehículo en ruta"
            )
            return

        delete_vehiculo(data["id"])
        self.refresh()

   
    def _add_ruta(self):
        dlg = RutaDialog(parent=self)
        if dlg.exec():
            data = dlg.get_data()
            data["id"] = next_ruta_id()
            insert_ruta(data)
            self.refresh()

    def _edit_ruta(self, data):
        if data["estado"] == "Activa":
            QMessageBox.warning(
                self,
                "Ruta activa",
                "No se puede editar una ruta activa"
            )
            return

        dlg = RutaDialog(data, self)
        if dlg.exec():
            new = dlg.get_data()
            new["id"] = data["id"]
            update_ruta(new)
            self.refresh()

    def _delete_ruta(self, data):
        if data["estado"] == "Activa":
            QMessageBox.warning(
                self,
                "Ruta activa",
                "No se puede eliminar una ruta activa"
            )
            return

        delete_ruta(data["id"])
        self.refresh()

    
    def _add_asignacion(self):
        dlg = AsignacionDialog(self)
        if not dlg.exec():
            return

        data = dlg.get_data()

        if not vehiculo_disponible(data["vehiculo_id"]):
            QMessageBox.warning(self, "Error", "Vehículo ocupado")
            return

        if not ruta_disponible(data["ruta_id"]):
            QMessageBox.warning(self, "Error", "Ruta ocupada")
            return

        if not chofer_disponible(data["chofer_id"]):
            QMessageBox.warning(self, "Error", "Chofer ocupado")
            return

        data["id"] = next_asignacion_id()
        data["estado"] = "Activa"

        insert_asignacion(data)

        set_estado_vehiculo(data["vehiculo_id"], "En ruta")
        set_estado_ruta(data["ruta_id"], "Activa")

        self.refresh()

    def _finalizar_asignacion(self, data):
        finalizar_asignacion(data["id"])

        set_estado_vehiculo(data["vehiculo_id"], "Disponible")
        set_estado_ruta(data["ruta_id"], "Finalizada")

        self.refresh()
