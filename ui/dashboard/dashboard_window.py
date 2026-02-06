from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton,
    QStackedWidget, QSizePolicy, QGridLayout, QLabel, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QCursor, QPixmap

from collections import deque
import datetime

from core.sensores.esp32_worker import ESP32Worker
from ui.IA.regresion import regresion_lineal
from database.devices_service import get_device_service
from ui.IA.regresion_service import RegressionService

from ui.widgets.grafica import RealtimeChart

from ui.devices.devices_window import DevicesPage
from ui.users.users_page import UsersPage
from ui.insumos.insumos_page import InsumosPage
from ui.rutas.vehiculos_page import VehiculosPage
from ui.historial.historial_page import HistorialPage
from ui.historial.historial_buffer import HistorialBuffer
from ui.IA.logica_difusa import evaluar_riesgo_difuso



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

        # ==========================
        # SERVICIO DE BASE DE DATOS
        # ==========================
        self.device_service = get_device_service()
        self.regresion_service = RegressionService()

        # ==========================
        # CONTADORES
        # ==========================
        self.registros_ok = 0
        self.registros_warn = 0
        self.registros_alert = 0

        # ==========================
        # BUFFER REGRESIÓN
        # ==========================
        self.temp_buffer = deque(maxlen=10)

        # ==========================
        # WORKER ESP32
        # ==========================
        self.worker = ESP32Worker()
        self.worker.data_received.connect(self.on_sensor_data)
        self.worker._running = True
        self.worker.start()

        # ==========================
        # LAYOUT BASE
        # ==========================
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

        # Menú lateral
        self.menu_container = QFrame()
        self.menu_container.setMaximumWidth(0)
        menu_layout = QHBoxLayout(self.menu_container)
        menu_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = self._build_sidebar()
        menu_layout.addWidget(self.sidebar)

        # Stack central
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.page_dashboard = self._build_dashboard_page()
        self.page_historial = HistorialPage()

        self.stack.addWidget(self.page_dashboard)      # 0
        self.stack.addWidget(VehiculosPage())          # 1
        self.stack.addWidget(InsumosPage())            # 2
        self.stack.addWidget(DevicesPage(self.worker)) # 3
        self.stack.addWidget(UsersPage())              # 4
        self.stack.addWidget(self.page_historial)      # 5
        self.stack.addWidget(QWidget())                # 6

        main_layout.addWidget(btn_container)
        main_layout.addWidget(self.menu_container)
        main_layout.addWidget(self.stack, 1)

        # Animación menú
        self.menu_animation = QPropertyAnimation(self.menu_container, b"maximumWidth")
        self.menu_animation.setDuration(250)
        self.menu_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    # ==========================
    # ESTILOS
    # ==========================
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

    # ==========================
    # SIDEBAR
    # ==========================
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

    # ==========================
    # KPI CARD
    # ==========================
    def _build_kpi_card(self, title):
        card = QFrame()
        card.setFixedHeight(65)
        card.setStyleSheet("background:#dbe9ee; border-radius:18px;")

        v = QVBoxLayout(card)
        v.setContentsMargins(18, 12, 18, 12)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size:12px; font-weight:600;")

        lbl_value = QLabel("--")
        lbl_value.setStyleSheet("font-size:13px; font-weight:700;")

        v.addWidget(lbl_title)
        v.addWidget(lbl_value)

        return card, lbl_value

    # ==========================
    # DASHBOARD PAGE
    # ==========================
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

        kpi_titles = [
            "ID", "Temp Ambiente", "Aceleracion",
            "Bateria", "Luz", "Temp condensacion"
        ]

        for i, title in enumerate(kpi_titles):
            card, lbl_value = self._build_kpi_card(title)
            self.kpi_cards[title] = lbl_value
            row, col = divmod(i, 3)
            kpi_grid.addWidget(card, row, col)

        center.addLayout(kpi_grid)

        # 🔥 SOLO GRÁFICAS (sin tarjeta intermedia)
        self.temp_chart = RealtimeChart("Temperatura", "°C")
        self.hum_chart = RealtimeChart("Humedad", "%")

        center.addWidget(self.temp_chart)
        center.addWidget(self.hum_chart)

        main.addLayout(center, 1)
        main.addWidget(self._build_status_panel())

        return page

    # ==========================
    # PANEL ESTADOS
    # ==========================
    def _build_status_panel(self):
        panel = QFrame()
        panel.setFixedWidth(300)
        panel.setStyleSheet("background:white; border-radius:20px;")

        v = QVBoxLayout(panel)
        v.setContentsMargins(15, 15, 15, 15)
        v.setSpacing(10)

        title = QLabel("Registros")
        title.setStyleSheet("font-size:22px; font-weight:700;")
        v.addWidget(title)

        self.badge_ok = QLabel()
        self.badge_warn = QLabel()
        self.badge_alert = QLabel()

        for b, c in [
            (self.badge_ok, "#1ecb4f"),
            (self.badge_warn, "#ff9800"),
            (self.badge_alert, "#f44336"),
        ]:
            b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b.setFixedHeight(32)
            b.setStyleSheet(f"""
                background:{c};
                color:white;
                border-radius:16px;
                font-weight:600;
            """)
            v.addWidget(b)

        v.addSpacing(12)

        # ==========================
        # ALERTAS RECIENTES
        # ==========================
        lbl_alertas = QLabel("Alertas recientes")
        lbl_alertas.setStyleSheet("font-weight:700; font-size:14px;")
        v.addWidget(lbl_alertas)

        self.alerts_container = QVBoxLayout()
        self.alerts_container.setAlignment(Qt.AlignmentFlag.AlignTop)

        content = QWidget()
        content.setLayout(self.alerts_container)

        self.alerts_scroll = QScrollArea()
        self.alerts_scroll.setWidgetResizable(True)
        self.alerts_scroll.setMinimumHeight(240)
        self.alerts_scroll.setWidget(content)

        v.addWidget(self.alerts_scroll, 1)

        self.actualizar_badges()
        return panel

    def _agregar_alerta_visual(self, texto, nivel):
        color = {"warn": "#ff9800", "alert": "#f44336"}.get(nivel, "#999")
        lbl = QLabel(texto)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color:{color}; font-size:12px; padding: 3px;")
        
        # Limitar a 20 alertas máximo
        count = self.alerts_container.count()
        if count >= 20:
            item = self.alerts_container.itemAt(count - 1)
            if item and item.widget():
                item.widget().deleteLater()
        
        self.alerts_container.insertWidget(0, lbl)

    def actualizar_badges(self):
        self.badge_ok.setText(f"OK dentro de rango: {self.registros_ok}")
        self.badge_warn.setText(f"Advertencias: {self.registros_warn}")
        self.badge_alert.setText(f"Alertas críticas: {self.registros_alert}")

    # ==========================
    # LÓGICA SENSOR
    # ==========================
    def evaluar_estado(self, valor, minimo, maximo, margen):
        if minimo <= valor <= maximo:
            return "ok"
        if (minimo - margen) <= valor <= (maximo + margen):
            return "warn"
        return "alert"

    def _format_safe(self, value, fmt=".2f", unit=""):
        if value is None:
            return "--"
        try:
            formatted = f"{value:{fmt}}"
            return f"{formatted} {unit}" if unit else formatted
        except Exception:
            return "--"

    def on_sensor_data(self, datos: dict):
        # GUARDAR EN BASE DE DATOS
        try:
            self.device_service.save_device_data(datos)
        except Exception as e:
            print(f"[ERROR BD] No se pudo guardar sensor data: {e}")
        
        estado = "ok"
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        if "ID" in datos:
            self.kpi_cards["ID"].setText(str(datos["ID"]))

        if "T_Sonda" in datos:
            t = datos["T_Sonda"]
            self.kpi_cards["Temp Ambiente"].setText(self._format_safe(t, ".2f", "°C"))
            self.temp_chart.update_value(t)

            self.temp_buffer.append(t)

            if len(self.temp_buffer) >= 5:
                y = list(self.temp_buffer)

                pendiente, r2 =regresion_lineal(y)

                riesgo, score = evaluar_riesgo_difuso(
                    pendiente=pendiente,
                    r2=r2,
                    valor_actual=t,
                    minimo=2,
                    maximo=8
                )

                trend = (
                    "Subiendo" if pendiente > 0.02 else
                    "Bajando" if pendiente < -0.02 else
                    "Estable"
                )

                risk = (
                    "Alto" if r2 > 0.5 else
                    "Medio" if r2 > 0.2 else
                    "Bajo"
                )

                prediction = pendiente * (len(y) + 5) + sum(y) / len(y)

                self.regresion_service.save_result({
                    "device_id": str(datos.get("ID")),
                    "sensor": "T_Sonda",
                    "window_size": len(y),
                    "slope": pendiente,
                    "r2": r2,
                    "prediction": prediction,
                    "trend": trend,
                    "risk_level": risk,
                    "timestamp": datetime.datetime.now().isoformat()
                })

                # Evaluar y notificar sólo si la lógica difusa devolvió un riesgo
                if riesgo and str(riesgo).lower() == "alto":
                    self._agregar_alerta_visual(
                        f"[Prevencion] Riesgo alto de aumento de temperatura: ({trend}) °C",
                        "alert"
                    )

                    regresion_lineal(list(self.temp_buffer))

                    estado = self.evaluar_estado(t, 2, 8, 1)
                    if estado == "alert":
                        alert_text = f"[{current_time}] Temperatura crítica: {t:.2f} °C"
                        self._agregar_alerta_visual(alert_text, "alert")
                        HistorialBuffer.agregar(
                            "Temperatura", "alert",
                            f"Temperatura crítica: {t:.2f} °C"
                        )
                    elif estado == "warn":
                        alert_text = f"[{current_time}] Temperatura fuera de rango: {t:.2f} °C"
                        self._agregar_alerta_visual(alert_text, "warn")
                        HistorialBuffer.agregar(
                            "Temperatura", "warn",
                            f"Temperatura fuera de rango: {t:.2f} °C"
                        )

        if "Hum" in datos:
            hum = datos["Hum"]
            self.hum_chart.update_value(hum)
            estado_hum = self.evaluar_estado(hum, 30, 70, 5)

            if estado_hum == "alert":
                alert_text = f"[{current_time}] Humedad crítica: {hum:.2f} %"
                self._agregar_alerta_visual(alert_text, "alert")
                HistorialBuffer.agregar(
                    "Humedad", "alert",
                    f"Humedad crítica: {hum:.2f} %"
                )
            elif estado_hum == "warn":
                alert_text = f"[{current_time}] Humedad fuera de rango: {hum:.2f} %"
                self._agregar_alerta_visual(alert_text, "warn")
                HistorialBuffer.agregar(
                    "Humedad", "warn",
                    f"Humedad fuera de rango: {hum:.2f} %"
                )
            
            # Actualizar estado general para contadores
            if estado_hum in ["alert", "warn"]:
                estado = estado_hum

        if "Aceleracion" in datos:
            self.kpi_cards["Aceleracion"].setText(self._format_safe(datos["Aceleracion"], ".2f", "m/s²"))

        if "Bat" in datos:
            self.kpi_cards["Bateria"].setText(self._format_safe(datos["Bat"], ".2f", "V"))

        if "Luz" in datos:
            self.kpi_cards["Luz"].setText(self._format_safe(datos["Luz"], ".0f", "lx"))

        if "Rocio" in datos:
            self.kpi_cards["Temp condensacion"].setText(self._format_safe(datos["Rocio"], ".2f", "°C"))

        # Actualizar contadores
        if estado == "alert":
            self.registros_alert += 1
        elif estado == "warn":
            self.registros_warn += 1
        else:
            self.registros_ok += 1

        self.actualizar_badges()
        self.page_historial.refrescar()

    # ==========================
    # CONTROL
    # ==========================
    def toggle_menu(self):
        end = self.menu_expanded_width if self.menu_container.maximumWidth() == 0 else 0
        self.menu_animation.setEndValue(end)
        self.menu_animation.start()

    def confirm_logout(self):
        if QMessageBox.question(self, "Cerrar sesión", "¿Deseas cerrar sesión?") == QMessageBox.StandardButton.Yes:
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