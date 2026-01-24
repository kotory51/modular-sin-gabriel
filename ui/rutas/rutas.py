from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QFont, QColor, QPalette
from typing import List, Dict, Optional
import random


class LastMileHeader(QWidget):
    """Header superior con información del conductor y métricas"""
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._start_timer()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Fecha y estado
        date_frame = QFrame()
        date_layout = QVBoxLayout(date_frame)
        
        self.date_label = QLabel(QDateTime.currentDateTime().toString("yyyy-MM-dd"))
        self.date_label.setStyleSheet("font-size: 14px; color: #666;")
        
        self.status_label = QLabel("EN RUTA")
        self.status_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2E7D32;
            background-color: #E8F5E9;
            padding: 5px 15px;
            border-radius: 10px;
        """)
        
        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.status_label)
        
        # Métricas principales
        metrics_frame = QFrame()
        metrics_layout = QHBoxLayout(metrics_frame)
        metrics_layout.setSpacing(30)
        
        self.delivery_metric = self._create_metric_widget("22/129", "Entregas")
        self.time_metric = self._create_metric_widget("02:45", "Tiempo")
        self.distance_metric = self._create_metric_widget("18.2", "Kms")
        
        metrics_layout.addWidget(self.delivery_metric)
        metrics_layout.addWidget(self.time_metric)
        metrics_layout.addWidget(self.distance_metric)
        
        layout.addWidget(date_frame)
        layout.addStretch()
        layout.addWidget(metrics_frame)
    
    def _create_metric_widget(self, value: str, label: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1976D2;
        """)
        
        label_label = QLabel(label)
        label_label.setStyleSheet("font-size: 12px; color: #666;")
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return widget
    
    def _start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.start(60000)  # Actualizar cada minuto
    
    def _update_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm")
        self.time_metric.layout().itemAt(0).widget().setText(current_time)


class DriverInfoWidget(QGroupBox):
    """Widget de información del conductor y vehículo"""
    def __init__(self):
        super().__init__("Información de Ruta")
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Información del vehículo
        vehicle_layout = QHBoxLayout()
        
        self.plate_label = QLabel("JRU600 - BOGOTÁ")
        self.plate_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.vehicle_id = QLabel("ID: 3176")
        self.vehicle_id.setStyleSheet("color: #666;")
        
        vehicle_layout.addWidget(self.plate_label)
        vehicle_layout.addStretch()
        vehicle_layout.addWidget(self.vehicle_id)
        
        # Información del conductor
        self.driver_label = QLabel("JOSE ALEXANDER SANCHEZ RAMIREZ - MEDELLÍN")
        self.driver_label.setStyleSheet("font-size: 14px; color: #333;")
        
        # Barra de progreso
        progress_layout = QVBoxLayout()
        
        progress_header = QHBoxLayout()
        progress_label = QLabel("Progreso de Ruta:")
        self.percentage_label = QLabel("63.6%")
        self.percentage_label.setStyleSheet("font-weight: bold; color: #1976D2;")
        
        progress_header.addWidget(progress_label)
        progress_header.addStretch()
        progress_header.addWidget(self.percentage_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(64)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        
        progress_layout.addLayout(progress_header)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addLayout(vehicle_layout)
        layout.addWidget(self.driver_label)
        layout.addLayout(progress_layout)


class PerformanceMetrics(QWidget):
    """Widget de métricas de rendimiento"""
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QGridLayout(self)
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(10)
        
        # Crear métricas
        metrics = [
            ("Guías gestionadas", "7/11", "#2196F3"),
            ("Tiempo de ruta", "2:21 hrs", "#4CAF50"),
            ("Distancia recorrida", "16.3 kms", "#FF9800"),
            ("Tiempo sin actividad", "2 min", "#9C27B0"),
            ("Guías pendientes", "38.4%", "#F44336"),
            ("Ítems en vehículo", "41.2%", "#607D8B")
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            row = i // 3
            col = i % 3
            metric_widget = self._create_metric(label, value, color)
            layout.addWidget(metric_widget, row, col)
    
    def _create_metric(self, label: str, value: str, color: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {color};
        """)
        
        label_label = QLabel(label)
        label_label.setStyleSheet("font-size: 12px; color: #666;")
        label_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return widget


class DeliveryStatsWidget(QGroupBox):
    """Widget de estadísticas de entregas"""
    def __init__(self):
        super().__init__("Estadísticas de Entregas")
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Resumen
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("11 Asignadas")
        self.delivered_label = QLabel("85.7% Entregadas")
        self.partial_label = QLabel("0% Parciales")
        self.failed_label = QLabel("14.3% No entregadas")
        
        for label in [self.total_label, self.delivered_label, self.partial_label, self.failed_label]:
            label.setStyleSheet("font-size: 13px; padding: 5px;")
        
        self.delivered_label.setStyleSheet("font-size: 13px; color: #4CAF50; padding: 5px;")
        self.failed_label.setStyleSheet("font-size: 13px; color: #F44336; padding: 5px;")
        
        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.delivered_label)
        summary_layout.addWidget(self.partial_label)
        summary_layout.addWidget(self.failed_label)
        summary_layout.addStretch()
        
        # Barras de progreso
        bars_layout = QVBoxLayout()
        
        # Barra de entregas completadas
        delivered_bar = self._create_delivery_bar("Entregadas", 85.7, "#4CAF50")
        # Barra de entregas parciales
        partial_bar = self._create_delivery_bar("Parciales", 0, "#FF9800")
        # Barra de no entregadas
        failed_bar = self._create_delivery_bar("No entregadas", 14.3, "#F44336")
        
        bars_layout.addLayout(delivered_bar)
        bars_layout.addLayout(partial_bar)
        bars_layout.addLayout(failed_bar)
        
        layout.addLayout(summary_layout)
        layout.addLayout(bars_layout)
    
    def _create_delivery_bar(self, label: str, percentage: float, color: str) -> QHBoxLayout:
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setMinimumWidth(100)
        
        bar = QProgressBar()
        bar.setValue(int(percentage))
        bar.setTextVisible(False)
        bar.setMaximumHeight(10)
        bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f5f5f5;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)
        
        percentage_label = QLabel(f"{percentage}%")
        percentage_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        layout.addWidget(label_widget)
        layout.addWidget(bar)
        layout.addWidget(percentage_label)
        
        return layout


class RouteMapWidget(QGroupBox):
    """Widget de mapa simplificado con progreso de ruta"""
    def __init__(self):
        super().__init__("Ruta Activa")
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Información de la ruta
        route_info = QHBoxLayout()
        self.route_status = QLabel("Ruta activa: 13:40 (63.6%)")
        self.route_status.setStyleSheet("font-weight: bold; color: #1976D2;")
        
        route_info.addWidget(self.route_status)
        route_info.addStretch()
        
        # Mapa simplificado (simulado con labels)
        map_container = QWidget()
        map_layout = QVBoxLayout(map_container)
        
        # Zonas de la ruta (simuladas)
        zones = ["Poblado", "Castilla", "Laureles", "San Javier", "Villa Hermosa", 
                "Belén", "Aeropuerto", "Guayabal", "Comuna 13", "Itagüí"]
        
        for zone in zones:
            zone_label = QLabel(f"📍 {zone}")
            zone_label.setStyleSheet("padding: 5px;")
            map_layout.addWidget(zone_label)
        
        # Scroll area para las zonas
        scroll = QScrollArea()
        scroll.setWidget(map_container)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setStyleSheet("border: 1px solid #ddd; border-radius: 5px;")
        
        layout.addLayout(route_info)
        layout.addWidget(scroll)


class DeliveryListWidget(QGroupBox):
    """Lista de entregas pendientes"""
    delivery_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__("Entregas Pendientes")
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Tabla de entregas
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Referencia", "Cliente", "Dirección", "Estado"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Configurar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
    
    def load_deliveries(self, deliveries: List[Dict]):
        self.table.setRowCount(0)
        
        for delivery in deliveries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(delivery.get('reference', '')))
            self.table.setItem(row, 1, QTableWidgetItem(delivery.get('client', '')))
            self.table.setItem(row, 2, QTableWidgetItem(delivery.get('address', '')))
            
            status_item = QTableWidgetItem(delivery.get('status', 'Pendiente'))
            status = delivery.get('status', 'Pendiente')
            if status == 'Entregado':
                status_item.setForeground(QColor('#4CAF50'))
            elif status == 'En camino':
                status_item.setForeground(QColor('#2196F3'))
            elif status == 'Pendiente':
                status_item.setForeground(QColor('#FF9800'))
            elif status == 'Fallido':
                status_item.setForeground(QColor('#F44336'))
            
            self.table.setItem(row, 3, status_item)


class LastMileDashboard(QWidget):
    """Dashboard principal estilo LastMile Delivery"""
    
    delivery_completed = pyqtSignal(dict)
    route_changed = pyqtSignal(dict)
    
    def __init__(self, role: str = "driver", user_id: Optional[int] = None):
        super().__init__()
        self.role = role
        self.user_id = user_id
        
        # Datos de ejemplo
        self.deliveries = [
            {"reference": "R:1604 - E:1601", "client": "EMILSE DEL SOCORRO ARCILLA LONDONO", 
             "address": "Calle 123 #45-67", "status": "En camino"},
            {"reference": "R:1629 - E:1628", "client": "NATALIA NAVARRO CARDENO", 
             "address": "Carrera 89 #12-34", "status": "Pendiente"},
            {"reference": "R:1630 - E:1629", "client": "CARLOS ANDRES GOMEZ", 
             "address": "Avenida 56 #78-90", "status": "Pendiente"},
            {"reference": "R:1631 - E:1630", "client": "MARIA FERNANDA LOPEZ", 
             "address": "Calle 34 #56-78", "status": "Pendiente"}
        ]
        
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # Header
        self.header = LastMileHeader()
        main_layout.addWidget(self.header)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo (Información y métricas)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Información del conductor
        self.driver_info = DriverInfoWidget()
        left_layout.addWidget(self.driver_info)
        
        # Métricas de rendimiento
        self.metrics = PerformanceMetrics()
        left_layout.addWidget(self.metrics)
        
        # Estadísticas de entregas
        self.delivery_stats = DeliveryStatsWidget()
        left_layout.addWidget(self.delivery_stats)
        
        # Lista de entregas
        self.delivery_list = DeliveryListWidget()
        self.delivery_list.delivery_selected.connect(self._on_delivery_selected)
        left_layout.addWidget(self.delivery_list, 2)
        
        # Panel derecho (Mapa y controles)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Mapa de ruta
        self.route_map = RouteMapWidget()
        right_layout.addWidget(self.route_map, 3)
        
        # Controles de acción
        controls = self._create_action_controls()
        right_layout.addWidget(controls)
        
        # Configurar splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])
        
        main_layout.addWidget(splitter)
    
    def _create_action_controls(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Iniciar Ruta")
        self.complete_btn = QPushButton("✓ Marcar como Entregado")
        self.failed_btn = QPushButton("✗ Marcar como Fallido")
        self.pause_btn = QPushButton("⏸ Pausar Ruta")
        
        # Estilizar botones
        for btn in [self.start_btn, self.complete_btn, self.failed_btn, self.pause_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    border: 2px solid #1976D2;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E3F2FD;
                }
            """)
        
        self.complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #388E3C;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        
        self.failed_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: 2px solid #D32F2F;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        
        # Conectar señales
        self.start_btn.clicked.connect(self._start_route)
        self.complete_btn.clicked.connect(self._complete_delivery)
        self.failed_btn.clicked.connect(self._fail_delivery)
        self.pause_btn.clicked.connect(self._pause_route)
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.complete_btn)
        buttons_layout.addWidget(self.failed_btn)
        buttons_layout.addWidget(self.pause_btn)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def _load_data(self):
        """Cargar datos en los widgets"""
        self.delivery_list.load_deliveries(self.deliveries)
        
        # Actualizar estadísticas
        total = len(self.deliveries)
        delivered = len([d for d in self.deliveries if d['status'] == 'Entregado'])
        percentage = (delivered / total * 100) if total > 0 else 0
        
        self.delivery_stats.total_label.setText(f"{total} Asignadas")
        self.delivery_stats.delivered_label.setText(f"{percentage:.1f}% Entregadas")
        
        # Actualizar barra de progreso
        self.driver_info.progress_bar.setValue(int(percentage))
        self.driver_info.percentage_label.setText(f"{percentage:.1f}%")
    
    def _on_delivery_selected(self, delivery: Dict):
        """Manejar selección de entrega"""
        print(f"Entrega seleccionada: {delivery}")
    
    def _start_route(self):
        """Iniciar ruta"""
        self.header.status_label.setText("EN RUTA")
        self.header.status_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2E7D32;
            background-color: #E8F5E9;
            padding: 5px 15px;
            border-radius: 10px;
        """)
        QMessageBox.information(self, "Ruta Iniciada", "La ruta ha sido iniciada")
    
    def _complete_delivery(self):
        """Marcar entrega como completada"""
        selected = self.delivery_list.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.deliveries[row]['status'] = 'Entregado'
            self._load_data()
            self.delivery_completed.emit(self.deliveries[row])
    
    def _fail_delivery(self):
        """Marcar entrega como fallida"""
        selected = self.delivery_list.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.deliveries[row]['status'] = 'Fallido'
            self._load_data()
    
    def _pause_route(self):
        """Pausar ruta"""
        self.header.status_label.setText("PAUSADA")
        self.header.status_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #F57C00;
            background-color: #FFF3E0;
            padding: 5px 15px;
            border-radius: 10px;
        """)
        QMessageBox.information(self, "Ruta Pausada", "La ruta ha sido pausada")
    
    def set_role(self, role: str, user_id: Optional[int] = None):
        """Cambiar rol y actualizar vista"""
        self.role = role
        self.user_id = user_id
        
        if role == 'driver':
            # Mostrar controles específicos de conductor
            pass
        elif role == 'admin':
            # Mostrar controles administrativos
            pass


# Ejemplo de uso
if __name__ == "__main__":
    app = QApplication([])
    
    # Para modo conductor
    driver_dashboard = LastMileDashboard(role="driver", user_id=3176)
    driver_dashboard.setWindowTitle("LastMile Delivery - Panel de Conductor")
    driver_dashboard.resize(1400, 800)
    driver_dashboard.show()
    
    app.exec()