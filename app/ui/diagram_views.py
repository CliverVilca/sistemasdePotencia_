"""
Diagramas visuales únicos para cada módulo del libro Pumacayo.
Cada clase dibuja el esquema eléctrico específico del tema.
"""
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QSizePolicy
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath, QPolygonF


class BaseDiagram(QGraphicsView):
    """Vista base para todos los diagramas técnicos."""
    def __init__(self, height=200):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setFixedHeight(height)
        self.setStyleSheet("background: #020617; border: 1px solid #334155; border-radius: 8px;")
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.draw()

    def draw(self): pass

    def line(self, x1, y1, x2, y2, color="#38bdf8", width=2):
        pen = QPen(QColor(color), width)
        self.scene.addLine(x1, y1, x2, y2, pen)

    def text(self, x, y, txt, color="#94a3b8", size=9, bold=False):
        item = self.scene.addText(txt)
        item.setDefaultTextColor(QColor(color))
        f = QFont("Consolas", size)
        if bold: f.setBold(True)
        item.setFont(f)
        item.setPos(x, y)
        return item

    def circle(self, cx, cy, r, color="#38bdf8", fill=None, width=2):
        pen = QPen(QColor(color), width)
        brush = QBrush(QColor(fill)) if fill else QBrush(Qt.BrushStyle.NoBrush)
        self.scene.addEllipse(cx - r, cy - r, 2*r, 2*r, pen, brush)

    def rect(self, x, y, w, h, color="#38bdf8", fill=None, width=2):
        pen = QPen(QColor(color), width)
        brush = QBrush(QColor(fill)) if fill else QBrush(Qt.BrushStyle.NoBrush)
        self.scene.addRect(x, y, w, h, pen, brush)


# ─────────────────────────────────────────────────────────────────────────────
# Tema 1 – Sistema por Unidad: circuito multitensión con transformadores
# ─────────────────────────────────────────────────────────────────────────────
class DiagramPerUnit(BaseDiagram):
    def __init__(self): super().__init__(height=230)
    def draw(self):
        self.setSceneRect(-10, -10, 760, 220)
        # Zonas de voltaje
        zones = [("Zona 1\nV_base1", 50, "#10b981"), ("Zona 2\nV_base2", 350, "#f59e0b"), ("Zona 3\nV_base3", 580, "#ef4444")]
        for lbl, x, c in zones:
            self.scene.addRect(x, 20, 160, 160, QPen(QColor(c), 1, Qt.PenStyle.DashLine), QBrush(QColor(c + "15")))
            self.text(x + 5, 22, lbl, c, 8)
        # Generador
        self.circle(130, 100, 35, "#10b981", "#10b98120")
        self.text(112, 91, "Gen", "#10b981", 9, True)
        # Lineas y transformadores
        self.line(165, 100, 230, 100, "#f8fafc"); self.text(185, 82, "ZL1", "#94a3b8", 8)
        # Trafo 1
        self.circle(245, 100, 18, "#f59e0b"); self.circle(263, 100, 18, "#f59e0b")
        self.text(238, 108, "T1", "#f59e0b", 7, True)
        # Bus central
        self.line(280, 100, 420, 100, "#f8fafc"); self.text(340, 80, "Bus", "#38bdf8", 9, True)
        # Trafo 2
        self.circle(435, 100, 18, "#ef4444"); self.circle(453, 100, 18, "#ef4444")
        self.text(428, 108, "T2", "#ef4444", 7, True)
        # Carga
        self.line(470, 100, 540, 100)
        path = QPainterPath()
        path.moveTo(540, 80); path.lineTo(560, 100); path.lineTo(540, 120); path.closeSubpath()
        self.scene.addPath(path, QPen(QColor("#ef4444"), 2), QBrush(QColor("#ef4444")))
        self.text(545, 125, "Carga", "#94a3b8", 8)
        # Ecuaciones
        self.text(20, 190, "Vpu = V_real / V_base          Zbase = V²base / Sbase          Zpu = Z_real / Zbase", "#38bdf8", 8)


# ─────────────────────────────────────────────────────────────────────────────
# Tema 2 – Inductancia: sección transversal de conductores trifásicos
# ─────────────────────────────────────────────────────────────────────────────
class DiagramInductancia(BaseDiagram):
    def __init__(self): super().__init__(height=250)
    def draw(self):
        self.setSceneRect(-10, -10, 760, 250)
        # 3 conductores
        conductors = [("A", 150, 60, "#10b981"), ("B", 380, 60, "#38bdf8"), ("C", 620, 60, "#ef4444")]
        for lbl, cx, cy, c in conductors:
            self.circle(cx, cy, 35, c, "#0f172a")
            self.circle(cx, cy, 8, c, c)  # nucleo
            self.text(cx - 5, cy - 8, lbl, c, 12, True)
        # Distancias
        self.line(150, 115, 380, 115, "#334155")
        self.text(250, 120, "D12", "#f59e0b", 9)
        self.line(380, 115, 620, 115, "#334155")
        self.text(490, 120, "D23", "#f59e0b", 9)
        self.line(150, 135, 620, 135, "#334155", 1)
        self.text(365, 140, "D31", "#f59e0b", 9)
        # Radio
        self.line(150, 60, 185, 60, "#94a3b8", 1)
        self.text(155, 42, "r  (r'=r·e⁻¹/⁴)", "#94a3b8", 8)
        # Fórmula
        self.text(80, 175, "GMD = ∛(D12 · D23 · D31)", "#38bdf8", 10, True)
        self.text(80, 200, "L = (μ₀/2π) · ln(GMD / r')    [H/m]", "#10b981", 10)
        self.text(80, 225, "XL = 2πf · L    [Ω/m]", "#f59e0b", 10)


# ─────────────────────────────────────────────────────────────────────────────
# Tema 3 – Capacidad: sección transversal con campo eléctrico
# ─────────────────────────────────────────────────────────────────────────────
class DiagramCapacidad(BaseDiagram):
    def __init__(self): super().__init__(height=250)
    def draw(self):
        self.setSceneRect(-10, -10, 760, 250)
        conductors = [("A", 150, 80, "#10b981"), ("B", 380, 80, "#38bdf8"), ("C", 620, 80, "#ef4444")]
        for lbl, cx, cy, c in conductors:
            self.circle(cx, cy, 30, c, "#0f172a")
            self.circle(cx, cy, 8, c, c)
            self.text(cx - 5, cy - 7, lbl, c, 12, True)
            # Líneas de campo eléctrico (radiales)
            for angle_deg in range(0, 360, 45):
                import math
                angle = math.radians(angle_deg)
                x1 = cx + 30 * math.cos(angle); y1 = cy + 30 * math.sin(angle)
                x2 = cx + 60 * math.cos(angle); y2 = cy + 60 * math.sin(angle)
                self.line(x1, y1, x2, y2, c + "60", 1)
        # Capacitancias de línea
        self.text(250, 150, "Cab", "#f59e0b", 9)
        self.text(480, 150, "Cbc", "#f59e0b", 9)
        self.text(365, 50, "Cac", "#f59e0b", 8)
        # Fórmulas
        self.text(80, 175, "C = 2πε₀ / ln(GMD/r)    [F/m]", "#38bdf8", 10, True)
        self.text(80, 200, "BC = ωC    [S/m]       ε₀ = 8.854×10⁻¹² F/m", "#10b981", 10)
        self.text(80, 225, "QC = V² · BC    [VAR/m] → potencia generada por la línea", "#f59e0b", 10)


# ─────────────────────────────────────────────────────────────────────────────
# Tema 4 – Líneas de Transmisión: modelos en cascada
# ─────────────────────────────────────────────────────────────────────────────
class DiagramLineas(BaseDiagram):
    def __init__(self): super().__init__(height=260)
    def draw(self):
        self.setSceneRect(-10, -10, 760, 260)
        # Extremo envío
        self.line(20, 80, 80, 80); self.text(5, 60, "VS", "#10b981", 9, True)
        self.text(5, 85, "IS →", "#94a3b8", 8)
        # Impedancia serie Z (caja)
        self.rect(80, 58, 120, 44, "#f59e0b", "#f59e0b20")
        self.text(110, 70, "R + jX", "#f59e0b", 9, True)
        # Línea central
        self.line(200, 80, 560, 80)
        # Extremo recepción
        self.line(560, 80, 630, 80); self.text(635, 60, "VR", "#ef4444", 9, True)
        self.text(625, 85, "← IR", "#94a3b8", 8)
        # Carga
        path = QPainterPath(); path.moveTo(630, 60); path.lineTo(660, 80); path.lineTo(630, 100); path.closeSubpath()
        self.scene.addPath(path, QPen(QColor("#ef4444"), 2), QBrush(QColor("#ef444440")))
        self.text(660, 70, "PQ\nCarga", "#94a3b8", 8)
        # Modelo π (admitancias shunt)
        self.text(225, 50, "── Modelo π ──", "#38bdf8", 9, True)
        for x_shunt in [280, 480]:
            self.line(x_shunt, 80, x_shunt, 150)
            self.rect(x_shunt - 20, 150, 40, 30, "#38bdf8", "#38bdf820")
            self.text(x_shunt - 12, 155, "Y/2", "#38bdf8", 8)
            self.line(x_shunt - 25, 185, x_shunt + 25, 185, "#64748b", 2)
            self.line(x_shunt - 15, 190, x_shunt + 15, 190, "#64748b", 2)
            self.line(x_shunt - 5, 195, x_shunt + 5, 195, "#64748b", 2)
        # Fórmulas
        self.text(20, 215, "Corta: VS = VR + Z·IR", "#10b981", 9)
        self.text(20, 235, "Media π: A=D=1+ZY/2  B=Z  C=Y(1+ZY/4)", "#38bdf8", 9)
        self.text(20, 255, "Reg.Volt: RV% = (|VS|−|VR|)/|VR| × 100%", "#f59e0b", 9)


# ─────────────────────────────────────────────────────────────────────────────
# Tema 5 – Constantes ABCD: cuadripolo de dos puertos
# ─────────────────────────────────────────────────────────────────────────────
class DiagramABCD(BaseDiagram):
    def __init__(self): super().__init__(height=240)
    def draw(self):
        self.setSceneRect(-10, -10, 760, 240)
        # Puerto envío
        self.line(20, 80, 80, 80)
        self.line(20, 150, 80, 150)
        self.text(5, 60, "VS", "#10b981", 10, True)
        self.text(5, 150, "IS→", "#10b981", 9)
        # Caja del cuadripolo
        self.rect(80, 30, 560, 160, "#38bdf8", "#38bdf808", 3)
        self.text(310, 95, "RED\nELÉCTRICA", "#38bdf8", 12, True)
        # Puerto recepción
        self.line(640, 80, 710, 80)
        self.line(640, 150, 710, 150)
        self.text(715, 60, "VR", "#ef4444", 10, True)
        self.text(710, 150, "←IR", "#ef4444", 9)
        # Matriz ABCD
        self.text(60, 210, "│VS│   │A  B│ │VR│         A·D − B·C = 1  (red recíproca)", "#f8fafc", 9)
        self.text(60, 225, "│IS│ = │C  D│·│IR│         Corta: A=D=1  B=Z  C=0", "#94a3b8", 9)


# ─────────────────────────────────────────────────────────────────────────────
# Tema 6 – Diagramas Circulares: círculo P-Q
# ─────────────────────────────────────────────────────────────────────────────
class DiagramCirculares(BaseDiagram):
    def __init__(self): super().__init__(height=300)
    def draw(self):
        self.setSceneRect(-10, -10, 760, 300)
        # Ejes P-Q
        cx, cy = 380, 160
        self.line(60, cy, 700, cy, "#334155", 1);  self.text(695, cy + 5, "P →", "#64748b", 8)
        self.line(cx, 20, cx, 280, "#334155", 1); self.text(cx + 5, 15, "↑ Q", "#64748b", 8)
        # Centro de los círculos (ejemplo aproximado)
        oc_x, oc_y = cx - 40, cy + 30  # reflejo zona absorción MVAR
        # Círculo recepción (azul)
        r_r = 130
        self.scene.addEllipse(oc_x - r_r, oc_y - r_r, 2*r_r, 2*r_r,
                               QPen(QColor("#38bdf8"), 2, Qt.PenStyle.DashLine))
        self.text(oc_x - 10, oc_y - 6, "OR", "#38bdf8", 8)
        self.circle(oc_x, oc_y, 4, "#38bdf8", "#38bdf8")
        # Círculo envío (rosa)
        os_x, os_y = cx + 30, cy - 20
        r_s = 110
        self.scene.addEllipse(os_x - r_s, os_y - r_s, 2*r_s, 2*r_s,
                               QPen(QColor("#f472b6"), 2, Qt.PenStyle.DashLine))
        self.text(os_x - 10, os_y - 6, "OS", "#f472b6", 8)
        self.circle(os_x, os_y, 4, "#f472b6", "#f472b6")
        # Radio y punto de operación
        px, py = cx + 60, cy - 80
        self.line(oc_x, oc_y, px, py, "#10b981", 2)
        self.circle(px, py, 6, "#10b981", "#10b981")
        self.text(px + 5, py - 15, "Punto de\noperación (δ)", "#10b981", 8)
        # Etiquetas
        self.text(oc_x + r_r + 5, oc_y - 8, "RR = |VS||VR|/|B|", "#38bdf8", 8)
        self.text(20, 275, "PR_max = RR − |OR|     (potencia máxima transferible sin perder estabilidad)", "#facc15", 9)


# ─────────────────────────────────────────────────────────────────────────────
# Tema 7 – Flujo de Potencia: red nodal con Ybus
# ─────────────────────────────────────────────────────────────────────────────
class DiagramFlujoPotencia(BaseDiagram):
    def __init__(self): super().__init__(height=280)
    def draw(self):
        self.setSceneRect(-10, -10, 760, 280)
        buses = [("1\nSlack\nV∠0°", 100, 100, "#10b981"), ("2\nPV Bus\nV|P", 380, 50, "#f59e0b"),
                 ("3\nPQ Bus\nP+jQ", 620, 100, "#ef4444"), ("4\nPQ Bus\nP+jQ", 380, 200, "#8b5cf6")]
        for lbl, bx, by, c in buses:
            self.rect(bx - 45, by - 35, 90, 70, c, c + "20")
            self.text(bx - 35, by - 30, lbl, c, 8, True)
        # Líneas de interconexión
        connections = [(100, 100, 380, 50), (100, 100, 380, 200), (380, 50, 620, 100), (380, 200, 620, 100)]
        for x1, y1, x2, y2 in connections:
            self.line(x1, y1, x2, y2, "#475569", 2)
            mx, my = (x1+x2)//2, (y1+y2)//2
            self.text(mx - 15, my - 18, "Yij", "#334155", 8)
        # Matriz Ybus (simplificada)
        self.text(20, 255, "Gauss-Seidel: Vi(k+1) = [1/Yii] · [(Pi−jQi)/Vi*(k) − Σj≠i Yij·Vj]", "#38bdf8", 9)


# ─────────────────────────────────────────────────────────────────────────────
# Tema 8 – Despacho Económico: curvas de costo incremental
# ─────────────────────────────────────────────────────────────────────────────
class DiagramDespacho(BaseDiagram):
    def __init__(self): super().__init__(height=280)
    def draw(self):
        import math
        self.setSceneRect(-10, -10, 760, 280)
        # Ejes
        ax, ay = 60, 240
        self.line(ax, 20, ax, ay, "#334155", 1); self.text(ax - 10, 10, "λ", "#64748b", 10)
        self.line(ax, ay, 720, ay, "#334155", 1); self.text(715, ay + 5, "P →", "#64748b", 8)
        # 3 curvas de costo incremental (líneas rectas dCi/dP = bi + 2ci*P)
        units = [
            ("G1", 0.01, 9.0, "#10b981"),    # dC/dP = 9 + 0.02*P
            ("G2", 0.012, 7.5, "#f59e0b"),   # dC/dP = 7.5 + 0.024*P
            ("G3", 0.008, 8.0, "#ef4444"),   # dC/dP = 8 + 0.016*P
        ]
        scale_x = 2.0; scale_y = 8.0
        for name, c, b, col in units:
            pts = []
            for P in range(0, 300, 10):
                dC = b + 2*c*P
                px = ax + P * scale_x; py = ay - (dC - 6) * scale_y
                if 20 < py < ay: pts.append((px, py))
            for i in range(len(pts) - 1):
                self.line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], col, 2)
            if pts:
                self.text(pts[-1][0] + 3, pts[-1][1] - 5, name, col, 8, True)
        # Lambda óptimo (línea horizontal)
        lam_y = ay - (9.5 - 6) * scale_y
        self.line(ax, lam_y, 600, lam_y, "#facc15", 2)
        self.text(605, lam_y - 8, "λ_opt", "#facc15", 9, True)
        # P1, P2, P3
        for P_val, c_, b_, col in [(150, 0.01, 9.0, "#10b981"), (100, 0.012, 7.5, "#f59e0b"), (150, 0.008, 8.0, "#ef4444")]:
            px = ax + P_val * scale_x
            self.line(px, lam_y, px, ay, col, 1)
            self.text(px - 10, ay + 5, f"P={P_val}", col, 7)
        self.text(ax, 265, "Condición óptima: dC1/dP1 = dC2/dP2 = dC3/dP3 = λ    y    ΣPi = PD", "#38bdf8", 9)


# ─────────────────────────────────────────────────────────────────────────────
# Tema 9 – Fallas: redes de secuencia
# ─────────────────────────────────────────────────────────────────────────────
class DiagramFallas(BaseDiagram):
    def __init__(self): super().__init__(height=300)
    def draw(self):
        self.setSceneRect(-10, -10, 760, 300)
        # Título
        self.text(250, 5, "REDES DE SECUENCIA (para falla en bus k)", "#f8fafc", 10, True)
        # 3 redes en paralelo/serie
        seqs = [("Secuencia +", 80, "#10b981"), ("Secuencia −", 290, "#f59e0b"), ("Secuencia 0", 500, "#ef4444")]
        for name, sx, c in seqs:
            self.rect(sx, 50, 170, 180, c, c + "10")
            self.text(sx + 20, 55, name, c, 9, True)
            # Generador Thevenin
            self.circle(sx + 85, 100, 22, c)
            self.text(sx + 76, 91, "Vpf", c, 8)
            # Impedancia
            self.rect(sx + 60, 135, 50, 30, c)
            self.text(sx + 65, 140, "Z1" if "+" in name else ("Z2" if "−" in name else "Z0"), c, 9, True)
            self.line(sx + 85, 122, sx + 85, 135, c)
            self.line(sx + 85, 165, sx + 85, 210, c)
            # Terminal de falla
            self.circle(sx + 85, 220, 5, c, c)
        # Conexión para SLG (serie)
        self.text(20, 255, "SLG: Z1−Z2−Z0 en serie    Iaf1 = Vf/(Z1+Z2+Z0)   Ia = 3·Ia1", "#38bdf8", 9)
        self.text(20, 272, "3φ:  solo red Z1             Iaf = Vf/Z1", "#10b981", 9)
        self.text(20, 289, "LL:  Z1−Z2 en serie          Ia1 = Vf/(Z1+Z2)   |Ib|=|Ic|=√3·|Ia1|", "#f59e0b", 9)
