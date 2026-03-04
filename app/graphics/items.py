from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem
from PyQt6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPainterPath, QRadialGradient
from PyQt6.QtCore import Qt, QPointF, QRectF

class FlowDot(QGraphicsEllipseItem):
    """Punto de flujo animado para las líneas"""
    def __init__(self, line):
        super().__init__(-5, -5, 10, 10)
        self.line_item = line
        # Gradiente radial para el punto (glow effect)
        gradient = QRadialGradient(0, 0, 5)
        gradient.setColorAt(0, QColor("#38bdf8"))
        gradient.setColorAt(1, QColor(56, 189, 248, 0))
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(Qt.GlobalColor.transparent))
        self.setZValue(10)
        self.progress = 0.0

    def advance_pos(self):
        line = self.line_item.line()
        self.progress = (self.progress + 0.015) % 1.0
        x = line.x1() + (line.x2() - line.x1()) * self.progress
        y = line.y1() + (line.y2() - line.y1()) * self.progress
        self.setPos(x, y)

class SmartLine(QGraphicsLineItem):
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
        pen = QPen(QColor("#475569"), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)
        self.setZValue(-1)
        self.dots = []
        self.update_path()

    def update_path(self):
        # Conectar al centro de los items
        p1 = self.source.scenePos() + QPointF(35, 25)
        p2 = self.target.scenePos() + QPointF(35, 25)
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())

class BaseEquipment(QGraphicsRectItem):
    def __init__(self, x, y, name, type="Bus", color="#38bdf8"):
        super().__init__(0, 0, 70, 50)
        self.setPos(x, y)
        self.type = type
        self.base_color = QColor(color)
        self.setBrush(QBrush(self.base_color))
        self.setPen(QPen(QColor("#f8fafc"), 2))
        
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        # Labels
        self.label = QGraphicsTextItem(name, self)
        self.label.setDefaultTextColor(QColor("#f8fafc"))
        self.label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.label.setPos(-10, -30)
        
        self.value_label = QGraphicsTextItem("1.00 ∠ 0° pu", self)
        self.value_label.setDefaultTextColor(QColor("#38bdf8"))
        self.value_label.setFont(QFont("Consolas", 8))
        self.value_label.setPos(-10, 55)
        
        self.connections = []

    def boundingRect(self):
        # Extendemos el bounding rect para incluir los labels y el borde de selección
        return QRectF(-15, -35, 100, 110)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for conn in self.connections:
                conn.update_path()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Efecto de selección
        if self.isSelected():
            painter.setPen(QPen(QColor("#38bdf8"), 3))
            painter.drawRoundedRect(-5, -5, 80, 60, 10, 10)

        # Dibujar formas según el tipo
        color = self.base_color
        painter.setBrush(QBrush(color))
        painter.setPen(self.pen())
        
        if self.type == "Gen":
            # Generador
            painter.setBrush(QBrush(color.lighter(130)))
            painter.drawEllipse(10, 0, 50, 50)
            painter.setPen(QPen(QColor("#020617"), 2))
            path = QPainterPath()
            path.moveTo(22, 25)
            path.quadTo(28, 15, 35, 25)
            path.quadTo(42, 35, 48, 25)
            painter.drawPath(path)
            
        elif self.type == "Trafo":
            # Transformador
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(color, 3))
            painter.drawEllipse(5, 5, 40, 40)
            painter.drawEllipse(25, 5, 40, 40)
            
        elif self.type == "Bus":
            # Barra
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.lighter(160), 1))
            painter.drawRoundedRect(0, 20, 70, 10, 3, 3)
            
        elif self.type == "Load":
            # Carga
            painter.setBrush(QBrush(color))
            path = QPainterPath()
            path.moveTo(15, 10)
            path.lineTo(55, 10)
            path.lineTo(35, 45)
            path.closeSubpath()
            painter.drawPath(path)

        elif self.type == "Motor":
            # Motor
            painter.setBrush(QBrush(QColor("#8b5cf6")))
            painter.drawEllipse(10, 0, 50, 50)
            painter.setPen(QPen(QColor("white"), 2))
            painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            painter.drawText(26, 33, "M")

        elif self.type == "Cap":
            # Capacitor
            painter.setPen(QPen(QColor("#f472b6"), 3))
            painter.drawLine(20, 10, 20, 40)
            painter.drawLine(30, 10, 30, 40)
            painter.drawLine(0, 25, 20, 25)
            painter.drawLine(30, 25, 50, 25)

        elif self.type == "Breaker":
            # Interruptor
            painter.setBrush(QBrush(QColor("#94a3b8")))
            if self.isSelected(): painter.setBrush(QBrush(QColor("#ef4444")))
            painter.drawRect(20, 10, 30, 30)
            painter.drawLine(0, 25, 20, 25)
            painter.drawLine(50, 25, 70, 25)

        elif self.type == "Reactor":
            # Reactor (Inductancia)
            painter.setPen(QPen(QColor("#facc15"), 3))
            path = QPainterPath()
            path.moveTo(10, 25)
            for i in range(4):
                path.arcTo(10 + i*12, 15, 15, 20, 0, 180)
            painter.drawPath(path)

        elif self.type == "Solar":
            # Panel Solar
            painter.setBrush(QBrush(QColor("#38bdf8")))
            painter.drawRect(15, 10, 40, 30)
            painter.setPen(QPen(QColor("#0f172a"), 1))
            painter.drawLine(15, 20, 55, 20)
            painter.drawLine(15, 30, 55, 30)
            painter.drawLine(28, 10, 28, 40)
            painter.drawLine(42, 10, 42, 40)

        elif self.type == "Wind":
            # Aerogenerador
            painter.setPen(QPen(QColor("#f8fafc"), 2))
            painter.drawLine(35, 45, 35, 25)
            path = QPainterPath()
            path.moveTo(35, 25)
            path.lineTo(20, 15)
            path.moveTo(35, 25)
            path.lineTo(50, 15)
            path.moveTo(35, 25)
            path.lineTo(35, 5)
            painter.drawPath(path)

        elif self.type == "Switch":
            # Seccionador
            painter.setPen(QPen(QColor("#94a3b8"), 2))
            painter.drawLine(0, 25, 20, 25)
            painter.drawLine(50, 25, 70, 25)
            painter.drawLine(20, 25, 45, 10) # Abierto

        elif self.type == "Ground":
            # Puesta a Tierra
            painter.setPen(QPen(QColor("#64748b"), 3))
            painter.drawLine(35, 0, 35, 20) # Acometida
            painter.drawLine(20, 20, 50, 20) # Barra principal
            painter.drawLine(25, 28, 45, 28) # Barra media
            painter.drawLine(30, 36, 40, 36) # Barra inferior
