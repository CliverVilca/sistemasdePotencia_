from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QStatusBar, QFrame, QLabel, QPushButton)
from app.ui.widgets import ToolboxPanel, InspectorPanel
from app.graphics.scene import PowerGraphicsView

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
import numpy as np

class PowerSystemPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ POWER ANALYZER PRO v10.0 | Enterprise Edition")
        self.setMinimumSize(1400, 900)
        
        self.setup_ui()
        self.apply_styles()
        
        # Animacion Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(30)

    def update_dots(self):
        from app.graphics.items import FlowDot
        for item in self.canvas_view.scene.items():
            if isinstance(item, FlowDot):
                item.advance_pos()

    def setup_ui(self):
        # Componentes Principales
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Header
        self.header = self.create_header()
        self.main_layout.addWidget(self.header)

        # Work Area (Splitter logic via layouts)
        self.work_area = QHBoxLayout()
        
        # 1. Left Sidebar
        self.toolbox = ToolboxPanel(self)
        self.work_area.addWidget(self.toolbox)

        # 2. Main Canvas (Tabs)
        self.tabs = QTabWidget()
        self.canvas_view = PowerGraphicsView(self)
        self.tabs.addTab(self.canvas_view, "Diagrama Unifilar (Design)")
        self.tabs.addTab(QFrame(), "Análisis de Estabilidad")
        self.tabs.addTab(QFrame(), "Reportes Técnicos")
        self.work_area.addWidget(self.tabs, stretch=2)

        # 3. Right Sidebar
        self.inspector = InspectorPanel(self)
        self.work_area.addWidget(self.inspector)
        
        # Conectar Botón Eliminar
        self.inspector.delete_btn.clicked.connect(self.canvas_view.delete_selected)

        self.main_layout.addLayout(self.work_area)

        # Footer
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Motor de Cálculo Conectado | Base de Datos IEC Activa")

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(80)
        header.setObjectName("Header")
        h_layout = QHBoxLayout(header)
        
        logo = QLabel("POWER MASTER PRO")
        logo.setObjectName("Logo")
        h_layout.addWidget(logo)
        
        h_layout.addStretch()
        
        self.btn_conn = QPushButton("🔗 CONECTAR")
        self.btn_conn.setObjectName("SecondAction")
        self.btn_conn.setCheckable(True)
        self.btn_conn.clicked.connect(self.toggle_connection_mode)
        h_layout.addWidget(self.btn_conn)

        btn_demo = QPushButton("🧩 CARGAR DEMO 9-BUS")
        btn_demo.setObjectName("SecondAction")
        btn_demo.clicked.connect(self.load_demo)
        h_layout.addWidget(btn_demo)
        
        sim_btn = QPushButton("🚀 EJECUTAR ANÁLISIS")
        sim_btn.setObjectName("PrimaryAction")
        sim_btn.setFixedWidth(250)
        sim_btn.clicked.connect(self.start_simulation)
        h_layout.addWidget(sim_btn)
        
        return header

    def toggle_connection_mode(self):
        if self.btn_conn.isChecked():
            self.canvas_view.start_connection()
            self.status.showMessage("🖱️ MODO CONECTAR ACTIVO: Clic en el primer componente, luego en el segundo.", 0)
        else:
            self.canvas_view.cancel_connection()
            self.status.showMessage("Modo edición restaurado.", 3000)

    def on_connection_finished(self):
        """Callback from scene when connection is done"""
        self.btn_conn.setChecked(False)
        self.status.showMessage("✅ Conexión establecida", 3000)

    def start_simulation(self):
        self.status.showMessage("🚀 Analizando Flujo de Potencia (Newton-Raphson)...", 3000)
        # Randomize results and show them
        from app.graphics.items import BaseEquipment
        for item in self.canvas_view.scene.items():
            if isinstance(item, BaseEquipment):
                v = 0.98 + np.random.random() * 0.05
                angle = (np.random.random() - 0.5) * 10
                item.value_label.setPlainText(f"{v:.3f} ∠ {angle:.1f}° pu")
                # Cambiar color según voltaje
                if v < 0.95 or v > 1.05:
                    item.value_label.setDefaultTextColor(QColor("#ef4444"))
                else:
                    item.value_label.setDefaultTextColor(QColor("#10b981"))

    def load_demo(self):
        v = self.canvas_view
        v.clear_diagram()
        
        # 1. Nodo Central (Barra Principal)
        central_bus = v.add_element("Bus")
        central_bus.setPos(500, 400)
        central_bus.label.setPlainText("Barra-Central")
        
        # 2. Generación (Norte)
        gen = v.add_element("Gen")
        gen.setPos(500, 200)
        
        # 3. Transformador -> Carga (Este)
        trafo = v.add_element("Trafo")
        trafo.setPos(800, 400)
        load = v.add_element("Load")
        load.setPos(1000, 400)
        
        # 4. Motor (Oeste)
        motor = v.add_element("Motor")
        motor.setPos(200, 400)
        
        # 5. Energías Renovables (Sur)
        solar = v.add_element("Solar")
        solar.setPos(500, 650)
        
        # 6. Compensación y Tierra (Diagonal)
        cap = v.add_element("Cap")
        cap.setPos(700, 600)
        ground = v.add_element("Ground")
        ground.setPos(500, 520)
        
        # Función auxiliar de conexión con animación
        from app.graphics.items import SmartLine, FlowDot
        def quick_connect(s, t):
            line = SmartLine(s, t)
            v.scene.addItem(line)
            s.connections.append(line)
            t.connections.append(line)
            for i in range(3):
                dot = FlowDot(line)
                dot.progress = i * 0.33
                v.scene.addItem(dot)
                line.dots.append(dot)
        
        # Construir la Estrella (Radial)
        quick_connect(gen, central_bus)       # Fuente
        quick_connect(central_bus, trafo)     # Salida feeder
        quick_connect(trafo, load)            # Consumo industrial
        quick_connect(central_bus, motor)     # Demanda mecánica
        quick_connect(solar, central_bus)     # Inyección renovable
        quick_connect(central_bus, cap)       # Mejora FP
        quick_connect(ground, central_bus)    # Tierra de servicio
        
        self.status.showMessage("✅ Sistema en Estrella (Radial) Cargado")
        v.center_on_items()


    def apply_styles(self):
        # QSS Professional Theme
        self.setStyleSheet("""
            QMainWindow { background-color: #020617; }
            #Header { background-color: #0f172a; border-bottom: 2px solid #1e293b; }
            #Logo { color: #38bdf8; font-weight: 900; font-size: 24px; letter-spacing: 2px; }
            #PrimaryAction { 
                background-color: #38bdf8; color: #020617; border-radius: 8px; 
                font-weight: 800; padding: 12px; font-size: 14px;
            }
            #SecondAction {
                background-color: #1e293b; color: #f8fafc; border: 1px solid #334155;
                border-radius: 8px; font-weight: 600; padding: 8px 15px;
            }
            #SecondAction:checked {
                background-color: #38bdf8; color: #020617; border-color: #7dd3fc;
            }
            QTabWidget::pane { border: 1px solid #1e293b; background: #0f172a; }
            QTabBar::tab {
                background: #1e293b; color: #94a3b8; padding: 12px 30px;
                border-top-left-radius: 8px; border-top-right-radius: 8px;
            }
            QTabBar::tab:selected { background: #0f172a; color: #38bdf8; border-bottom: 2px solid #38bdf8; }
            QStatusBar { background: #0f172a; color: #64748b; font-size: 11px; }
        """)
