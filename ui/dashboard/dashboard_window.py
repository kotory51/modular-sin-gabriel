from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton,
    QStackedWidget, QSizePolicy, QGridLayout, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QCursor, QPixmap

from ui.widgets.sensor_card import SensorCard
from core.sensores.esp32_worker import ESP32Worker
from ui.devices.devices_window import DevicesPage
from ui.users.users_page import UsersPage
from ui.insumos.insumos_page import InsumosPage


class Dashboard(QWidget):
    def __init__(self, user_role: str, on_logout):
        super().__init__()
        self.user_role = user_role.lower()
        self.on_logout = on_logout

        self.menu_expanded_width = 240
        self.menu_collapsed_width = 0
        self.menu_pinned = False

        self.setWindowTitle("Monitoreo de Insumos")
        self.resize(1360, 820)
        self.setObjectName("root")

        self.apply_theme()

        # ESP32
        self.worker = ESP32Worker(puerto="COM8", baudios=115200)
        self.worker.data_received.connect(self.on_sensor_data)
        self.worker.start()

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # boton menu
        btn_container = QFrame()
        btn_container.setFixedWidth(40)
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(5, 5, 5, 5)

        self.toggle_button = QPushButton("☰")
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_button.clicked.connect(self.toggle_menu)
        btn_layout.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignTop)
        btn_layout.addStretch()

        # menu lateral
        self.menu_container = QFrame()
        self.menu_container.setFixedWidth(0)

        menu_layout = QHBoxLayout(self.menu_container)
        menu_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = self._build_sidebar()
        self.sidebar.setMinimumWidth(self.menu_expanded_width)
        menu_layout.addWidget(self.sidebar)

        # pila
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.page_dashboard = self._build_dashboard_page()
        self.page_devices = DevicesPage(esp32_worker=self.worker)

        self.stack.addWidget(self.page_dashboard)      # 0
        self.stack.addWidget(QWidget())                # 1 Rutas
        self.stack.addWidget(InsumosPage())            # 2 Insumos
        self.stack.addWidget(self.page_devices)        # 3 Dispositivos
        self.stack.addWidget(UsersPage())              # 4 Usuarios
        self.stack.addWidget(QWidget())                # 5 Historial
        self.stack.addWidget(QWidget())                # 6 Alertas

        main_layout.addWidget(btn_container)
        main_layout.addWidget(self.menu_container)
        main_layout.addWidget(self.stack, 1)

        # animacion
        self.menu_animation = QPropertyAnimation(self.menu_container, b"maximumWidth")
        self.menu_animation.setDuration(250)
        self.menu_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    # estilos
    def apply_theme(self):
        self.setStyleSheet("""
            QWidget#root { background: #f4f6fa; }
            QFrame#sidebar {
                background: white;
                border-top-right-radius: 16px;
                border-bottom-right-radius: 16px;
            }
            QPushButton[class="menuBtn"] {
                background: transparent;
                color: #222;
                padding: 10px 18px;
                font-size: 15px;
                text-align: left;
                border-radius: 8px;
            }
            QPushButton[class="menuBtn"]:hover {
                background: rgba(0,0,0,0.08);
            }
        """)

    # menu
    def _build_sidebar(self):
        menu = QFrame()
        menu.setObjectName("sidebar")
        layout = QVBoxLayout(menu)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # logo
        logo = QLabel()
        pixmap = QPixmap(r"C:\Users\kurof\OneDrive\Desktop\prueba\ui\widgets\img\logo.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # menu de rol
        role_menu = {
            "administrador": [
                ("Dashboard", 0),
                ("Rutas y Transporte", 1),
                ("Insumos Médicos", 2),
                ("Dispositivos", 3),
                ("Usuarios", 4),
                ("Historial & Reportes", 5),
                ("Alertas & Notificaciones", 6),
            ],
            "supervisor": [
                ("Dashboard", 0),
                ("Rutas y Transporte", 1),
                ("Insumos Médicos", 2),
                ("Dispositivos", 3),
                ("Historial & Reportes", 5),
                ("Alertas & Notificaciones", 6),
            ],
            "chofer": [
                ("Dashboard", 0),
                ("Rutas y Transporte", 1),
                ("Alertas & Notificaciones", 6),
            ],
        }

        for text, index in role_menu.get(self.user_role, []):
            btn = QPushButton(text)
            btn.setProperty("class", "menuBtn")
            btn.clicked.connect(lambda _, i=index: self.stack.setCurrentIndex(i))
            layout.addWidget(btn)

        layout.addStretch()

        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.setProperty("class", "menuBtn")
        btn_logout.clicked.connect(self.confirm_logout)
        layout.addWidget(btn_logout)

        return menu

    # dashboard
    def _build_dashboard_page(self):
        page = QFrame()
        g = QGridLayout(page)
        g.setContentsMargins(24, 24, 24, 24)
        g.setSpacing(20)

        self.cards = {
            "T_Amb": SensorCard("Temperatura Ambiente", "°C"),
            "T_Sonda": SensorCard("Temp. Sonda", "°C"),
            "Hum": SensorCard("Humedad", "%"),
            "Luz": SensorCard("Luz", "lx"),
            "Rocío": SensorCard("Punto de Condensación", "°C"),
            "Bat": SensorCard("Batería", "%"),
            "Acc": SensorCard("Aceleración", "g"),
        }

        for i, card in enumerate(self.cards.values()):
            g.addWidget(card, i // 4, i % 4)

        return page

    # menu
    def toggle_menu(self):
        end = self.menu_expanded_width if self.menu_container.maximumWidth() == 0 else 0
        self.menu_animation.setEndValue(end)
        self.menu_animation.start()

    # sensores
    def on_sensor_data(self, datos: dict):
        for k, v in datos.items():
            if k in self.cards:
                self.cards[k].update_value(v)

    # salir
    def confirm_logout(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Cerrar sesión")
        msg.setText("¿Deseas cerrar sesión?")
        msg.setIcon(QMessageBox.Icon.Question)

        yes = msg.addButton("Sí", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("No", QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        if msg.clickedButton() == yes:
            self._do_logout()

    def _do_logout(self):
        if self.worker.isRunning():
            self.worker.stop()
        if callable(self.on_logout):
            self.on_logout()

    # ESC
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.confirm_logout()
        else:
            super().keyPressEvent(event)
