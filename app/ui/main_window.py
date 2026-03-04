"""
Dashboard principal con los 9 temas del libro Pumacayo.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QFrame, QLabel, QPushButton,
    QScrollArea, QGridLayout, QApplication
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QFont

from app.ui.widgets import ToolboxPanel, InspectorPanel
from app.graphics.scene import PowerGraphicsView
from app.ui.solver_panel import (
    SolverPerUnit, SolverInductancia, SolverCapacidad, SolverLineas,
    SolverConstantesABCD, SolverCirculares, SolverFlujoPotencia,
    SolverDespachoEconomico, SolverFallas
)
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Pantalla de Bienvenida / Selector de Módulos
# ─────────────────────────────────────────────────────────────────────────────
class WelcomeScreen(QWidget):
    def __init__(self, on_module_select, on_go_canvas):
        super().__init__()
        self.on_module_select = on_module_select
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header de bienvenida
        header = QFrame()
        header.setFixedHeight(160)
        header.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #020617,stop:1 #0f172a);")
        h_lay = QVBoxLayout(header)
        h_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("⚡ POWER ANALYZER PRO")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #38bdf8; font-size: 32px; font-weight: 900; letter-spacing: 4px;")
        sub = QLabel("Análisis de Sistemas de Potencia — Pumacayo & Romero")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color: #64748b; font-size: 14px; margin-top: 8px;")
        h_lay.addWidget(title); h_lay.addWidget(sub)
        layout.addWidget(header)

        # Grid de módulos
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #020617; }")
        content = QWidget(); content.setStyleSheet("background: #020617;")
        grid = QGridLayout(content); grid.setSpacing(15); grid.setContentsMargins(30, 30, 30, 30)

        modules = [
            ("1", "Valores por Unidad",        "Normalización de magnitudes. Base de todo el análisis.",     "#38bdf8", SolverPerUnit),
            ("2", "Inductancia de Líneas",      "Parámetros L, GMD, GMR. Reactancia inductiva.",             "#10b981", SolverInductancia),
            ("3", "Capacidad de Líneas",        "Parámetros C, susceptancia, potencia reactiva.",            "#f59e0b", SolverCapacidad),
            ("4", "Líneas de Transmisión",      "Modelos corta/media/larga. Regulación y pérdidas.",         "#8b5cf6", SolverLineas),
            ("5", "Constantes ABCD",            "Parámetros generalizados para análisis de redes.",          "#f472b6", SolverConstantesABCD),
            ("6", "Diagramas Circulares",       "Potencia máx. transferible. Centros y radios.",             "#fb923c", SolverCirculares),
            ("7", "Flujo de Potencia",          "Gauss-Seidel / Newton-Raphson. Convergencia iterativa.",    "#22d3ee", SolverFlujoPotencia),
            ("8", "Despacho Económico",         "Lambda iteration. Costo mínimo de operación.",              "#facc15", SolverDespachoEconomico),
            ("9", "Teoría de Fallas",           "Fallas 3φ, SLG, LL, DLG. Componentes simétricas.",        "#ef4444", SolverFallas),
        ]

        for idx, (num, name, desc, color, cls) in enumerate(modules):
            card = self._make_card(num, name, desc, color, cls)
            grid.addWidget(card, idx // 3, idx % 3)

        # Botón ir al canvas
        btn_canvas = QPushButton("🗺️  Ir al Diagrama Unifilar →")
        btn_canvas.setStyleSheet("""
            QPushButton { background: #1e293b; color: #38bdf8; border: 1px solid #334155;
            border-radius: 8px; padding: 15px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background: #334155; }
        """)
        btn_canvas.clicked.connect(on_go_canvas)
        grid.addWidget(btn_canvas, 3, 0, 1, 3)

        scroll.setWidget(content); layout.addWidget(scroll)

    def _make_card(self, num, name, desc, color, cls):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; }}
            QFrame:hover {{ border: 1px solid {color}; }}
        """)
        lay = QVBoxLayout(card); lay.setSpacing(8)
        badge = QLabel(f"TEMA {num}")
        badge.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 800; letter-spacing: 2px;")
        title = QLabel(name)
        title.setStyleSheet(f"color: #f8fafc; font-size: 15px; font-weight: 700;")
        title.setWordWrap(True)
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
        desc_lbl.setWordWrap(True)
        btn = QPushButton(f"🔬 ABRIR MÓDULO")
        btn.setStyleSheet(f"""
            QPushButton {{ background: {color}20; color: {color}; border: 1px solid {color}60;
            border-radius: 6px; padding: 8px; font-weight: bold; }}
            QPushButton:hover {{ background: {color}; color: #020617; }}
        """)
        btn.clicked.connect(lambda _, c=cls, n=name: self.on_module_select(c, n))
        lay.addWidget(badge); lay.addWidget(title); lay.addWidget(desc_lbl); lay.addWidget(btn)
        return card


# ─────────────────────────────────────────────────────────────────────────────
# Ventana Principal
# ─────────────────────────────────────────────────────────────────────────────
class PowerSystemPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ POWER ANALYZER PRO v10.0 | Pumacayo & Romero")
        self.setMinimumSize(1400, 900)
        self.setup_ui()
        self.apply_styles()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(30)

    def update_dots(self):
        from app.graphics.items import FlowDot
        for item in self.canvas_view.scene.items():
            if isinstance(item, FlowDot):
                item.advance_pos()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(0); self.main_layout.setContentsMargins(0,0,0,0)
        self.setCentralWidget(self.central_widget)

        # Header compacto
        self.header = self.create_header()
        self.main_layout.addWidget(self.header)

        # Tabs principales
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setDocumentMode(True)

        # ── Tab 0: Dashboard / Welcome ──
        self.canvas_view = PowerGraphicsView(self)
        self.welcome = WelcomeScreen(
            on_module_select=self.open_solver_module,
            on_go_canvas=lambda: self.tabs.setCurrentIndex(1)
        )
        self.tabs.addTab(self.welcome, "🏠 Inicio")

        # ── Tab 1: Canvas ──
        canvas_wrapper = QWidget()
        cw_layout = QHBoxLayout(canvas_wrapper); cw_layout.setSpacing(0); cw_layout.setContentsMargins(0,0,0,0)
        self.toolbox = ToolboxPanel(self); cw_layout.addWidget(self.toolbox)
        cw_layout.addWidget(self.canvas_view, stretch=2)
        self.inspector = InspectorPanel(self); cw_layout.addWidget(self.inspector)
        self.inspector.delete_btn.clicked.connect(self.canvas_view.delete_selected)
        self.tabs.addTab(canvas_wrapper, "🗺️  Diagrama Unifilar")

        # ── Tabs del 2 al 10: Solvers (se añaden dinámicamente al abrirlos) ──

        self.main_layout.addWidget(self.tabs, stretch=1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("⚡ Power Analyzer PRO | Basado en Pumacayo & Romero — Elige un módulo de análisis")

    def open_solver_module(self, solver_cls, name):
        """Abre (o activa si ya existe) un tab del solver."""
        # Buscar si ya está abierto
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == f"📐 {name}":
                self.tabs.setCurrentIndex(i); return
        widget = solver_cls()
        scroll = QScrollArea(); scroll.setWidget(widget); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #020617; }")
        idx = self.tabs.addTab(scroll, f"📐 {name}")
        self.tabs.setCurrentIndex(idx)
        self.status.showMessage(f"Módulo cargado: {name}", 3000)

    def create_header(self):
        header = QFrame(); header.setFixedHeight(65); header.setObjectName("Header")
        h_layout = QHBoxLayout(header)
        logo = QLabel("⚡ POWER ANALYZER"); logo.setObjectName("Logo"); h_layout.addWidget(logo)
        subtitle = QLabel("| Sistemas de Potencia — Pumacayo & Romero")
        subtitle.setStyleSheet("color: #334155; font-size: 12px;"); h_layout.addWidget(subtitle)
        h_layout.addStretch()

        self.btn_conn = QPushButton("🔗 CONECTAR")
        self.btn_conn.setObjectName("SecondAction"); self.btn_conn.setCheckable(True)
        self.btn_conn.clicked.connect(self.toggle_connection_mode); h_layout.addWidget(self.btn_conn)

        btn_demo = QPushButton("🧩 DEMO ESTRELLA")
        btn_demo.setObjectName("SecondAction"); btn_demo.clicked.connect(self.load_demo); h_layout.addWidget(btn_demo)

        sim_btn = QPushButton("🚀 EJECUTAR ANÁLISIS")
        sim_btn.setObjectName("PrimaryAction"); sim_btn.setFixedWidth(230)
        sim_btn.clicked.connect(self.start_simulation); h_layout.addWidget(sim_btn)
        return header

    def toggle_connection_mode(self):
        if self.btn_conn.isChecked():
            self.canvas_view.start_connection()
            self.status.showMessage("🖱️ MODO CONECTAR ACTIVO — Clic en primer equipo, luego en segundo.", 0)
            self.tabs.setCurrentIndex(1)
        else:
            self.canvas_view.cancel_connection()
            self.status.showMessage("Modo edición", 3000)

    def on_connection_finished(self):
        self.btn_conn.setChecked(False)
        self.status.showMessage("✅ Conexión establecida", 3000)

    def start_simulation(self):
        self.tabs.setCurrentIndex(1)
        self.status.showMessage("🚀 Simulando flujo de potencia...", 3000)
        from app.graphics.items import BaseEquipment
        for item in self.canvas_view.scene.items():
            if isinstance(item, BaseEquipment):
                v = 0.98 + np.random.random() * 0.05
                angle = (np.random.random() - 0.5) * 10
                item.value_label.setPlainText(f"{v:.3f} ∠ {angle:.1f}° pu")
                item.value_label.setDefaultTextColor(
                    QColor("#ef4444") if (v < 0.95 or v > 1.05) else QColor("#10b981"))

    def load_demo(self):
        self.tabs.setCurrentIndex(1)
        v = self.canvas_view; v.clear_diagram()
        central_bus = v.add_element("Bus"); central_bus.setPos(500, 400); central_bus.label.setPlainText("Barra-Central")
        gen = v.add_element("Gen"); gen.setPos(500, 200)
        trafo = v.add_element("Trafo"); trafo.setPos(800, 400)
        load = v.add_element("Load"); load.setPos(1000, 400)
        motor = v.add_element("Motor"); motor.setPos(200, 400)
        solar = v.add_element("Solar"); solar.setPos(500, 650)
        cap = v.add_element("Cap"); cap.setPos(700, 600)
        ground = v.add_element("Ground"); ground.setPos(500, 520)
        from app.graphics.items import SmartLine, FlowDot
        def qc(s, t):
            line = SmartLine(s, t); v.scene.addItem(line)
            s.connections.append(line); t.connections.append(line)
            for i in range(3):
                dot = FlowDot(line); dot.progress = i * 0.33
                v.scene.addItem(dot); line.dots.append(dot)
        qc(gen, central_bus); qc(central_bus, trafo); qc(trafo, load)
        qc(central_bus, motor); qc(solar, central_bus); qc(central_bus, cap); qc(ground, central_bus)
        self.status.showMessage("✅ Sistema en Estrella Cargado"); v.center_on_items()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #020617; }
            #Header { background-color: #0f172a; border-bottom: 2px solid #1e293b; }
            #Logo { color: #38bdf8; font-weight: 900; font-size: 20px; letter-spacing: 2px; }
            #PrimaryAction {
                background-color: #38bdf8; color: #020617; border-radius: 8px;
                font-weight: 800; padding: 10px; font-size: 13px;
            }
            #SecondAction {
                background-color: #1e293b; color: #f8fafc; border: 1px solid #334155;
                border-radius: 8px; font-weight: 600; padding: 8px 15px;
            }
            #SecondAction:checked { background-color: #38bdf8; color: #020617; }
            QTabWidget::pane { border: none; background: #020617; }
            QTabBar::tab {
                background: #0f172a; color: #64748b; padding: 10px 20px;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background: #1e293b; color: #38bdf8; border-bottom: 2px solid #38bdf8; }
            QTabBar::tab:hover { background: #1e293b; color: #f8fafc; }
            QStatusBar { background: #0f172a; color: #64748b; font-size: 11px; }
            QLabel { color: #f8fafc; }
            QLineEdit { background: #1e293b; color: #f8fafc; border: 1px solid #334155; padding: 6px; border-radius: 4px; }
            QTextEdit { background: #0f172a; color: #10b981; border: 1px solid #334155; }
        """)
