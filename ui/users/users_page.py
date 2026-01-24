from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QScrollArea, QGridLayout, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from functools import partial
import csv
import requests
from datetime import datetime

from ui.users.users_card import UserCard
from ui.users.users_form import UserDialog

from database.users_db import (
    init_db, fetch_all_users,
    insert_user, update_user, delete_user,
    get_next_user_id
)

API_URL = "http://192.168.1.68:8000"


class UsersPage(QWidget):

    def __init__(self, current_role="Administrador", parent=None):
        super().__init__(parent)
        self.current_role = current_role

        init_db()
        self.users = fetch_all_users()

        self.user_cards = {}
        self._next_id = get_next_user_id()

        layout = QVBoxLayout(self)

        if self.current_role.lower() != "administrador":
            lbl = QLabel("Acceso denegado.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)
            return

    
        top = QHBoxLayout()

        self.search_input = QLineEdit(placeholderText="Buscar usuario…")
        self.search_input.textChanged.connect(self.filter_users)
        top.addWidget(self.search_input)

        self.btn_add = QPushButton("Agregar usuario")
        self.btn_add.clicked.connect(self.add_user)
        top.addWidget(self.btn_add)

        self.btn_sync = QPushButton("Sincronizar")
        self.btn_sync.clicked.connect(self.sync_all_users)
        top.addWidget(self.btn_sync)

        self.btn_export = QPushButton("Exportar CSV")
        self.btn_export.clicked.connect(self.export_csv)
        top.addWidget(self.btn_export)

        top.addStretch()
        layout.addLayout(top)

        self.scroll = QScrollArea(widgetResizable=True)
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.scroll.setWidget(self.cards_container)
        layout.addWidget(self.scroll)

        self.actualizar_vistas()

    # CRUD 

    def add_user(self):
        uid = f"USR-{self._next_id:03d}"
        self._next_id += 1

        base = {
            "id": uid,
            "nombre": "",
            "apellido": "",
            "usuario": uid.lower(),
            "telefono": "",
            "email": "",
            "rol": "Chofer",
            "rfc": "",
            "tipo_sangre": "",
            "alergias": "",
            "enfermedades": "",
            "notas_medicas": "",
            "apto_operar": 0,
            "foto": None,
            "ine": None,
            "licencia": None,
            "licencia_num": "",
            "licencia_exp": "",
            "estado_documentos": "Pendiente",
            "synced": 0,
            "last_sync": None
        }

        dlg = UserDialog(base, self)
        if dlg.exec():
            user = dlg.get_data()
            user["synced"] = 0
            user["last_sync"] = None

            insert_user(user)
            self.users.append(user)
            self.actualizar_vistas()

    def edit_user_by_id(self, uid):
        for i, u in enumerate(self.users):
            if u["id"] == uid:
                dlg = UserDialog(u, self)
                if dlg.exec():
                    updated = dlg.get_data()
                    updated["synced"] = 0
                    updated["last_sync"] = None
                    self.users[i].update(updated)
                    update_user(self.users[i])
                    self.actualizar_vistas()
                return

    def delete_user_by_id(self, uid):
        if QMessageBox.question(
            self, "Eliminar", "¿Eliminar usuario?"
        ) != QMessageBox.StandardButton.Yes:
            return

        delete_user(uid)
        self.users = [u for u in self.users if u["id"] != uid]
        self.actualizar_vistas()

    # UI

    def actualizar_vistas(self):
        for c in self.user_cards.values():
            c.deleteLater()
        self.user_cards.clear()

        for i, u in enumerate(self.users):
            card = UserCard(u, self)
            card.btn_edit.clicked.connect(
                partial(self.edit_user_by_id, u["id"])
            )
            card.btn_del.clicked.connect(
                partial(self.delete_user_by_id, u["id"])
            )
            self.cards_layout.addWidget(card, i // 3, i % 3)
            self.user_cards[u["id"]] = card

    def filter_users(self, text):
        text = text.lower()
        for card in self.user_cards.values():
            data = card.property("data") or {}
            full = " ".join(str(v) for v in data.values()).lower()
            card.setVisible(text in full)

    # Sincronización

    def sync_user(self, user: dict) -> bool:
        try:
            r = requests.post(
                f"{API_URL}/users/sync",
                json=user,
                timeout=5
            )
            return r.status_code == 200
        except Exception as e:
            print("Sync error:", e)
            return False

    def sync_all_users(self):
        enviados = 0

        for u in self.users:
            if u["synced"]:
                continue

            if self.sync_user(u):
                u["synced"] = 1
                u["last_sync"] = datetime.now().isoformat()
                update_user(u)
                enviados += 1

        QMessageBox.information(
            self,
            "Sincronización",
            f"{enviados} usuarios sincronizados."
        )

        self.actualizar_vistas()

    # Exportar CSV

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV", "", "CSV (*.csv)"
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Nombre", "Usuario", "Rol", "RFC", "Estado"
            ])
            for u in self.users:
                writer.writerow([
                    u["id"],
                    u["nombre"],
                    u["usuario"],
                    u["rol"],
                    u["rfc"],
                    "OK" if u["synced"] else "Pendiente"
                ])

        QMessageBox.information(self, "CSV", "Exportado correctamente")
