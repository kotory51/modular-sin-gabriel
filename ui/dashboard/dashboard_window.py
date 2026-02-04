from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton,
    QStackedWidget, QSizePolicy, QGridLayout, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QCursor, QPixmap

#from ui.widgets.sensor_card import SensorCard
from core.sensores.esp32_worker import ESP32Worker
from ui.devices.devices_window import DevicesPage
from ui.users.users_page import UsersPage
from ui.insumos.insumos_page import InsumosPage
from ui.rutas.vehiculos_page import VehiculosPage
from ui.historial.historial_page import HistorialPage

from ui.historial.historial_buffer import HistorialBuffer
from ui.widgets.grafica import RealtimeChart


class Dashboard(QWidget):
    def __init__(self, user_role: str, on_logout):
        super().__init__()

        self.user_role = user_role.lower()
        self.on_logout = on_logout

        self.menu_expanded_width = 240

        self.setWindowTitle("Monitoreo de Insumos")
        self.resize(1360, 820)
        self.setObjectName("root")

        self.apply_theme()

        
        self.registros_ok = 0
        self.registros_warn = 0
        self.registros_alert = 0

       
        self.worker = ESP32Worker()
        self.worker.data_received.connect(self.on_sensor_data)
        self.worker.start()

        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Botón menú
        btn_container = QFrame()
        btn_container.setFixedWidth(30)
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(5, 5, 5, 5)

        self.toggle_button = QPushButton("☰")
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_button.clicked.connect(self.toggle_menu)
        btn_layout.addWidget(self.toggle_button)
        btn_layout.addStretch()

       
        self.menu_container = QFrame()
        self.menu_container.setMaximumWidth(0)
        menu_layout = QHBoxLayout(self.menu_container)
        menu_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = self._build_sidebar()
        menu_layout.addWidget(self.sidebar)

      
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.page_dashboard = self._build_dashboard_page()
        self.page_historial = HistorialPage()

        self.stack.addWidget(self.page_dashboard)     # 0
        self.stack.addWidget(VehiculosPage())         # 1
        self.stack.addWidget(InsumosPage())           # 2
        self.stack.addWidget(DevicesPage(self.worker))# 3
        self.stack.addWidget(UsersPage())             # 4
        self.stack.addWidget(self.page_historial)     # 5
        self.stack.addWidget(QWidget())               # 6 

        main_layout.addWidget(btn_container)
        main_layout.addWidget(self.menu_container)
        main_layout.addWidget(self.stack, 1)

        
        self.menu_animation = QPropertyAnimation(self.menu_container, b"maximumWidth")
        self.menu_animation.setDuration(250)
        self.menu_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    
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

   
    def _build_sidebar(self):
        menu = QFrame()
        menu.setObjectName("sidebar")
        menu.setMinimumWidth(self.menu_expanded_width)

        layout = QVBoxLayout(menu)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        logo = QLabel()
        pixmap = QPixmap(r"C:\Users\kurof\OneDrive\Desktop\prueba\ui\widgets\img\logo.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        role_menu = {
            "administrador": [
                ("Dashboard", 0),
                ("Rutas y Transporte", 1),
                ("Insumos Médicos", 2),
                ("Dispositivos", 3),
                ("Usuarios", 4),
                ("Historial y Reportes", 5),
                ("Alertas y Notificaciones", 6),
            ],
            "supervisor": [
                ("Dashboard", 0),
                ("Rutas y Transporte", 1),
                ("Insumos Médicos", 2),
                ("Dispositivos", 3),
                ("Historial y Reportes", 5),
                ("Alertas y Notificaciones", 6),
            ],
            "chofer": [
                ("Dashboard", 0),
                ("Rutas y Transporte", 1),
                ("Alertas y Notificaciones", 6),
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

    
    def _build_kpi_card(self, title):
        card = QFrame()
        card.setFixedHeight(90)
        card.setStyleSheet("background:#dbe9ee; border-radius:18px;")

        v = QVBoxLayout(card)
        v.setContentsMargins(18, 12, 18, 12)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size:14px; font-weight:600;")

        lbl_value = QLabel("--")
        lbl_value.setStyleSheet("font-size:26px; font-weight:700;")

        v.addWidget(lbl_title)
        v.addWidget(lbl_value)

        return card, lbl_value

    
    def _build_status_panel(self):
        panel = QFrame()
        panel.setFixedWidth(260)
        panel.setStyleSheet("background:white; border-radius:20px;")

        v = QVBoxLayout(panel)
        v.setContentsMargins(18, 18, 18, 18)
        v.setSpacing(12)

        title = QLabel("Registros")
        title.setStyleSheet("font-size:22px; font-weight:700;")
        v.addWidget(title)

        def badge(color):
            b = QLabel()
            b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b.setFixedHeight(36)
            b.setStyleSheet(f"""
                background:{color};
                color:white;
                border-radius:18px;
                font-weight:600;
            """)
            return b

        self.badge_ok = badge("#1ecb4f")
        self.badge_warn = badge("#ff9800")
        self.badge_alert = badge("#f44336")

        v.addWidget(self.badge_ok)
        v.addWidget(self.badge_warn)
        v.addWidget(self.badge_alert)
        v.addStretch()

        self.actualizar_badges()
        return panel

    def actualizar_badges(self):
        self.badge_ok.setText(f"OK dentro de rango: {self.registros_ok}")
        self.badge_warn.setText(f"Advertencias: {self.registros_warn}")
        self.badge_alert.setText(f"Alertas críticas: {self.registros_alert}")

    
    def _build_dashboard_page(self):
        page = QFrame()
        main = QHBoxLayout(page)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(20)

        center = QVBoxLayout()
        center.setSpacing(20)

        self.kpi_cards = {}

        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(16)

        for i, title in enumerate(["Batería", "Luz", "Temp condensación"]):
            card, lbl = self._build_kpi_card(title)
            self.kpi_cards[title] = lbl
            kpi_grid.addWidget(card, 0, i)

        center.addLayout(kpi_grid)

        self.temp_chart = RealtimeChart("Temperatura", "°C")
        self.hum_chart = RealtimeChart("Humedad", "%")

        center.addWidget(self.temp_chart)
        center.addWidget(self.hum_chart)

        main.addLayout(center, 1)
        main.addWidget(self._build_status_panel())

        return page

    
    def evaluar_estado(self, valor, minimo, maximo, margen):
        if minimo <= valor <= maximo:
            return "ok"
        if (minimo - margen) <= valor <= (maximo + margen):
            return "warn"
        return "alert"

  
    def on_sensor_data(self, datos: dict):
        if "Bat" in datos:
            self.kpi_cards["Batería"].setText(f"{datos['Bat']:.2f} v")

        if "Luz" in datos:
            self.kpi_cards["Luz"].setText(f"{datos['Luz']} lx")

        if "Rocío" in datos:
            self.kpi_cards["Temp condensación"].setText(f"{datos['Rocío']:.1f} °C")

        estados = []

        if "T_Sonda" in datos:
            estado = self.evaluar_estado(datos["T_Sonda"], 2, 8, 1)
            self.temp_chart.update_value(datos["T_Sonda"])
            estados.append(estado)

            if estado == "alert":
                HistorialBuffer.agregar(
                    "temperatura", "alert",
                    f"Temperatura crítica: {datos['T_Sonda']:.2f} °C"
                )
            elif estado == "warn":
                HistorialBuffer.agregar(
                    "temperatura", "warn",
                    f"Temperatura cercana al límite: {datos['T_Sonda']:.2f} °C"
                )

        if "Hum" in datos:
            estado = self.evaluar_estado(datos["Hum"], 30, 70, 5)
            self.hum_chart.update_value(datos["Hum"])
            estados.append(estado)

            if estado == "alert":
                HistorialBuffer.agregar(
                    "humedad", "alert",
                    f"Humedad crítica: {datos['Hum']:.1f} %"
                )
            elif estado == "warn":
                HistorialBuffer.agregar(
                    "humedad", "warn",
                    f"Humedad cercana al límite: {datos['Hum']:.1f} %"
                )

        if not estados:
            return

        if "alert" in estados:
            self.registros_alert += 1
        elif "warn" in estados:
            self.registros_warn += 1
        else:
            self.registros_ok += 1

        self.actualizar_badges()
        self.page_historial.refrescar()

    
    def toggle_menu(self):
        end = self.menu_expanded_width if self.menu_container.maximumWidth() == 0 else 0
        self.menu_animation.setEndValue(end)
        self.menu_animation.start()

    def confirm_logout(self):
        msg = QMessageBox.question(self, "Cerrar sesión", "¿Deseas cerrar sesión?")
        if msg == QMessageBox.StandardButton.Yes:
            self._do_logout()

    def _do_logout(self):
        if self.worker.isRunning():
            self.worker.stop()
        if callable(self.on_logout):
            self.on_logout()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.confirm_logout()
        else:
            super().keyPressEvent(event)
