from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen, QMouseEvent
from PyQt6.QtCore import Qt, QPointF, QEvent, QLineF
import numpy as np

class PowerGraphicsView(QGraphicsView):
    """
    Motor Gráfico (Canvas Engine)
    Gestiona la visualización del diagrama unifilar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(-2500, -2500, 5000, 5000)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setBackgroundBrush(QBrush(QColor("#020617")))

        self.selected_item = None
        self.connection_mode = False
        self.first_comp = None
        self.temp_line = None
        self.item_count = 0
        
        self.setStyleSheet("border: none; outline: none;")
        self.setup_internal_items()

    def setup_internal_items(self):
        """Crea items que deben persistir aunque se borre el diagrama"""
        from PyQt6.QtWidgets import QGraphicsTextItem
        self.hud = QGraphicsTextItem()
        self.hud.setZValue(100)
        self.hud.setHtml("<div style='background: rgba(15, 23, 42, 0.9); color: #38bdf8; font-weight: bold; padding: 15px 25px; border: 2px solid #38bdf8; border-radius: 10px; font-size: 18px;'>📍 MODO CONEXIÓN ACTIVO<br><span style='font-size: 12px; font-weight: normal; color: #94a3b8;'>Haz clic en dos equipos para unirlos</span></div>")
        self.hud.setVisible(False)
        # IMPORTANTE: Que el HUD no bloquee el click del ratón
        self.hud.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.scene.addItem(self.hud)
        
    def clear_diagram(self):
        """Borra solo los equipos y líneas, preservando UI interna"""
        from app.graphics.items import BaseEquipment, SmartLine, FlowDot
        for item in self.scene.items()[:]:
            if isinstance(item, (BaseEquipment, SmartLine, FlowDot)):
                if item.scene() == self.scene:
                    self.scene.removeItem(item)
        self.item_count = 0
        self.window().status.showMessage("Lienzo despejado", 2000)

    def drawBackground(self, painter, rect):
        """Dibuja una cuadrícula técnica de fondo"""
        super().drawBackground(painter, rect)
        
        pen = QPen(QColor("#1e293b"), 1)
        painter.setPen(pen)
        
        # Cuadrícula fina
        left = int(rect.left()) - (int(rect.left()) % 50)
        top = int(rect.top()) - (int(rect.top()) % 50)
        
        lines = []
        for x in range(left, int(rect.right()), 50):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
        for y in range(top, int(rect.bottom()), 50):
            lines.append(QLineF(rect.left(), y, rect.right(), y))
            
        painter.drawLines(lines)
        
        # Cuadrícula principal
        pen.setColor(QColor("#334155"))
        pen.setWidth(2)
        painter.setPen(pen)
        
        left = int(rect.left()) - (int(rect.left()) % 250)
        top = int(rect.top()) - (int(rect.top()) % 250)
        
        lines = []
        for x in range(left, int(rect.right()), 250):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
        for y in range(top, int(rect.bottom()), 250):
            lines.append(QLineF(rect.left(), y, rect.right(), y))
            
        painter.drawLines(lines)

    def add_element(self, type_name):
        from app.graphics.items import BaseEquipment
        colors = {
            "Gen": "#10b981", "Trafo": "#f59e0b", "Bus": "#38bdf8", "Load": "#ef4444",
            "Reactor": "#facc15", "Solar": "#0ea5e9", "Wind": "#f8fafc", "Switch": "#64748b",
            "Ground": "#475569"
        }
        
        # Intentar obtener el centro visible o usar 0,0
        view_center = self.viewport().rect().center()
        scene_center = self.mapToScene(view_center)
        
        x = scene_center.x() - 35
        y = scene_center.y() - 25
        
        # Si estamos en 0,0 por falta de renderizado inicial
        if x == -35 and y == -25:
            x, y = 0, 0

        self.item_count += 1
        item = BaseEquipment(x, y, f"{type_name}-{self.item_count:02d}", 
                             type=type_name, color=colors.get(type_name, "#38bdf8"))
        self.scene.addItem(item)
        item.setSelected(True)
        return item

    def start_connection(self):
        # Asegurar que el HUD existe (por si acaso se borró la escena)
        if self.hud.scene() != self.scene:
            self.scene.addItem(self.hud)
            
        self.connection_mode = True
        self.first_comp = None
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setBackgroundBrush(QBrush(QColor("#0f172a")))
        # Centrar HUD en la vista
        view_center = self.viewport().rect().center()
        self.hud.setPos(self.mapToScene(view_center) - QPointF(150, 50))
        self.hud.setVisible(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            fake_event = QMouseEvent(QEvent.Type.MouseButtonPress, event.position(), 
                                     Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, event.modifiers())
            super().mousePressEvent(fake_event)
            return

        # Buscar el equipo bajo el cursor
        from app.graphics.items import BaseEquipment, SmartLine, FlowDot
        item = None
        # Probar con itemsAt para ignorar la línea temporal
        items_at_pos = self.items(event.pos())
        for it in items_at_pos:
            candidate = it
            while candidate and not isinstance(candidate, BaseEquipment):
                candidate = candidate.parentItem()
            if candidate:
                item = candidate
                break
            
        # Actualizar Inspector
        if isinstance(item, BaseEquipment):
            self.window().inspector.update_from_item(item)
        elif not item and not self.connection_mode:
            self.window().inspector.type_label.setText("Canvas")

        if self.connection_mode:
            if isinstance(item, BaseEquipment):
                if not self.first_comp:
                    self.first_comp = item
                    item.setPen(QPen(QColor("#38bdf8"), 3, Qt.PenStyle.DashLine))
                    # Crear línea temporal
                    from PyQt6.QtWidgets import QGraphicsLineItem
                    self.temp_line = QGraphicsLineItem()
                    self.temp_line.setPen(QPen(QColor("#38bdf8"), 2, Qt.PenStyle.DashLine))
                    # NO aceptar eventos de ratón para no bloquear clicks futuros
                    self.temp_line.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
                    self.scene.addItem(self.temp_line)
                    return
                elif item != self.first_comp:
                    # Finalizar conexión
                    line = SmartLine(self.first_comp, item)
                    self.scene.addItem(line)
                    self.first_comp.connections.append(line)
                    item.connections.append(line)
                    
                    # Añadir puntos de flujo
                    for i in range(3):
                        dot = FlowDot(line)
                        dot.progress = i * 0.33
                        line.dots.append(dot)
                        self.scene.addItem(dot)
                    
                    self.finish_connection()
                    return
            elif self.first_comp:
                # Si ya teníamos el primero y pinchamos fuera, cancelar
                self.cancel_connection()
                return

        super().mousePressEvent(event)

    def finish_connection(self):
        """Limpia todo tras una conexión exitosa"""
        if self.first_comp:
            self.first_comp.setPen(QPen(QColor("#f8fafc"), 1))
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        self.connection_mode = False
        self.first_comp = None
        self.hud.setVisible(False)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setBackgroundBrush(QBrush(QColor("#020617")))
        self.window().on_connection_finished()

    def cancel_connection(self):
        """Cancela el modo de conexión"""
        if self.first_comp:
            self.first_comp.setPen(QPen(QColor("#f8fafc"), 1))
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        self.connection_mode = False
        self.first_comp = None
        self.hud.setVisible(False)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setBackgroundBrush(QBrush(QColor("#020617")))
        self.window().status.showMessage("❌ Conexión cancelada", 2000)
        # Notificar también a la ventana para desmarcar botón
        if hasattr(self.window(), 'btn_conn'):
            self.window().btn_conn.setChecked(False)

    def mouseMoveEvent(self, event):
        if self.connection_mode and self.first_comp and self.temp_line:
            p1 = self.first_comp.scenePos() + QPointF(35, 25)
            p2 = self.mapToScene(event.pos())
            self.temp_line.setLine(p1.x(), p1.y(), p2.x(), p2.y())
        super().mouseMoveEvent(event)

    def delete_selected(self):
        items = self.scene.selectedItems()
        for item in items:
            # Eliminar conexiones primero
            if hasattr(item, 'connections'):
                for conn in item.connections[:]:
                    # Eliminar dots
                    for dot in conn.dots:
                        self.scene.removeItem(dot)
                    self.scene.removeItem(conn)
                    # Quitar de la lista del otro extremo
                    other = conn.target if conn.source == item else conn.source
                    if conn in other.connections:
                        other.connections.remove(conn)
                    item.connections.remove(conn)
            self.scene.removeItem(item)
        self.window().status.showMessage(f"🗑️ Eliminados {len(items)} elementos")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoom_in = 1.15
        zoom_out = 1 / zoom_in
        if event.angleDelta().y() > 0:
            self.scale(zoom_in, zoom_in)
        else:
            self.scale(zoom_out, zoom_out)

    def center_on_items(self):
        rect = self.scene.itemsBoundingRect()
        if not rect.isEmpty():
            self.centerOn(rect.center())
            if rect.width() > self.width() or rect.height() > self.height():
                self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            self.delete_selected()
        super().keyPressEvent(event)
