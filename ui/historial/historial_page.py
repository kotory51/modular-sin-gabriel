from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QScrollArea, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtWidgets import QDateTimeEdit

from ui.historial.historial_buffer import HistorialBuffer
from database.devices_service import get_device_service
from datetime import datetime, timedelta


class HistorialPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.device_service = get_device_service()

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        title = QLabel("Historial de Dispositivos y Sensores")
        title.setStyleSheet("font-size:24px; font-weight:700;")
        root.addWidget(title)
        
        # Controles para seleccionar dispositivo y rango de fechas
        controles = QHBoxLayout()
        
        # Selector de dispositivo
        controles.addWidget(QLabel("Dispositivo:"))
        self.device_combo = QComboBox()
        self.device_combo.currentTextChanged.connect(self.on_device_changed)
        self.refrescar_dispositivos()
        controles.addWidget(self.device_combo)
        
        # Rango de fechas
        controles.addWidget(QLabel("Desde:"))
        self.start_datetime = QDateTimeEdit()
        self.start_datetime.setDateTime(
            QDateTime.currentDateTime().addDays(-7)
        )
        controles.addWidget(self.start_datetime)
        
        controles.addWidget(QLabel("Hasta:"))
        self.end_datetime = QDateTimeEdit()
        self.end_datetime.setDateTime(QDateTime.currentDateTime())
        controles.addWidget(self.end_datetime)
        
        # Botón para cargar
        self.btn_cargar = QPushButton("Cargar Historial")
        self.btn_cargar.clicked.connect(self.cargar_historial)
        controles.addWidget(self.btn_cargar)
        
        controles.addStretch()
        root.addLayout(controles)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setSpacing(20)

        scroll.setWidget(self.container)
        root.addWidget(scroll, 1)

        self.refrescar()
    
    def refrescar_dispositivos(self):
        """Recarga la lista de dispositivos disponibles"""
        try:
            device_ids = self.device_service.get_all_device_ids()
            self.device_combo.clear()
            self.device_combo.addItem("-- Todos --", None)
            for dev_id in device_ids:
                self.device_combo.addItem(dev_id, dev_id)
        except Exception as e:
            print(f"[ERROR] No se pudieron cargar dispositivos: {e}")
    
    def on_device_changed(self):
        """Se llama cuando cambia el dispositivo seleccionado"""
        pass
    
    def cargar_historial(self):
        """Carga el historial del dispositivo seleccionado en el rango de fechas"""
        device_id = self.device_combo.currentData()
        
        if not device_id:
            # Cargar datos de buffer en tiempo real
            self.refrescar()
            return
        
        start_dt = self.start_datetime.dateTime().toPyDateTime()
        end_dt = self.end_datetime.dateTime().toPyDateTime()
        
        try:
            history = self.device_service.get_data_range(
                device_id,
                start_dt.isoformat(),
                end_dt.isoformat()
            )
            
            self._mostrar_historial_datos(device_id, history)
        except Exception as e:
            print(f"[ERROR] No se pudieron cargar datos: {e}")
    
    def _mostrar_historial_datos(self, device_id: str, records: list):
        """Muestra los registros históricos en la UI"""
        # Limpiar
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not records:
            lbl = QLabel(f"No hay datos para {device_id} en el período seleccionado")
            lbl.setStyleSheet("font-size:14px; color:#666;")
            self.list_layout.addWidget(lbl)
            self.list_layout.addStretch()
            return
        
        # Agrupar por fecha
        by_date = {}
        for record in records:
            ts = record.get("timestamp", "")
            date = ts[:10] if ts else "Unknown"
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(record)
        
        # Mostrar por fecha
        for date in sorted(by_date.keys(), reverse=True):
            section = QFrame()
            section.setStyleSheet("background:white; border-radius:8px;")
            layout = QVBoxLayout(section)
            layout.setContentsMargins(12, 12, 12, 12)
            
            # Header con fecha
            header = QLabel(date)
            header.setStyleSheet("font-weight:600; font-size:14px;")
            layout.addWidget(header)
            
            # Registros de esa fecha
            for record in by_date[date]:
                record_text = (
                    f"⏰ {record.get('timestamp', '')}: "
                    f"Temp={record.get('temp_amb')}°C, "
                    f"Hum={record.get('humedad')}%, "
                    f"Luz={record.get('luz')}, "
                    f"Bat={record.get('bateria')}%"
                )
                lbl = QLabel(record_text)
                lbl.setStyleSheet("font-size:12px; color:#555;")
                layout.addWidget(lbl)
            
            self.list_layout.addWidget(section)
        
        self.list_layout.addStretch()

    def refrescar(self):
        """Recarga el historial del buffer en tiempo real"""
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        data = HistorialBuffer.obtener_por_sensor()

        if not data:
            lbl = QLabel("No hay advertencias ni alertas registradas.")
            lbl.setStyleSheet("font-size:14px; color:#666;")
            self.list_layout.addWidget(lbl)
            self.list_layout.addStretch()
            return

        for sensor, registros in data.items():
            self.list_layout.addWidget(self._build_sensor_section(sensor, registros))

        self.list_layout.addStretch()

    def _build_sensor_section(self, sensor, registros):
        section = QFrame()
        section.setStyleSheet("""
            background:white;
            border-radius:18px;
        """)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title = QLabel(sensor.upper())
        title.setStyleSheet("font-size:18px; font-weight:700;")
        layout.addWidget(title)

        for r in registros:
            layout.addWidget(
                self._build_item(
                    r["fecha"],
                    r["nivel"],
                    r["mensaje"]
                )
            )

        return section

    def _build_item(self, fecha, nivel, mensaje):
        card = QFrame()
        card.setStyleSheet("""
            background:#f4f6fa;
            border-radius:14px;
        """)
        card.setMinimumHeight(70)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)

        color = "#ff9800" if nivel == "warn" else "#f44336"
        icon = "🟠" if nivel == "warn" else "🔴"

        header = QLabel(f"{icon} {fecha}")
        header.setStyleSheet(f"""
            font-size:13px;
            font-weight:600;
            color:{color};
        """)

        body = QLabel(mensaje)
        body.setStyleSheet("font-size:13px;")
        body.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(body)

        return card
