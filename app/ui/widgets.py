from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QFormLayout, QLineEdit
from PyQt6.QtCore import Qt

class ToolboxPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setObjectName("Toolbox")
        self.setStyleSheet("background-color: #0f172a; border-right: 1px solid #1e293b;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("EQUIPOS IEEE", styleSheet="color: #64748b; font-weight: 800; font-size: 11px;"))
        
        comp_types = [
            ("Generador G", "Gen"), ("Transformador T", "Trafo"), 
            ("Barra B", "Bus"), ("Carga L", "Load"),
            ("Motor M", "Motor"), ("Capacitor C", "Cap"),
            ("Interruptor", "Breaker"), ("Reactor R", "Reactor"),
            ("Panel Solar", "Solar"), ("Aerogenerador", "Wind"),
            ("Seccionador", "Switch"), ("Puesta a Tierra", "Ground")
        ]
        for label, type_name in comp_types:
            btn = QPushButton(f"✚ {label}")
            btn.setStyleSheet("""
                QPushButton { 
                    background: #1e293b; color: #cbd5e1; border: 1px solid #334155; 
                    text-align: left; padding: 10px; border-radius: 6px; 
                    font-size: 12px; margin-bottom: 2px;
                }
                QPushButton:hover { background: #334155; border-color: #38bdf8; color: white; }
                QPushButton:pressed { background: #0f172a; }
            """)
            btn.clicked.connect(lambda ch, t=type_name: self.window().canvas_view.add_element(t))
            layout.addWidget(btn)
        layout.addStretch()

class InspectorPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setObjectName("Inspector")
        self.setStyleSheet("background-color: #0f172a; border-left: 1px solid #1e293b;")
        
        layout = QVBoxLayout(self)
        self.title = QLabel("INSPECTOR DE EQUIPO")
        self.title.setStyleSheet("color: #38bdf8; font-weight: 800; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(self.title)
        
        self.form = QFormLayout()
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.name_edit = QLineEdit()
        self.type_label = QLabel("None")
        self.v_edit = QLineEdit()
        self.p_edit = QLineEdit()
        
        style = "background: #1e293b; color: #f8fafc; border: 1px solid #334155; padding: 5px; border-radius: 4px;"
        for e in [self.name_edit, self.v_edit, self.p_edit]: e.setStyleSheet(style)
        self.type_label.setStyleSheet("color: #94a3b8; font-weight: bold;")

        self.form.addRow(self.create_label("Tipo:"), self.type_label)
        self.form.addRow(self.create_label("ID:"), self.name_edit)
        self.form.addRow(self.create_label("Voltaje (pu):"), self.v_edit)
        self.form.addRow(self.create_label("Potencia:"), self.p_edit)
        
        layout.addLayout(self.form)
        
        self.delete_btn = QPushButton("🗑️ ELIMINAR")
        self.delete_btn.setStyleSheet("""
            QPushButton { 
                background: #450a0a; color: #f87171; border: 1px solid #7f1d1d; 
                padding: 10px; border-radius: 6px; font-weight: bold; margin-top: 20px;
            }
            QPushButton:hover { background: #7f1d1d; color: white; }
        """)
        layout.addWidget(self.delete_btn)
        
        layout.addStretch()

    def create_label(self, text):
        l = QLabel(text)
        l.setStyleSheet("color: #64748b; font-size: 11px;")
        return l

    def update_from_item(self, item):
        if not item: return
        self.type_label.setText(item.type)
        
        # Desconectar señales previas para evitar duplicados
        try: self.name_edit.textChanged.disconnect()
        except: pass
        
        self.name_edit.setText(item.label.toPlainText())
        self.v_edit.setText(item.value_label.toPlainText())
        
        # Vincular cambio de nombre
        self.name_edit.textChanged.connect(lambda t: item.label.setPlainText(t))
