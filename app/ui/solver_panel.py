"""
Panel de Solución por Temas - Basado en el libro:
"Análisis de Sistemas de Potencia - Teoría y Problemas Resueltos"
de Rafael Pumacayo C. y Rubén Romero L.

Cada módulo incluye:
  - Diagrama visual único del esquema eléctrico del tema
  - Formulario de parámetros de entrada
  - Solución paso a paso alrededor de las fórmulas del libro
"""
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QFormLayout, QFrame, QScrollArea, QTextEdit,
    QComboBox, QGroupBox, QGridLayout, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.ui.diagram_views import (
    DiagramPerUnit, DiagramInductancia, DiagramCapacidad, DiagramLineas,
    DiagramABCD, DiagramCirculares, DiagramFlujoPotencia, DiagramDespacho, DiagramFallas
)


def styled_label(text, color="#94a3b8", bold=False, size=12):
    lbl = QLabel(text)
    w = "800" if bold else "400"
    lbl.setStyleSheet(f"color: {color}; font-size: {size}px; font-weight: {w};")
    lbl.setWordWrap(True)
    return lbl

def field_style():
    return "background: #1e293b; color: #f8fafc; border: 1px solid #334155; padding: 6px; border-radius: 4px; font-family: Consolas;"

def section_box(title):
    box = QGroupBox(title)
    box.setStyleSheet("""
        QGroupBox { 
            color: #38bdf8; font-weight: bold; font-size: 13px;
            border: 1px solid #334155; border-radius: 8px; margin-top: 10px; padding-top: 10px;
        }
        QGroupBox::title { subcontrol-origin: margin; padding: 0 5px; }
    """)
    return box

def calc_btn(label="⚡ CALCULAR", color="#38bdf8"):
    btn = QPushButton(label)
    btn.setStyleSheet(
        f"background:{color}; color:{'#020617' if color=='#38bdf8' else '#fff'}; "
        f"font-weight:bold; padding:10px; border-radius:6px; font-size:13px;"
    )
    return btn

def result_box():
    r = QTextEdit(); r.setReadOnly(True)
    r.setStyleSheet("background:#0f172a; color:#10b981; font-family:Consolas; font-size:12px; border:1px solid #334155; border-radius:4px;")
    r.setMinimumHeight(220)
    return r

def build_two_panel(left_widget, right_widget):
    """Construye un layout de dos paneles horizontales (izq: diagrama+entradas, der: solución)."""
    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(left_widget)
    splitter.addWidget(right_widget)
    splitter.setSizes([400, 400])
    splitter.setStyleSheet("QSplitter::handle { background: #334155; width: 3px; }")
    return splitter


# ─────────────────────────────────────────────────────────────────────────────
# Tema 1 – Valores por Unidad
# ─────────────────────────────────────────────────────────────────────────────
class SolverPerUnit(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #020617;")
        main = QVBoxLayout(self); main.setSpacing(8); main.setContentsMargins(10,10,10,10)
        main.addWidget(styled_label("TEMA 1 · VALORES POR UNIDAD (Per-Unit System)", "#38bdf8", True, 15))

        # — Diagrama único del tema —
        main.addWidget(DiagramPerUnit())

        # — Panel izquierdo: entradas —
        left = QWidget(); left.setStyleSheet("background:#020617;")
        llay = QVBoxLayout(left); llay.setSpacing(6)

        box1 = section_box("Convertir valor real → p.u.")
        f1 = QFormLayout()
        self.v_real = QLineEdit("115"); self.v_real.setStyleSheet(field_style())
        self.v_base = QLineEdit("115"); self.v_base.setStyleSheet(field_style())
        self.s_real = QLineEdit("50");  self.s_real.setStyleSheet(field_style())
        self.s_base = QLineEdit("100"); self.s_base.setStyleSheet(field_style())
        self.z_real = QLineEdit("10");  self.z_real.setStyleSheet(field_style())
        for lbl, w in [("V_real (kV):", self.v_real), ("V_base (kV):", self.v_base),
                       ("S_real (MVA):", self.s_real), ("S_base (MVA):", self.s_base), ("Z_real (Ω):", self.z_real)]:
            f1.addRow(styled_label(lbl, "#94a3b8", size=11), w)
        box1.setLayout(f1); llay.addWidget(box1)

        box2 = section_box("Cambio de Base")
        f2 = QFormLayout()
        self.zpu_old = QLineEdit("0.1"); self.zpu_old.setStyleSheet(field_style())
        self.sb_old  = QLineEdit("100"); self.sb_old.setStyleSheet(field_style())
        self.vb_old  = QLineEdit("115"); self.vb_old.setStyleSheet(field_style())
        self.sb_new  = QLineEdit("200"); self.sb_new.setStyleSheet(field_style())
        self.vb_new  = QLineEdit("115"); self.vb_new.setStyleSheet(field_style())
        for lbl, w in [("Zpu viejo:", self.zpu_old), ("S_base_viejo (MVA):", self.sb_old),
                       ("V_base_viejo (kV):", self.vb_old), ("S_base_nuevo (MVA):", self.sb_new),
                       ("V_base_nuevo (kV):", self.vb_new)]:
            f2.addRow(styled_label(lbl, "#94a3b8", size=11), w)
        box2.setLayout(f2); llay.addWidget(box2)

        btn = calc_btn(); btn.clicked.connect(self.calcular); llay.addWidget(btn)

        # — Panel derecho: resultados —
        right = QWidget(); right.setStyleSheet("background:#020617;")
        rlay = QVBoxLayout(right)
        rlay.addWidget(styled_label("📐 SOLUCIÓN PASO A PASO", "#f59e0b", True, 12))
        self.result = result_box(); rlay.addWidget(self.result)

        main.addWidget(build_two_panel(left, right), stretch=1)

    def calcular(self):
        try:
            Vr=float(self.v_real.text()); Vb=float(self.v_base.text())
            Sr=float(self.s_real.text()); Sb=float(self.s_base.text()); Zr=float(self.z_real.text())
            Zpu_old=float(self.zpu_old.text()); Sb_old=float(self.sb_old.text())
            Vb_old=float(self.vb_old.text()); Sb_new=float(self.sb_new.text()); Vb_new=float(self.vb_new.text())
            Vpu=Vr/Vb; Spu=Sr/Sb; Zbase=(Vb*1000)**2/(Sb*1e6); Zpu=Zr/Zbase
            Zpu_new=Zpu_old*(Sb_new/Sb_old)*(Vb_old/Vb_new)**2
            res = "═══ PASO A PASO ═══\n\n"
            res += f"[1] Vpu = {Vr}/{Vb} = {Vpu:.4f} pu\n\n"
            res += f"[2] Spu = {Sr}/{Sb} = {Spu:.4f} pu\n\n"
            res += f"[3] Zbase = ({Vb}kV)² / ({Sb}MVA)\n    = {Zbase:.4f} Ω\n\n"
            res += f"[4] Zpu = {Zr}/Zbase = {Zr}/{Zbase:.4f}\n    = {Zpu:.4f} pu\n\n"
            res += f"[5] Cambio de base:\n    Zpu_nuevo = {Zpu_old} × ({Sb_new}/{Sb_old}) × ({Vb_old}/{Vb_new})²\n    = {Zpu_new:.4f} pu\n"
            self.result.setPlainText(res)
        except Exception as e: self.result.setPlainText(f"Error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Tema 2 – Inductancia
# ─────────────────────────────────────────────────────────────────────────────
class SolverInductancia(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #020617;")
        main = QVBoxLayout(self); main.setSpacing(8); main.setContentsMargins(10,10,10,10)
        main.addWidget(styled_label("TEMA 2 · INDUCTANCIA DE LÍNEAS DE TRANSMISIÓN", "#10b981", True, 15))
        main.addWidget(DiagramInductancia())

        left = QWidget(); left.setStyleSheet("background:#020617;")
        llay = QVBoxLayout(left); llay.setSpacing(6)
        box = section_box("Parámetros de la línea trifásica")
        f = QFormLayout()
        self.r_cond = QLineEdit("1.5"); self.d12=QLineEdit("2.0"); self.d23=QLineEdit("2.5")
        self.d31=QLineEdit("4.5"); self.freq=QLineEdit("60")
        for lbl, w in [("Radio conductor r (cm):", self.r_cond), ("D12 (m):", self.d12),
                       ("D23 (m):", self.d23), ("D31 (m):", self.d31), ("Frecuencia (Hz):", self.freq)]:
            w.setStyleSheet(field_style()); f.addRow(styled_label(lbl, "#94a3b8", size=11), w)
        box.setLayout(f); llay.addWidget(box)
        btn = calc_btn("#10b981"); btn.clicked.connect(self.calcular); llay.addWidget(btn)

        right = QWidget(); right.setStyleSheet("background:#020617;")
        rlay = QVBoxLayout(right)
        rlay.addWidget(styled_label("📐 SOLUCIÓN PASO A PASO", "#f59e0b", True, 12))
        self.result = result_box(); rlay.addWidget(self.result)
        main.addWidget(build_two_panel(left, right), stretch=1)

    def calcular(self):
        try:
            r=float(self.r_cond.text())/100; D12=float(self.d12.text()); D23=float(self.d23.text()); D31=float(self.d31.text()); f=float(self.freq.text())
            mu0=4*np.pi*1e-7; r_p=r*np.exp(-1/4); GMD=(D12*D23*D31)**(1/3)
            L=(mu0/(2*np.pi))*np.log(GMD/r_p); XL=2*np.pi*f*L
            res="═══ PASO A PASO ═══\n\n"
            res+=f"[1] r' = r·e^(-1/4) = {r*100:.2f}cm × {np.exp(-1/4):.4f}\n    r' = {r_p*100:.5f} cm\n\n"
            res+=f"[2] GMD = ∛({D12}×{D23}×{D31})\n    GMD = {GMD:.4f} m\n\n"
            res+=f"[3] L = (μ₀/2π) × ln(GMD/r')\n    L = (4π×10⁻⁷/2π) × ln({GMD:.4f}/{r_p:.6f})\n    L = {L*1e6:.4f} μH/m\n    L = {L*1e3:.5f} mH/km\n\n"
            res+=f"[4] XL = 2π×{f}×{L:.8f}\n    XL = {XL*1000:.4f} Ω/km\n"
            self.result.setPlainText(res)
        except Exception as e: self.result.setPlainText(f"Error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Tema 3 – Capacidad
# ─────────────────────────────────────────────────────────────────────────────
class SolverCapacidad(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #020617;")
        main = QVBoxLayout(self); main.setSpacing(8); main.setContentsMargins(10,10,10,10)
        main.addWidget(styled_label("TEMA 3 · CAPACIDAD DE LÍNEAS DE TRANSMISIÓN", "#f59e0b", True, 15))
        main.addWidget(DiagramCapacidad())

        left = QWidget(); left.setStyleSheet("background:#020617;")
        llay = QVBoxLayout(left)
        box = section_box("Parámetros de la línea trifásica")
        f = QFormLayout()
        self.r_cond=QLineEdit("1.5"); self.d12=QLineEdit("2.0"); self.d23=QLineEdit("2.5")
        self.d31=QLineEdit("4.5"); self.freq=QLineEdit("60"); self.vln=QLineEdit("115")
        for lbl, w in [("Radio conductor r (cm):", self.r_cond), ("D12 (m):", self.d12),
                       ("D23 (m):", self.d23), ("D31 (m):", self.d31), ("Frecuencia (Hz):", self.freq),
                       ("Voltaje L-N (kV):", self.vln)]:
            w.setStyleSheet(field_style()); f.addRow(styled_label(lbl, "#94a3b8", size=11), w)
        box.setLayout(f); llay.addWidget(box)
        btn = calc_btn("#f59e0b"); btn.clicked.connect(self.calcular); llay.addWidget(btn)

        right = QWidget(); right.setStyleSheet("background:#020617;")
        rlay = QVBoxLayout(right)
        rlay.addWidget(styled_label("📐 SOLUCIÓN PASO A PASO", "#f59e0b", True, 12))
        self.result = result_box(); rlay.addWidget(self.result)
        main.addWidget(build_two_panel(left, right), stretch=1)

    def calcular(self):
        try:
            r=float(self.r_cond.text())/100; D12=float(self.d12.text()); D23=float(self.d23.text()); D31=float(self.d31.text())
            f=float(self.freq.text()); VLN=float(self.vln.text())*1000; eps0=8.854e-12
            GMD=(D12*D23*D31)**(1/3); C=(2*np.pi*eps0)/np.log(GMD/r); BC=2*np.pi*f*C; QC=VLN**2*BC*1000/1e6
            res="═══ PASO A PASO ═══\n\n"
            res+=f"[1] GMD = ∛({D12}×{D23}×{D31}) = {GMD:.4f} m\n\n"
            res+=f"[2] C = 2π×ε₀ / ln({GMD:.4f}/{r:.4f})\n    C = {C*1e12:.4f} pF/m\n    C = {C*1e9:.5f} nF/km\n\n"
            res+=f"[3] BC = ω×C = 2π×{f}×{C:.4e}\n    BC = {BC*1e6:.4f} μS/m\n    BC = {BC*1e3:.4f} mS/km\n\n"
            res+=f"[4] QC = V² × BC_km\n    QC = ({VLN/1000:.1f})² × {BC*1000*1e6:.4f}×10⁻⁶\n    QC ≈ {QC:.5f} MVAR/km\n"
            self.result.setPlainText(res)
        except Exception as e: self.result.setPlainText(f"Error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Tema 4 – Modelos de Línea
# ─────────────────────────────────────────────────────────────────────────────
class SolverLineas(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #020617;")
        main = QVBoxLayout(self); main.setSpacing(8); main.setContentsMargins(10,10,10,10)
        main.addWidget(styled_label("TEMA 4 · MODELOS DE LÍNEAS DE TRANSMISIÓN", "#8b5cf6", True, 15))
        main.addWidget(DiagramLineas())

        left = QWidget(); left.setStyleSheet("background:#020617;")
        llay = QVBoxLayout(left)
        box = section_box("Línea corta (modelo serie Z)")
        f = QFormLayout()
        self.R_km=QLineEdit("0.05"); self.X_km=QLineEdit("0.4"); self.longit=QLineEdit("100")
        self.VR=QLineEdit("115"); self.IR=QLineEdit("200"); self.fp=QLineEdit("0.9")
        for lbl, w in [("R (Ω/km):", self.R_km), ("X (Ω/km):", self.X_km), ("Longitud (km):", self.longit),
                       ("VR L-L (kV):", self.VR), ("IR (A):", self.IR), ("F.P. (cosφ):", self.fp)]:
            w.setStyleSheet(field_style()); f.addRow(styled_label(lbl, "#94a3b8", size=11), w)
        box.setLayout(f); llay.addWidget(box)
        btn = calc_btn("#8b5cf6"); btn.clicked.connect(self.calcular); llay.addWidget(btn)

        right = QWidget(); right.setStyleSheet("background:#020617;")
        rlay = QVBoxLayout(right)
        rlay.addWidget(styled_label("📐 SOLUCIÓN PASO A PASO", "#f59e0b", True, 12))
        self.result = result_box(); rlay.addWidget(self.result)
        main.addWidget(build_two_panel(left, right), stretch=1)

    def calcular(self):
        try:
            Rkm=float(self.R_km.text()); Xkm=float(self.X_km.text()); L=float(self.longit.text())
            VR_ll=float(self.VR.text())*1000; IR_mag=float(self.IR.text()); fp=float(self.fp.text())
            phi=np.arccos(fp); VR_ln=VR_ll/np.sqrt(3)
            Z=complex(Rkm*L, Xkm*L); IR=complex(IR_mag*fp, -IR_mag*np.sin(phi)); VR=complex(VR_ln, 0)
            VS=VR+Z*IR; VS_ll=abs(VS)*np.sqrt(3)/1000; RV=(abs(VS)-abs(VR))/abs(VR)*100
            Ploss=(abs(IR)**2)*Rkm*L/1e6
            res="═══ PASO A PASO ═══\n\n"
            res+=f"[1] Z = {Rkm}×{L} + j{Xkm}×{L}\n    Z = {Z.real:.2f}+j{Z.imag:.2f} Ω\n\n"
            res+=f"[2] φ = arccos({fp}) = {np.degrees(phi):.2f}°\n    IR = {IR_mag}∠-{np.degrees(phi):.2f}°\n    IR = {IR.real:.2f}{IR.imag:+.2f}j A\n\n"
            res+=f"[3] VS = VR + Z·IR\n    VS = {VR.real:.2f} + ({Z.real:.2f}+j{Z.imag:.2f})·({IR.real:.2f}{IR.imag:+.2f}j)\n    VS = {VS.real:.2f}{VS.imag:+.2f}j V L-N\n    |VS| = {abs(VS):.2f} V  =  {VS_ll:.4f} kV L-L\n    ∠VS = {np.degrees(np.angle(VS)):.3f}°\n\n"
            res+=f"[4] Regulación:\n    RV% = ({abs(VS):.2f} − {VR_ln:.2f}) / {VR_ln:.2f} × 100\n    RV% = {RV:.3f}%\n\n"
            res+=f"[5] Pérdidas:\n    P = I²·R = {abs(IR):.2f}²·{Rkm*L:.2f}\n    P = {Ploss:.4f} MW\n"
            self.result.setPlainText(res)
        except Exception as e: self.result.setPlainText(f"Error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Tema 5 – Constantes ABCD
# ─────────────────────────────────────────────────────────────────────────────
class SolverConstantesABCD(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #020617;")
        main = QVBoxLayout(self); main.setSpacing(8); main.setContentsMargins(10,10,10,10)
        main.addWidget(styled_label("TEMA 5 · CONSTANTES GENERALIZADAS ABCD", "#f472b6", True, 15))
        main.addWidget(DiagramABCD())

        left = QWidget(); left.setStyleSheet("background:#020617;")
        llay = QVBoxLayout(left)
        box = section_box("Línea Media — Modelo π")
        f = QFormLayout()
        self.R=QLineEdit("5"); self.X=QLineEdit("30"); self.BC=QLineEdit("0.002")
        self.VR=QLineEdit("115"); self.IR=QLineEdit("200"); self.fp=QLineEdit("0.85")
        for lbl, w in [("R total (Ω):", self.R), ("X total (Ω):", self.X), ("BC total (S):", self.BC),
                       ("VR L-L (kV):", self.VR), ("IR (A):", self.IR), ("F.P.:", self.fp)]:
            w.setStyleSheet(field_style()); f.addRow(styled_label(lbl, "#94a3b8", size=11), w)
        box.setLayout(f); llay.addWidget(box)
        btn = calc_btn("#f472b6"); btn.clicked.connect(self.calcular); llay.addWidget(btn)

        right = QWidget(); right.setStyleSheet("background:#020617;")
        rlay = QVBoxLayout(right)
        rlay.addWidget(styled_label("📐 SOLUCIÓN PASO A PASO", "#f59e0b", True, 12))
        self.result = result_box(); rlay.addWidget(self.result)
        main.addWidget(build_two_panel(left, right), stretch=1)

    def calcular(self):
        try:
            Z=complex(float(self.R.text()), float(self.X.text())); Y=complex(0, float(self.BC.text()))
            VR_ll=float(self.VR.text())*1000; IR_m=float(self.IR.text()); fp=float(self.fp.text())
            phi=np.arccos(fp); VR_ln=VR_ll/np.sqrt(3)
            VR_f=complex(VR_ln,0); IR_f=complex(IR_m*fp, -IR_m*np.sin(phi))
            A=1+Z*Y/2; B=Z; C=Y*(1+Z*Y/4); D=A
            VS=A*VR_f+B*IR_f; IS=C*VR_f+D*IR_f
            res="═══ PASO A PASO ═══\n\n"
            res+=f"[1] Z = {Z.real:.2f}+j{Z.imag:.2f} Ω\n    Y = j{Y.imag:.6f} S\n\n"
            res+=f"[2] Constantes ABCD:\n    A = 1 + ZY/2 = {A.real:.6f}{A.imag:+.6f}j\n    B = Z        = {B.real:.4f}{B.imag:+.4f}j Ω\n    C = Y(1+ZY/4)= {C.real:.8f}{C.imag:+.8f}j S\n    D = A\n\n"
            res+=f"[3] VS = A·VR + B·IR\n    VS = {VS.real:.2f}{VS.imag:+.2f}j V L-N\n    |VS| = {abs(VS):.2f} V  =  {abs(VS)*np.sqrt(3)/1000:.4f} kV L-L\n    ∠VS = {np.degrees(np.angle(VS)):.3f}°\n\n"
            res+=f"[4] IS = C·VR + D·IR\n    |IS| = {abs(IS):.4f} A\n\n"
            res+=f"[5] Verificacion AD-BC = {(A*D-B*C).real:.4f}{(A*D-B*C).imag:+.6f}j  (debe ser = 1)\n"
            self.result.setPlainText(res)
        except Exception as e: self.result.setPlainText(f"Error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Tema 6 – Diagramas Circulares
# ─────────────────────────────────────────────────────────────────────────────
class SolverCirculares(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #020617;")
        main = QVBoxLayout(self); main.setSpacing(8); main.setContentsMargins(10,10,10,10)
        main.addWidget(styled_label("TEMA 6 · DIAGRAMAS CIRCULARES DE POTENCIA", "#fb923c", True, 15))
        main.addWidget(DiagramCirculares())

        left = QWidget(); left.setStyleSheet("background:#020617;")
        llay = QVBoxLayout(left)
        box = section_box("Parámetros del sistema")
        f = QFormLayout()
        self.VS=QLineEdit("132"); self.VR=QLineEdit("115"); self.A_mag=QLineEdit("0.99")
        self.A_ang=QLineEdit("1.5"); self.B_mag=QLineEdit("35"); self.B_ang=QLineEdit("80"); self.delta=QLineEdit("15")
        for lbl, w in [("VS L-L (kV):", self.VS), ("VR L-L (kV):", self.VR), ("|A|:", self.A_mag),
                       ("∠A (°):", self.A_ang), ("|B| (Ω):", self.B_mag), ("∠B (°):", self.B_ang), ("δ (°):", self.delta)]:
            w.setStyleSheet(field_style()); f.addRow(styled_label(lbl, "#94a3b8", size=11), w)
        box.setLayout(f); llay.addWidget(box)
        btn = calc_btn("#fb923c"); btn.clicked.connect(self.calcular); llay.addWidget(btn)

        right = QWidget(); right.setStyleSheet("background:#020617;")
        rlay = QVBoxLayout(right)
        rlay.addWidget(styled_label("📐 SOLUCIÓN PASO A PASO", "#f59e0b", True, 12))
        self.result = result_box(); rlay.addWidget(self.result)
        main.addWidget(build_two_panel(left, right), stretch=1)

    def calcular(self):
        try:
            VS_kv=float(self.VS.text()); VR_kv=float(self.VR.text())
            Am=float(self.A_mag.text()); Aa=np.radians(float(self.A_ang.text()))
            Bm=float(self.B_mag.text()); Ba=np.radians(float(self.B_ang.text()))
            d=np.radians(float(self.delta.text()))
            VS=VS_kv*1000/np.sqrt(3); VR=VR_kv*1000/np.sqrt(3)
            OR=Am*VR**2/Bm; RR=VS*VR/Bm
            PR=3*((VS*VR/Bm)*np.sin(d+Ba-np.pi/2)-(Am*VR**2/Bm)*np.sin(Ba-Aa-np.pi/2))
            QR=3*((VS*VR/Bm)*np.cos(d+Ba-np.pi/2)-(Am*VR**2/Bm)*np.cos(Ba-Aa-np.pi/2)) # approximate
            Pmax=3*(VS*VR/Bm-Am*VR**2/Bm)/1e6
            res="═══ PASO A PASO: Diagramas Circulares ═══\n\n"
            res+=f"[1] Voltajes L-N:\n    VS = {VS/1000:.4f} kV\n    VR = {VR/1000:.4f} kV\n\n"
            res+=f"[2] Centro círculo recepción (|OR|):\n    |OR| = |A|×VR²/|B| = {Am}×{VR**2:.0f}/{Bm}\n    |OR| = {OR:.2f} VA L-N\n\n"
            res+=f"[3] Radio círculo recepción:\n    RR = |VS|×|VR|/|B| = {VS:.0f}×{VR:.0f}/{Bm}\n    RR = {RR:.2f} VA L-N\n\n"
            res+=f"[4] PR (δ={float(self.delta.text())}°) ≈ {PR/1e6:.4f} MW (3φ)\n\n"
            res+=f"[5] Potencia máxima transferible:\n    PR_max = 3(RR - |OR|)/10⁶\n    PR_max ≈ {Pmax:.4f} MW (3φ)\n"
            self.result.setPlainText(res)
        except Exception as e: self.result.setPlainText(f"Error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Tema 7 – Flujo de Potencia
# ─────────────────────────────────────────────────────────────────────────────
class SolverFlujoPotencia(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #020617;")
        main = QVBoxLayout(self); main.setSpacing(8); main.setContentsMargins(10,10,10,10)
        main.addWidget(styled_label("TEMA 7 · FLUJO DE POTENCIA (Gauss-Seidel)", "#22d3ee", True, 15))
        main.addWidget(DiagramFlujoPotencia())

        left = QWidget(); left.setStyleSheet("background:#020617;")
        llay = QVBoxLayout(left)
        box = section_box("Sistema 2 barras (PQ Load)")
        f = QFormLayout()
        self.y_serie=QLineEdit("10"); self.ang_y=QLineEdit("-85"); self.v1=QLineEdit("1.05")
        self.p2=QLineEdit("-0.5"); self.q2=QLineEdit("-0.2"); self.eps=QLineEdit("0.001")
        for lbl, w in [("|Y_serie| (pu):", self.y_serie), ("∠Y (°):", self.ang_y), ("V1 slack (pu):", self.v1),
                       ("P2 inyectada (pu):", self.p2), ("Q2 inyectada (pu):", self.q2), ("Tolerancia ε:", self.eps)]:
            w.setStyleSheet(field_style()); f.addRow(styled_label(lbl, "#94a3b8", size=11), w)
        box.setLayout(f); llay.addWidget(box)
        btn = calc_btn("#22d3ee"); btn.clicked.connect(self.calcular); llay.addWidget(btn)

        right = QWidget(); right.setStyleSheet("background:#020617;")
        rlay = QVBoxLayout(right)
        rlay.addWidget(styled_label("📐 ITERACIONES GAUSS-SEIDEL", "#f59e0b", True, 12))
        self.result = result_box(); rlay.addWidget(self.result)
        main.addWidget(build_two_panel(left, right), stretch=1)

    def calcular(self):
        try:
            Y_mag=float(self.y_serie.text()); Y_ang=np.radians(float(self.ang_y.text()))
            V1=float(self.v1.text()); P2=float(self.p2.text()); Q2=float(self.q2.text()); eps=float(self.eps.text())
            Y12=-Y_mag*np.exp(1j*Y_ang); Y11=-Y12; Y22=-Y12
            V2=complex(1.0, 0.0)
            res="═══ PASO A PASO: Gauss-Seidel ═══\n\n"
            res+=f"Ybus (2 barras):\n  Y11 = Y22 = {Y11:.4f}\n  Y12 = Y21 = {Y12:.4f}\n\n"
            res+="Fórmula iterativa:\n  V2(k+1) = [1/Y22] × [(P2−jQ2)/V2*(k) − Y12×V1]\n\n"
            for k in range(30):
                S2c=complex(P2,-Q2); V2_new=(S2c/V2.conjugate()-Y12*V1)/Y22; dV=abs(V2_new-V2)
                res+=f"  k={k+1:2d}: |V2|={abs(V2_new):.6f}  ∠{np.degrees(np.angle(V2_new)):+.4f}°  |ΔV|={dV:.2e}\n"
                V2=V2_new
                if dV<eps: res+=f"\n✅ Convergió en {k+1} iteraciones (ε={eps})\n"; break
            S12=V1*(Y11*V1+Y12*V2).conjugate()
            res+=f"\n═══ RESULTADOS ═══\n  V2 = {abs(V2):.6f} pu  ∠ {np.degrees(np.angle(V2)):.4f}°\n"
            res+=f"  P12 = {S12.real:.4f} pu  Q12 = {S12.imag:.4f} pu\n"
            self.result.setPlainText(res)
        except Exception as e: self.result.setPlainText(f"Error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Tema 8 – Despacho Económico
# ─────────────────────────────────────────────────────────────────────────────
class SolverDespachoEconomico(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #020617;")
        main = QVBoxLayout(self); main.setSpacing(8); main.setContentsMargins(10,10,10,10)
        main.addWidget(styled_label("TEMA 8 · DESPACHO ECONÓMICO DE CENTRALES TÉRMICAS", "#facc15", True, 15))
        main.addWidget(DiagramDespacho())

        left = QWidget(); left.setStyleSheet("background:#020617;")
        llay = QVBoxLayout(left)
        box = section_box("3 Unidades Generadoras  Ci = ai + bi·Pi + ci·Pi²")
        f = QFormLayout()
        entries = [("a1,b1,c1 [$/h,$/MWh,$/MW²h]:", "200,9,0.01"),
                   ("a2,b2,c2:", "180,7.5,0.012"), ("a3,b3,c3:", "140,8,0.008"),
                   ("Pmin1,Pmax1 (MW):", "50,200"), ("Pmin2,Pmax2 (MW):", "40,150"),
                   ("Pmin3,Pmax3 (MW):", "30,250"), ("Demanda PD (MW):", "400")]
        self.fields = []
        for lbl, default in entries:
            e = QLineEdit(default); e.setStyleSheet(field_style())
            f.addRow(styled_label(lbl, "#94a3b8", size=11), e); self.fields.append(e)
        box.setLayout(f); llay.addWidget(box)
        btn = calc_btn("#facc15"); btn.clicked.connect(self.calcular); llay.addWidget(btn)

        right = QWidget(); right.setStyleSheet("background:#020617;")
        rlay = QVBoxLayout(right)
        rlay.addWidget(styled_label("📐 LAMBDA ITERATION", "#f59e0b", True, 12))
        self.result = result_box(); rlay.addWidget(self.result)
        main.addWidget(build_two_panel(left, right), stretch=1)

    def calcular(self):
        try:
            abc=[list(map(float, self.fields[i].text().split(','))) for i in range(3)]
            lims=[list(map(float, self.fields[i].text().split(','))) for i in range(3,6)]
            PD=float(self.fields[6].text())
            a=[x[0] for x in abc]; b=[x[1] for x in abc]; c=[x[2] for x in abc]
            Pmin=[x[0] for x in lims]; Pmax=[x[1] for x in lims]
            lam_min=max(b[i]+2*c[i]*Pmin[i] for i in range(3))
            lam_max=min(b[i]+2*c[i]*Pmax[i] for i in range(3))
            lam=(lam_min+lam_max)/2; P=[0.0]*3
            res="═══ PASO A PASO: Lambda Iteration ═══\n\n"
            res+="Curvas de costo incremental:\n"
            for i in range(3): res+=f"  dC{i+1}/dP = {b[i]} + {2*c[i]}·P\n"
            res+=f"\nRango λ inicial: [{lam_min:.4f}, {lam_max:.4f}]\n\n"
            for it in range(60):
                P_new=[(lam-b[i])/(2*c[i]) for i in range(3)]
                P_new=[max(Pmin[i],min(Pmax[i],P_new[i])) for i in range(3)]
                err=sum(P_new)-PD
                if abs(err)<0.01: P=P_new; break
                if err>0: lam_max=lam
                else: lam_min=lam
                lam=(lam_min+lam_max)/2; P=P_new
            costo=sum(a[i]+b[i]*P[i]+c[i]*P[i]**2 for i in range(3))
            res+=f"λ_óptimo = {lam:.5f} $/MWh\n\n"
            for i in range(3):
                res+=f"P{i+1} = (λ - {b[i]}) / {2*c[i]} = {P[i]:.2f} MW\n"
            res+=f"\nΣP = {sum(P):.2f} MW  (PD = {PD} MW)\n"
            res+=f"Costo mínimo total = {costo:.2f} $/h\n"
            self.result.setPlainText(res)
        except Exception as e: self.result.setPlainText(f"Error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Tema 9 – Teoría de Fallas
# ─────────────────────────────────────────────────────────────────────────────
class SolverFallas(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #020617;")
        main = QVBoxLayout(self); main.setSpacing(8); main.setContentsMargins(10,10,10,10)
        main.addWidget(styled_label("TEMA 9 · TEORÍA DE FALLAS (Componentes Simétricas)", "#ef4444", True, 15))
        main.addWidget(DiagramFallas())

        left = QWidget(); left.setStyleSheet("background:#020617;")
        llay = QVBoxLayout(left)
        box = section_box("Parámetros de la falla")
        f = QFormLayout()
        self.combo = QComboBox()
        self.combo.addItems(["Falla 3φ (simétrica)", "Falla 1φ a tierra (SLG)", "Falla 2φ (LL)", "Falla 2φ a tierra (DLG)"])
        self.combo.setStyleSheet("background:#1e293b;color:#f8fafc;padding:5px; border:1px solid #334155;")
        self.Vpf=QLineEdit("1.0"); self.Z1=QLineEdit("0.1"); self.Z2=QLineEdit("0.1")
        self.Z0=QLineEdit("0.3"); self.Sbase=QLineEdit("100"); self.Vbase=QLineEdit("115")
        f.addRow(styled_label("Tipo de falla:", "#94a3b8", size=11), self.combo)
        for lbl, w in [("V_prefalla (pu):", self.Vpf), ("Z1 seq+ (pu):", self.Z1),
                       ("Z2 seq− (pu):", self.Z2), ("Z0 seq0 (pu):", self.Z0),
                       ("S_base (MVA):", self.Sbase), ("V_base (kV):", self.Vbase)]:
            w.setStyleSheet(field_style()); f.addRow(styled_label(lbl, "#94a3b8", size=11), w)
        box.setLayout(f); llay.addWidget(box)
        btn = calc_btn("#ef4444"); btn.clicked.connect(self.calcular); llay.addWidget(btn)

        right = QWidget(); right.setStyleSheet("background:#020617;")
        rlay = QVBoxLayout(right)
        rlay.addWidget(styled_label("📐 SOLUCIÓN COMPONENTES SIMÉTRICAS", "#f59e0b", True, 12))
        self.result = result_box(); rlay.addWidget(self.result)
        main.addWidget(build_two_panel(left, right), stretch=1)

    def calcular(self):
        try:
            Vpf=float(self.Vpf.text())
            Z1=complex(0,float(self.Z1.text())); Z2=complex(0,float(self.Z2.text())); Z0=complex(0,float(self.Z0.text()))
            Sbase=float(self.Sbase.text())*1e6; Vbase=float(self.Vbase.text())*1000
            Ibase=Sbase/(np.sqrt(3)*Vbase); tipo=self.combo.currentIndex()
            res="═══ PASO A PASO: Fallas ═══\n\n"
            res+=f"Ibase = {Sbase/1e6:.0f}MVA / (√3×{Vbase/1000:.0f}kV) = {Ibase:.2f} A\n\n"
            if tipo==0:
                IF1=Vpf/Z1; IF=IF1
                res+="[FALLA TRIFÁSICA 3φ]\n"
                res+=f"  Red de secuencia positiva actúa sola\n"
                res+=f"  Ia1 = Vpf/Z1 = {Vpf}/j{Z1.imag} = {abs(IF1):.4f}∠{np.degrees(np.angle(IF1)):.1f}° pu\n"
                res+=f"  Ia  = Ia1 = {abs(IF1):.4f} pu = {abs(IF1)*Ibase:.2f} A\n"
            elif tipo==1:
                IF1=Vpf/(Z1+Z2+Z0); IF=3*IF1
                res+="[FALLA MONOFÁSICA A TIERRA (SLG) — Fase A]\n"
                res+=f"  Redes Z1, Z2, Z0 en SERIE\n"
                res+=f"  Ia1 = Vpf/(Z1+Z2+Z0) = {Vpf}/(j{Z1.imag+Z2.imag+Z0.imag})\n"
                res+=f"  Ia1 = {abs(IF1):.4f} pu\n"
                res+=f"  Ia  = 3·Ia1 = {abs(IF):.4f} pu = {abs(IF)*Ibase:.2f} A rms\n"
                res+=f"  Ib = Ic = 0 (fase sana)\n"
            elif tipo==2:
                IF1=Vpf/(Z1+Z2); IFb=abs(IF1)*np.sqrt(3); IF=IF1
                res+="[FALLA BIFÁSICA (LL) — Fases B-C]\n"
                res+=f"  Redes Z1 y Z2 en SERIE\n"
                res+=f"  Ia1 = Vpf/(Z1+Z2) = {Vpf}/j{Z1.imag+Z2.imag:.2f}\n"
                res+=f"  Ia1 = {abs(IF1):.4f} pu\n"
                res+=f"  |Ib| = |Ic| = √3·|Ia1| = {IFb:.4f} pu = {IFb*Ibase:.2f} A\n"
            else:
                ZZ=Z2*Z0/(Z2+Z0); IF1=Vpf/(Z1+ZZ)
                IF0=-IF1*Z2/(Z2+Z0); IF2=-IF1*Z0/(Z2+Z0); IA=IF1+IF2+IF0; IF=IA
                res+="[FALLA BIFÁSICA A TIERRA (DLG) — Fases B-C-Tierra]\n"
                res+=f"  Z2||Z0 = {ZZ.real:.6f}+j{ZZ.imag:.4f} Ω\n"
                res+=f"  Ia1 = Vpf/(Z1+Z2||Z0) = {abs(IF1):.4f}∠{np.degrees(np.angle(IF1)):.1f}° pu\n"
                res+=f"  Ia0 = {abs(IF0):.4f} pu    Ia2 = {abs(IF2):.4f} pu\n"
                res+=f"  Ia  = I1+I2+I0 = {abs(IA):.4f} pu\n"
                res+=f"  Itierrra = 3×Ia0 = {abs(3*IF0):.4f} pu = {abs(3*IF0)*Ibase:.2f} A\n"
            res+=f"\n═══ RESUMEN ═══\n|IF| = {abs(IF):.4f} pu = {abs(IF)*Ibase:.2f} A rms"
            self.result.setPlainText(res)
        except Exception as e: self.result.setPlainText(f"Error: {e}")
