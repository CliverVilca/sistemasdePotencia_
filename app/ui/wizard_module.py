"""
wizard_module.py
Base de todos los módulos asistidos paso a paso.
Cada módulo hereda de ModuleWizard y define sus propios pasos.
"""
import os, datetime
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QFrame, QTextEdit, QStackedWidget,
    QGroupBox, QProgressBar, QFileDialog, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont


# ─── helpers ──────────────────────────────────────────────────────────────────
def _lbl(txt, color="#94a3b8", bold=False, size=12):
    l = QLabel(txt); l.setWordWrap(True)
    l.setStyleSheet(f"color:{color};font-size:{size}px;font-weight:{'800' if bold else '400'};")
    return l

def _field(default=""):
    e = QLineEdit(default)
    e.setStyleSheet("background:#1e293b;color:#f8fafc;border:1px solid #334155;"
                    "padding:7px;border-radius:4px;font-family:Consolas;font-size:12px;")
    return e

def _box(title, color="#38bdf8"):
    b = QGroupBox(title)
    b.setStyleSheet(f"QGroupBox{{color:{color};font-weight:bold;font-size:13px;"
                    f"border:1px solid #1e293b;border-radius:8px;margin-top:10px;padding-top:8px;}}"
                    f"QGroupBox::title{{subcontrol-origin:margin;padding:0 4px;}}")
    return b

def _result_box():
    t = QTextEdit(); t.setReadOnly(True)
    t.setStyleSheet("background:#020617;color:#10b981;font-family:Consolas;font-size:12px;"
                    "border:1px solid #334155;border-radius:4px;")
    t.setMinimumHeight(130)
    return t

def _sep():
    f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("background:#1e293b;color:#1e293b;"); return f


# ─── PDF generator ─────────────────────────────────────────────────────────────
def generate_pdf(filename: str, module_name: str, steps_data: list[dict]):
    """
    steps_data = [{"title": str, "inputs": {key: value}, "result": str}, ...]
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable)

    doc = SimpleDocTemplate(filename, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Portada
    title_style = ParagraphStyle('T', fontSize=20, textColor=colors.HexColor('#1e3a5f'),
                                  spaceAfter=6, fontName='Helvetica-Bold', alignment=1)
    sub_style   = ParagraphStyle('S', fontSize=11, textColor=colors.HexColor('#475569'),
                                  spaceAfter=4, alignment=1)
    body_style  = ParagraphStyle('B', fontSize=10, textColor=colors.HexColor('#1e293b'),
                                  spaceAfter=4, leading=16)
    code_style  = ParagraphStyle('C', fontSize=9, fontName='Courier',
                                  textColor=colors.HexColor('#0f4c2a'),
                                  backColor=colors.HexColor('#f0fdf4'),
                                  spaceAfter=3, leading=14, leftIndent=12, rightIndent=12)
    head_style  = ParagraphStyle('H', fontSize=13, fontName='Helvetica-Bold',
                                  textColor=colors.HexColor('#1e3a5f'), spaceBefore=12, spaceAfter=4)

    story.append(Paragraph("⚡ POWER ANALYZER PRO", title_style))
    story.append(Paragraph("Análisis de Sistemas de Potencia", sub_style))
    story.append(Paragraph("Basado en: Pumacayo C. & Romero L. — Teoría y Problemas Resueltos", sub_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#38bdf8')))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"MÓDULO: {module_name.upper()}", title_style))
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"Fecha de análisis: {now}", sub_style))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1')))
    story.append(Spacer(1, 10))

    for i, step in enumerate(steps_data):
        story.append(Paragraph(f"PASO {i+1}: {step['title']}", head_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
        story.append(Spacer(1, 4))

        # Tabla de datos de entrada
        if step.get("inputs"):
            t_data = [["Parámetro", "Valor"]] + [[k, str(v)] for k, v in step["inputs"].items()]
            t = Table(t_data, colWidths=[8*cm, 7*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a5f')),
                ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
                ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0), (-1,-1), 9),
                ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#cbd5e1')),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.HexColor('#f1f5f9')]),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t); story.append(Spacer(1, 8))

        # Resultado/Desarrollo
        if step.get("result"):
            for line in step["result"].split('\n'):
                if line.strip():
                    story.append(Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), code_style))

        story.append(Spacer(1, 10))

    # Conclusión
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#38bdf8')))
    story.append(Spacer(1, 8))
    story.append(Paragraph("CONCLUSIÓN DEL ANÁLISIS", head_style))
    story.append(Paragraph(
        f"El análisis del módulo <b>{module_name}</b> ha sido completado satisfactoriamente "
        f"siguiendo la metodología del libro de Análisis de Sistemas de Potencia de Pumacayo & Romero. "
        f"Todos los resultados han sido calculados paso a paso con las fórmulas del libro de referencia.",
        body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("— Generado por Power Analyzer PRO v10.0 | Pumacayo & Romero —", sub_style))

    doc.build(story)


# ─── Clase base Wizard ─────────────────────────────────────────────────────────
class ModuleWizard(QWidget):
    """
    Asistente guiado paso a paso para un módulo de análisis.
    Las subclases definen self.steps_config = [ {title, description, build_fn, calc_fn}, ...]
    """
    MODULE_NAME = "Módulo"
    MODULE_COLOR = "#38bdf8"

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#020617;")
        self.steps_data   = []   # datos acumulados para PDF
        self.step_results = {}   # resultados intermedios para pasar entre pasos
        self.current_step = 0
        self._build_steps()      # subclase define self.step_widgets[]
        self._build_ui()

    def _build_steps(self):
        """Subclase debe poblar self.step_widgets (list of QWidget) y self.step_titles."""
        self.step_widgets = []
        self.step_titles  = []

    def _build_ui(self):
        root = QVBoxLayout(self); root.setSpacing(0); root.setContentsMargins(0,0,0,0)

        # ── Header premium del módulo ──────────────────────────────────────────
        hdr = QFrame(); hdr.setFixedHeight(68)
        hdr.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {self.MODULE_COLOR}28,stop:0.6 {self.MODULE_COLOR}0a,stop:1 #020617);"
            f"border-bottom:2px solid {self.MODULE_COLOR}55;"
        )
        hlay = QHBoxLayout(hdr); hlay.setContentsMargins(16,0,20,0); hlay.setSpacing(14)

        # Ícono hexagonal
        icon_frame = QFrame()
        icon_frame.setFixedSize(42, 42)
        icon_frame.setStyleSheet(
            f"background:{self.MODULE_COLOR}22; border:2px solid {self.MODULE_COLOR}66;"
            f"border-radius:8px;"
        )
        icon_lay = QHBoxLayout(icon_frame); icon_lay.setContentsMargins(0,0,0,0)
        icon_lbl = QLabel("⚡")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"color:{self.MODULE_COLOR}; font-size:20px; border:none; background:transparent;")
        icon_lay.addWidget(icon_lbl)
        hlay.addWidget(icon_frame)

        # Texto del módulo
        txt_block = QWidget(); txt_block.setStyleSheet("background:transparent;")
        tb_lay = QVBoxLayout(txt_block); tb_lay.setSpacing(1); tb_lay.setContentsMargins(0,0,0,0)
        self.title_lbl = QLabel(f"{self.MODULE_NAME}")
        self.title_lbl.setStyleSheet(
            f"color:{self.MODULE_COLOR}; font-size:16px; font-weight:900; letter-spacing:-0.5px;"
        )
        sub_lbl = QLabel("Análisis paso a paso — Pumacayo & Romero")
        sub_lbl.setStyleSheet("color:#475569; font-size:10px; font-weight:600; letter-spacing:0.5px;")
        tb_lay.addWidget(self.title_lbl)
        tb_lay.addWidget(sub_lbl)
        hlay.addWidget(txt_block, stretch=1)

        # Contador de paso (derecha)
        self.step_counter = QLabel("")
        self.step_counter.setStyleSheet(
            f"color:{self.MODULE_COLOR}; font-size:13px; font-weight:900;"
            f"background:{self.MODULE_COLOR}18; border:1px solid {self.MODULE_COLOR}44;"
            f"border-radius:8px; padding:4px 14px; font-family:Consolas;"
        )
        hlay.addWidget(self.step_counter)
        root.addWidget(hdr)

        # ── Barra de progreso premium ──────────────────────────────────────────
        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setStyleSheet(
            f"QProgressBar{{background:#0a1628;border:none;}}"
            f"QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {self.MODULE_COLOR},stop:1 {self.MODULE_COLOR}88);}}"
        )
        self.progress.setTextVisible(False)
        root.addWidget(self.progress)

        # ── Contenido (stacked) ────────────────────────────────────────────────
        self.stack = QStackedWidget()
        for w in self.step_widgets:
            scroll = QScrollArea(); scroll.setWidget(w); scroll.setWidgetResizable(True)
            scroll.setStyleSheet(
                "QScrollArea{border:none;background:#020617;}"
                "QScrollBar:vertical{background:#0a1628;width:8px;border-radius:4px;}"
                "QScrollBar::handle:vertical{background:#1e3a5f;border-radius:4px;}"
                "QScrollBar::handle:vertical:hover{background:#334155;}"
            )
            self.stack.addWidget(scroll)

        # Pantalla final
        self.stack.addWidget(self._build_final_screen())
        root.addWidget(self.stack, stretch=1)

        # ── Barra de navegación premium ────────────────────────────────────────
        nav = QFrame(); nav.setFixedHeight(64)
        nav.setStyleSheet(
            "background:#050e1e; border-top:1px solid #1e293b;"
        )
        nlay = QHBoxLayout(nav); nlay.setContentsMargins(20,8,20,8); nlay.setSpacing(12)

        self.btn_prev = QPushButton("← ANTERIOR")
        self.btn_prev.setStyleSheet(
            "background:#0f172a; color:#64748b; border:1px solid #1e293b;"
            "border-radius:8px; padding:10px 20px; font-weight:700; font-size:11px;"
            "letter-spacing:0.5px;"
        )
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.clicked.connect(self.prev_step)
        nlay.addWidget(self.btn_prev)

        nlay.addStretch()
        self.step_dots = QLabel(""); nlay.addWidget(self.step_dots)
        nlay.addStretch()

        self.btn_next = QPushButton("SIGUIENTE →")
        self.btn_next.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {self.MODULE_COLOR},stop:1 {self.MODULE_COLOR}bb);"
            f"color:#020617; border-radius:8px; padding:10px 26px;"
            f"font-weight:900; font-size:12px; letter-spacing:1px; border:none;"
        )
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.clicked.connect(self.next_step)
        nlay.addWidget(self.btn_next)
        root.addWidget(nav)

        self._update_nav()

    def _build_final_screen(self):
        w = QWidget(); w.setStyleSheet("background:#020617;")
        lay = QVBoxLayout(w); lay.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.setSpacing(16)
        lay.addStretch()

        # Ícono grande
        ico = QLabel("✅"); ico.setStyleSheet("font-size:72px;"); ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(ico)

        # Título
        title = QLabel("¡Análisis Completado!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color:{self.MODULE_COLOR}; font-size:24px; font-weight:900; letter-spacing:-0.5px;")
        lay.addWidget(title)

        # Subtítulo
        sub = QLabel(f"Todos los pasos del módulo  {self.MODULE_NAME.upper()}  han sido procesados exitosamente.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color:#64748b; font-size:13px; font-weight:500;")
        sub.setWordWrap(True)
        lay.addWidget(sub)

        # Separator
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{self.MODULE_COLOR}33; max-height:1px; margin:8px 60px;")
        lay.addWidget(sep)

        # Info chips
        chips_row = QHBoxLayout(); chips_row.setSpacing(12); chips_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for icon, lbl in [("📐","Fórmulas verificadas"),("📋","Datos registrados"),("📊","Gráficas disponibles")]:
            chip = QFrame()
            chip.setStyleSheet(f"background:{self.MODULE_COLOR}12; border:1px solid {self.MODULE_COLOR}33;"
                               f"border-radius:10px; padding:6px 14px;")
            ch_lay = QHBoxLayout(chip); ch_lay.setContentsMargins(8,4,8,4)
            ch_lay.addWidget(QLabel(icon))
            cl = QLabel(lbl)
            cl.setStyleSheet(f"color:{self.MODULE_COLOR}; font-size:11px; font-weight:700;")
            ch_lay.addWidget(cl)
            chips_row.addWidget(chip)
        lay.addLayout(chips_row)

        lay.addSpacing(16)

        # Botón PDF
        btn_pdf = QPushButton("  📄   GENERAR REPORTE PDF")
        btn_pdf.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {self.MODULE_COLOR},stop:1 {self.MODULE_COLOR}bb);"
            f"color:#020617; border-radius:10px; padding:14px 40px;"
            f"font-weight:900; font-size:15px; letter-spacing:1.5px; border:none;"
        )
        btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pdf.clicked.connect(self.export_pdf)
        lay.addWidget(btn_pdf, alignment=Qt.AlignmentFlag.AlignCenter)

        lay.addStretch()
        return w

    def _update_nav(self):
        n = len(self.step_widgets)
        on_final = self.current_step >= n
        self.btn_prev.setEnabled(self.current_step > 0)

        # Estilo del botón anterior
        if self.current_step > 0:
            self.btn_prev.setStyleSheet(
                "background:#0f172a; color:#94a3b8; border:1px solid #334155;"
                "border-radius:8px; padding:10px 20px; font-weight:700; font-size:11px;"
                "letter-spacing:0.5px;"
            )
        else:
            self.btn_prev.setStyleSheet(
                "background:#0a1020; color:#2d3748; border:1px solid #1a2535;"
                "border-radius:8px; padding:10px 20px; font-weight:700; font-size:11px;"
            )

        if on_final:
            self.btn_next.setVisible(False)
        else:
            self.btn_next.setVisible(True)
            last = self.current_step == n - 1
            if last:
                self.btn_next.setText("  ✅  FINALIZAR")
                self.btn_next.setStyleSheet(
                    "background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #10b981,stop:1 #059669);"
                    "color:#020617; border-radius:8px; padding:10px 26px;"
                    "font-weight:900; font-size:12px; letter-spacing:1px; border:none;"
                )
            else:
                self.btn_next.setText("SIGUIENTE →")
                self.btn_next.setStyleSheet(
                    f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {self.MODULE_COLOR},stop:1 {self.MODULE_COLOR}bb);"
                    f"color:#020617; border-radius:8px; padding:10px 26px;"
                    f"font-weight:900; font-size:12px; letter-spacing:1px; border:none;"
                )

        prog = int((self.current_step / max(n, 1)) * 100)
        self.progress.setValue(prog)
        self.step_counter.setText(f"Paso {min(self.current_step+1, n)} / {n}")

        # Dots con número
        dots = ""
        for i in range(n + 1):
            if i == self.current_step:
                dots += f"<span style='color:{self.MODULE_COLOR};font-size:17px;font-weight:900;'>●</span> "
            elif i < self.current_step:
                dots += f"<span style='color:{self.MODULE_COLOR}66;font-size:13px;'>●</span> "
            else:
                dots += "<span style='color:#1e293b;font-size:13px;'>●</span> "
        self.step_dots.setText(dots)

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.stack.setCurrentIndex(self.current_step)
            self._update_nav()

    def next_step(self):
        n = len(self.step_widgets)
        if self.current_step < n:
            self.current_step += 1
            self.stack.setCurrentIndex(self.current_step)
            self._update_nav()

    def record_step(self, title, inputs: dict, result: str):
        """Guardar datos del paso actual para el reporte PDF."""
        # Actualizar o agregar
        idx = self.current_step
        entry = {"title": title, "inputs": inputs, "result": result}
        if idx < len(self.steps_data):
            self.steps_data[idx] = entry
        else:
            while len(self.steps_data) < idx:
                self.steps_data.append({})
            self.steps_data.append(entry)

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte PDF Detallado",
            f"Reporte_{self.MODULE_NAME.replace(' ','_')}.pdf",
            "PDF Files (*.pdf)")
        if not path:
            return
        try:
            # Recolectar datos de todos los pasos (de los widgets)
            steps_data = []
            for i, w in enumerate(self.step_widgets):
                title = self.step_titles[i] if i < len(self.step_titles) else f"Paso {i+1}"
                sd = getattr(w, "_step_data", {})
                steps_data.append({
                    "title": title,
                    "inputs": sd.get("inputs", {}),
                    "result": sd.get("result", "")
                })
            from app.ui.pdf_report import generate_detailed_pdf
            generate_detailed_pdf(path, self.MODULE_NAME, steps_data)
            QMessageBox.information(self, "✅ Reporte Generado",
                f"Reporte PDF detallado guardado:\n{path}\n\n"
                "Incluye: marco teórico, fórmulas, desarrollo matemático, "
                "gráficas y circuitos.")
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Error al generar PDF", f"{e}")
