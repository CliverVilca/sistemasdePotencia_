"""9 módulos wizard paso a paso - Pumacayo & Romero"""
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from app.ui.wizard_module import ModuleWizard, _lbl, _field, _box, _result_box, _sep
import app.ui.plots as P


def _render_result_html(txt: str, accent: str = "#10b981") -> str:
    """
    Convierte la salida de texto plano de los helpers calc_* en HTML rico
    con colorizacion semantica de secciones, formulas y resultados.
    """
    import re, html as _h

    # Colores del tema
    C_SECTION  = accent          # cabeceras ━━ ... ━━
    C_FORMULA  = "#38bdf8"       # lineas con = o formulas
    C_RESULT   = "#a3e635"       # resultados clave |VS|, RV%, etc.
    C_NUM      = "#fbbf24"       # numeros y valores calculados
    C_WARN     = "#fb923c"       # advertencias, NEGATIVA, ATENCION
    C_CONCLUDE = "#c084fc"       # conclusiones [1] [2] ...
    C_DIM      = "#475569"       # separadores ─────
    C_LABEL    = "#64748b"       # etiquetas Za, VR, IR
    BG_SECTION = "#0a1f14"
    BG_FORMULA = "#071524"

    lines = txt.split("\n")
    html_parts = [
        "<div style='font-family:Consolas,monospace; font-size:12px; "
        "line-height:1.75; padding:4px 0;'>"
    ]

    for raw in lines:
        line = _h.escape(raw)  # escape HTML special chars
        stripped = raw.strip()

        if not stripped:
            html_parts.append("<br/>")
            continue

        # ── Cabeceras de seccion ━━ TITULO ━━ ────────────────────────────
        if stripped.startswith(("━━", "══")):
            # Quitar los caracteres de borde, dejar el texto
            inner = stripped.strip("━═ \t")
            html_parts.append(
                f"<div style='background:{BG_SECTION}; border-left:3px solid {C_SECTION}; "
                f"border-radius:4px; padding:3px 10px; margin:4px 0; "
                f"color:{C_SECTION}; font-weight:900; font-size:11px; "
                f"letter-spacing:0.8px;'>{inner or '&nbsp;'}</div>"
            )
            continue

        # ── Separadores de tabla ──────────────────────────────────────────
        if stripped.startswith(("─", "─────", "═", "━")):
            html_parts.append(
                f"<hr style='border:none; border-top:1px solid #1e293b; margin:2px 0;'/>"
            )
            continue

        # ── Conclusiones [1], [2], ... ────────────────────────────────────
        if re.match(r"^\[\d+\]", stripped):
            html_parts.append(
                f"<div style='color:{C_CONCLUDE}; padding-left:8px; margin:1px 0;'>{line}</div>"
            )
            continue

        # ── Advertencias / alertas ────────────────────────────────────────
        if any(w in stripped.upper() for w in ("NEGATIVA", "ATENCION", "⚠", "CUIDADO", "ALERT")):
            html_parts.append(
                f"<div style='color:{C_WARN}; font-weight:700; padding-left:4px;'>{line}</div>"
            )
            continue

        # ── Lineas de tabla de resultados (columnas alineadas) ─────────────
        if re.match(r"^(A|B|C)\s+0\.", stripped) or (stripped.count("   ") >= 2 and re.search(r"\d+\.\d+", stripped)):
            # Resalta los numeros en amarillo
            highlighted = re.sub(
                r"(-?\d+\.\d+)",
                rf"<span style='color:{C_NUM}; font-weight:700;'>\1</span>",
                line
            )
            html_parts.append(
                f"<div style='background:#07121e; padding:1px 8px; "
                f"border-radius:2px; color:#94a3b8;'>{highlighted}</div>"
            )
            continue

        # ── Lineas con signo = (formulas/calculos) ─────────────────────────
        if "=" in stripped and len(stripped) > 4:
            # subrayar partes a la derecha del ultimo =
            # Numeros en amarillo, resto en cyan
            highlighted = re.sub(
                r"(-?\d+\.\d+(?:[eE][+-]?\d+)?)",
                rf"<span style='color:{C_NUM}; font-weight:800;'>\1</span>",
                line
            )
            # Simbolos matematicos en accent
            highlighted = re.sub(
                r"([∠∡√×÷±≈≤≥⟹⇒→←])",
                rf"<span style='color:{C_SECTION}; font-weight:700;'>\1</span>",
                highlighted
            )
            is_result = any(kw in stripped for kw in ("|VS|", "|VR|", "RV%", "Efici", "Ploss", "Perdidas", "eta", "PR =", "PS =", "QR =", "SR ="))
            row_color = C_RESULT if is_result else C_FORMULA
            row_bg    = "#071c0e" if is_result else BG_FORMULA
            html_parts.append(
                f"<div style='background:{row_bg}; color:{row_color}; "
                f"padding:2px 8px; border-radius:3px; margin:1px 0;'>{highlighted}</div>"
            )
            continue

        # ── Lineas que contienen resultado clave ──────────────────────────
        if any(kw in stripped for kw in ("kV L-L", "kV L-N", "V L-N", " MW", " MVAR", " MVA", " A ", "% ", "deg", "Ohm", "Ω")):
            highlighted = re.sub(
                r"(-?\d+\.\d+(?:[eE][+-]?\d+)?)",
                rf"<span style='color:{C_NUM}; font-weight:800;'>\1</span>",
                line
            )
            html_parts.append(
                f"<div style='color:{C_RESULT}; padding:1px 6px;'>{highlighted}</div>"
            )
            continue

        # ── Lineas normales ────────────────────────────────────────────────
        highlighted = re.sub(
            r"(-?\d+\.\d+)",
            rf"<span style='color:{C_NUM};'>\1</span>",
            line
        )
        html_parts.append(
            f"<div style='color:#94a3b8; padding:0 4px;'>{highlighted}</div>"
        )

    html_parts.append("</div>")
    return "".join(html_parts)


def _step_widget(schema_txt, desc_txt, fields_def, calc_fn, color="#38bdf8", plot_fn=None):
    """
    Widget de paso premium - layout 2 columnas: izquierda inputs, derecha resultados.
    calc_fn(vals) -> (inputs_dict, result_str)
    plot_fn(vals) -> None  [opcional]
    """
    from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
    from PyQt6.QtGui  import QColor

    # ── Contenedor raíz ───────────────────────────────────────────────────────
    w = QWidget()
    w.setStyleSheet("background:#020617;")
    root = QVBoxLayout(w)
    root.setSpacing(0)
    root.setContentsMargins(0, 0, 0, 0)

    # ── HEADER BANNER (banda de color con título del esquema) ─────────────────
    header = QFrame()
    header.setFixedHeight(38)
    header.setStyleSheet(
        f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        f"stop:0 {color}22, stop:0.5 {color}11, stop:1 #020617);"
        f"border-bottom: 2px solid {color}55;"
        f"border-top: 1px solid {color}33;"
    )
    h_lay = QHBoxLayout(header)
    h_lay.setContentsMargins(14, 0, 14, 0)
    dot = QLabel("⬡")
    dot.setStyleSheet(f"color:{color}; font-size:18px; font-weight:900;")
    h_lay.addWidget(dot)
    desc_header = QLabel(desc_txt[:100] + ("…" if len(desc_txt) > 100 else ""))
    desc_header.setStyleSheet(f"color:{color}; font-size:11px; font-weight:700; letter-spacing:0.3px;")
    h_lay.addWidget(desc_header, stretch=1)
    # Badge estado
    status_badge = QLabel("○ EN ESPERA")
    status_badge.setStyleSheet(
        "color:#64748b; font-size:10px; font-weight:800; "
        "background:#0f172a; border:1px solid #334155; "
        "border-radius:10px; padding:2px 10px; letter-spacing:0.5px;"
    )
    h_lay.addWidget(status_badge)
    root.addWidget(header)

    # ── CUERPO: 2 columnas ────────────────────────────────────────────────────
    body = QWidget()
    body.setStyleSheet("background:#020617;")
    body_lay = QHBoxLayout(body)
    body_lay.setSpacing(0)
    body_lay.setContentsMargins(0, 0, 0, 0)

    # ── COLUMNA IZQUIERDA (esquema + inputs) ───────────────────────────────
    left_panel = QWidget()
    left_panel.setStyleSheet("background:#020617;")
    left_panel.setMaximumWidth(420)
    left_panel.setMinimumWidth(320)
    left_lay = QVBoxLayout(left_panel)
    left_lay.setSpacing(8)
    left_lay.setContentsMargins(14, 10, 8, 10)

    # Esquema ASCII — caja con borde luminoso
    schema_frame = QFrame()
    schema_frame.setStyleSheet(
        f"background:#050e1e; border:1px solid {color}40; "
        f"border-radius:8px; border-left: 3px solid {color};"
    )
    sf_lay = QVBoxLayout(schema_frame)
    sf_lay.setContentsMargins(8, 6, 8, 6)
    sf_lay.setSpacing(0)
    schema_lbl = QLabel("CIRCUITO / FÓRMULA")
    schema_lbl.setStyleSheet(
        f"color:{color}88; font-size:9px; font-weight:900; "
        "letter-spacing:1.5px; text-transform:uppercase;"
    )
    sf_lay.addWidget(schema_lbl)
    schema = QTextEdit()
    schema.setReadOnly(True)
    schema.setPlainText(schema_txt)
    schema.setStyleSheet(
        f"background:transparent; color:{color}; font-family:Consolas; "
        "font-size:12px; border:none; selection-background-color:#334155;"
    )
    schema.setMaximumHeight(110)
    schema.setMinimumHeight(80)
    sf_lay.addWidget(schema)
    left_lay.addWidget(schema_frame)

    # Sección de campos con título
    fields_header = QLabel("▸  DATOS DE ENTRADA")
    fields_header.setStyleSheet(
        f"color:{color}; font-size:10px; font-weight:900; "
        "letter-spacing:1px; margin-top:4px; margin-bottom:2px;"
    )
    left_lay.addWidget(fields_header)

    fields = {}
    scroll_fields = QScrollArea()
    scroll_fields.setWidgetResizable(True)
    scroll_fields.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll_fields.setStyleSheet(
        "QScrollArea{background:#020617; border:none;}"
        "QScrollBar:vertical{background:#0f172a; width:6px; border-radius:3px;}"
        "QScrollBar::handle:vertical{background:#334155; border-radius:3px;}"
    )
    fields_widget = QWidget()
    fields_widget.setStyleSheet("background:#020617;")
    form_lay = QFormLayout(fields_widget)
    form_lay.setSpacing(6)
    form_lay.setContentsMargins(0, 0, 0, 0)
    form_lay.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

    for name, lbl_txt, default in fields_def:
        lbl_w = QLabel(lbl_txt)
        lbl_w.setStyleSheet(
            "color:#94a3b8; font-size:10.5px; font-weight:600; "
            "padding-right:6px;"
        )
        lbl_w.setWordWrap(True)
        e = QLineEdit(default)
        e.setStyleSheet(
            f"background:#0d1b2e; color:#e2e8f0; "
            f"border:1px solid #1e3a5f; border-radius:5px; "
            f"padding:6px 8px; font-family:Consolas; font-size:12px; "
            f"selection-background-color:{color}55;"
        )
        e.setPlaceholderText(default)
        # Focus style via dynamic property
        e.setFixedHeight(30)
        fields[name] = e
        form_lay.addRow(lbl_w, e)

    scroll_fields.setWidget(fields_widget)
    scroll_fields.setMinimumHeight(min(len(fields_def) * 42 + 10, 250))
    scroll_fields.setMaximumHeight(280)
    left_lay.addWidget(scroll_fields)

    # Botones
    btn_lay = QHBoxLayout()
    btn_lay.setSpacing(8)
    btn_calc = QPushButton("  ⚡  CALCULAR")
    btn_calc.setStyleSheet(
        f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {color},stop:1 {color}bb);"
        f"color:#020617; font-weight:900; font-size:12px; letter-spacing:1px;"
        f"padding:9px 18px; border-radius:7px; border:none;"
        f"text-align:left;"
    )
    btn_calc.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_lay.addWidget(btn_calc)

    last_vals = {}

    if plot_fn:
        btn_plot = QPushButton("📊 GRAFICAR")
        btn_plot.setStyleSheet(
            f"background:#0f172a; color:{color}; border:1.5px solid {color}; "
            f"font-weight:800; font-size:11px; padding:9px 14px; "
            f"border-radius:7px; letter-spacing:0.5px;"
        )
        btn_plot.setEnabled(False)
        btn_plot.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_lay.addWidget(btn_plot)

    left_lay.addLayout(btn_lay)
    left_lay.addStretch()
    body_lay.addWidget(left_panel)

    # ── DIVISOR VERTICAL ──────────────────────────────────────────────────
    divider = QFrame()
    divider.setFrameShape(QFrame.Shape.VLine)
    divider.setStyleSheet(f"background:{color}25; color:{color}25; max-width:2px;")
    body_lay.addWidget(divider)

    # ── COLUMNA DERECHA (resultados) ───────────────────────────────────────
    right_panel = QWidget()
    right_panel.setStyleSheet("background:#020617;")
    right_lay = QVBoxLayout(right_panel)
    right_lay.setSpacing(6)
    right_lay.setContentsMargins(10, 10, 14, 10)

    res_header = QLabel("▸  DESARROLLO Y RESULTADOS")
    res_header.setStyleSheet(
        "color:#10b981; font-size:10px; font-weight:900; "
        "letter-spacing:1px; margin-bottom:2px;"
    )
    right_lay.addWidget(res_header)

    res = QTextEdit()
    res.setReadOnly(True)
    res.setStyleSheet(
        "background:#050e1e; color:#10b981; font-family:Consolas; font-size:12px;"
        "border:1px solid #0d3321; border-radius:8px; border-left:3px solid #10b981;"
        "padding:10px; line-height:1.6; selection-background-color:#1e3a5f;"
    )
    res.setPlaceholderText(
        "⚡ Ingresa los datos y presiona CALCULAR para ver el desarrollo\n"
        "matemático paso a paso con todas las fórmulas..."
    )
    right_lay.addWidget(res, stretch=1)

    # Mini-barra de indicadores abajo del resultado
    kpi_bar = QFrame()
    kpi_bar.setFixedHeight(32)
    kpi_bar.setStyleSheet(
        "background:#050e1e; border:1px solid #0f172a; "
        "border-radius:6px; margin-top:2px;"
    )
    kpi_lay = QHBoxLayout(kpi_bar)
    kpi_lay.setContentsMargins(10, 0, 10, 0)
    kpi_lay.setSpacing(20)
    kpi_time  = QLabel("⏱ —")
    kpi_lines = QLabel("≡ —")
    kpi_ok    = QLabel("✓ —")
    for kl in (kpi_time, kpi_lines, kpi_ok):
        kl.setStyleSheet("color:#334155; font-size:10px; font-weight:700; font-family:Consolas;")
        kpi_lay.addWidget(kl)
    kpi_lay.addStretch()
    right_lay.addWidget(kpi_bar)

    body_lay.addWidget(right_panel, stretch=1)
    root.addWidget(body, stretch=1)

    step_data = {"inputs": {}, "result": ""}

    # ── Lógica de cálculo ─────────────────────────────────────────────────
    import time
    def on_calc():
        t0 = time.perf_counter()
        try:
            vals = {k: float(v.text()) for k, v in fields.items()}
            last_vals.clear(); last_vals.update(vals)
            inp, txt = calc_fn(vals)
            res.setHtml(_render_result_html(txt, accent=color))
            step_data["inputs"] = inp
            step_data["result"] = txt
            elapsed = (time.perf_counter() - t0) * 1000
            n_lines = txt.count("\n") + 1
            # Actualizar badge y KPIs
            status_badge.setText("✓  CALCULADO")
            status_badge.setStyleSheet(
                "color:#10b981; font-size:10px; font-weight:800; "
                "background:#0a2218; border:1px solid #10b981; "
                "border-radius:10px; padding:2px 10px; letter-spacing:0.5px;"
            )
            kpi_time.setText(f"⏱ {elapsed:.1f}ms")
            kpi_time.setStyleSheet("color:#38bdf8; font-size:10px; font-weight:700; font-family:Consolas;")
            kpi_lines.setText(f"≡ {n_lines} líneas")
            kpi_lines.setStyleSheet("color:#94a3b8; font-size:10px; font-weight:700; font-family:Consolas;")
            kpi_ok.setText("✓ OK")
            kpi_ok.setStyleSheet("color:#10b981; font-size:10px; font-weight:800; font-family:Consolas;")
            if plot_fn:
                btn_plot.setEnabled(True)
                btn_plot.setStyleSheet(
                    f"background:#0a2218; color:#10b981; border:1.5px solid #10b981; "
                    f"font-weight:800; font-size:11px; padding:9px 14px; "
                    f"border-radius:7px; letter-spacing:0.5px;"
                )
        except Exception as ex:
            res.setPlainText(f"❌ ERROR: {ex}\n\nVerifica que todos los campos tengan valores numéricos válidos.")
            status_badge.setText("✗  ERROR")
            status_badge.setStyleSheet(
                "color:#ef4444; font-size:10px; font-weight:800; "
                "background:#1a0606; border:1px solid #ef4444; "
                "border-radius:10px; padding:2px 10px; letter-spacing:0.5px;"
            )
            kpi_ok.setText("✗ ERROR")
            kpi_ok.setStyleSheet("color:#ef4444; font-size:10px; font-weight:800; font-family:Consolas;")

    btn_calc.clicked.connect(on_calc)
    if plot_fn:
        btn_plot.clicked.connect(lambda: plot_fn(last_vals))
    w._step_data = step_data
    return w


# ══════════════════════════════════════════════════════════════════
# TEMA 1 – Valores por Unidad
# ══════════════════════════════════════════════════════════════════
class WizardPerUnit(ModuleWizard):
    MODULE_NAME = "Valores por Unidad"
    MODULE_COLOR = "#38bdf8"

    def _build_steps(self):
        self.step_widgets = [
            _step_widget(
                "GEN ──Z1──|──Z2──|──Z3──  CARGA\n"
                "   Zona1(V1)  Trafo  Zona2(V2)  Trafo  Zona3(V3)\n"
                "Paso 1: Elegir bases del sistema",
                "Define las cantidades base para normalizar todo el sistema.",
                [("Sbase","Potencia base Sbase (MVA)","100"),
                 ("Vbase1","Voltaje base Zona1 (kV)","115"),
                 ("Vbase2","Voltaje base Zona2 (kV)","13.8"),
                 ("freq","Frecuencia (Hz)","60")],
                lambda v: (v, f"Bases definidas:\n  Sbase = {v['Sbase']} MVA\n"
                           f"  Vbase1 = {v['Vbase1']} kV\n  Vbase2 = {v['Vbase2']} kV\n"
                           f"  Ibase1 = {v['Sbase']*1e6/(np.sqrt(3)*v['Vbase1']*1e3):.2f} A\n"
                           f"  Ibase2 = {v['Sbase']*1e6/(np.sqrt(3)*v['Vbase2']*1e3):.2f} A\n"
                           f"  Zbase1 = {(v['Vbase1']*1e3)**2/(v['Sbase']*1e6):.4f} Ohm\n"
                           f"  Zbase2 = {(v['Vbase2']*1e3)**2/(v['Sbase']*1e6):.4f} Ohm"),
                "#38bdf8"),
            _step_widget(
                "Valor real  ──>  Valor p.u.\n"
                "  Vpu = V_real / Vbase\n"
                "  Zpu = Z_real / Zbase = Z_real * Sbase / Vbase^2",
                "Convierte impedancias y tensiones a valores por unidad.",
                [("Vreal","Tensión real a convertir V_real (kV)","115"),
                 ("Vbase","Vbase correspondiente (kV)","115"),
                 ("Zreal","Impedancia real Z_real (Ohm)","12.5"),
                 ("Sbase","Sbase (MVA)","100")],
                lambda v: (v,
                    f"[1] Vpu = {v['Vreal']}/{v['Vbase']} = {v['Vreal']/v['Vbase']:.4f} pu\n"
                    f"[2] Zbase = {v['Vbase']}^2/{v['Sbase']} x 1000 = "
                    f"{(v['Vbase']*1e3)**2/(v['Sbase']*1e6):.4f} Ohm\n"
                    f"[3] Zpu = {v['Zreal']} / {(v['Vbase']*1e3)**2/(v['Sbase']*1e6):.4f} = "
                    f"{v['Zreal']/((v['Vbase']*1e3)**2/(v['Sbase']*1e6)):.5f} pu"),
                "#38bdf8"),
            _step_widget(
                "BASE VIEJA  ──>  BASE NUEVA\n"
                "  Zpunew = Zpuold * (Sbase_new/Sbase_old) * (Vbase_old/Vbase_new)^2",
                "Cambia la base de referencia de una impedancia ya en p.u.",
                [("Zpuold","Zpu en base vieja (pu)","0.08"),
                 ("Sbold","Sbase_viejo (MVA)","50"),
                 ("Vbold","Vbase_viejo (kV)","115"),
                 ("Sbnew","Sbase_nuevo (MVA)","100"),
                 ("Vbnew","Vbase_nuevo (kV)","115")],
                lambda v: (v,
                    f"Zpunuevo = {v['Zpuold']} x ({v['Sbnew']}/{v['Sbold']}) x ({v['Vbold']}/{v['Vbnew']})^2\n"
                    f"Zpunuevo = {v['Zpuold'] * (v['Sbnew']/v['Sbold']) * (v['Vbold']/v['Vbnew'])**2:.6f} pu"),
                "#38bdf8"),
        ]
        self.step_titles = ["Definir Bases","Convertir a p.u.","Cambio de Base"]


# ══════════════════════════════════════════════════════════════════
# TEMA 2 – Inductancia
# ══════════════════════════════════════════════════════════════════
class WizardInductancia(ModuleWizard):
    MODULE_NAME = "Inductancia de Lineas"
    MODULE_COLOR = "#10b981"

    def _build_steps(self):
        def pfn_L(v):
            r=v['r']/100; GMD=(v['D12']*v['D23']*v['D31'])**(1/3)
            mu0=4*np.pi*1e-7; L=(mu0/(2*np.pi))*np.log(GMD/(r*np.exp(-0.25)))*1e3
            P.plot_inductancia(v['r'],v['D12'],v['D23'],v['D31'],L,2*np.pi*60*L/1e3*1000)
        self.step_widgets = [
            _step_widget(
                "    A           B           C\n"
                "    O           O           O\n"
                "    |<---D12--->|<---D23--->|\n"
                "    |<---------D31--------->|\n"
                "  radio = r  (r' = r*e^-0.25)",
                "Define la geometria transversal de la linea trifasica.",
                [("r","Radio del conductor r (cm)","1.5"),
                 ("D12","Distancia D12 (m)","2.0"),
                 ("D23","Distancia D23 (m)","2.5"),
                 ("D31","Distancia D31 (m)","4.5")],
                lambda v: (v,
                    f"r  = {v['r']} cm = {v['r']/100:.4f} m\n"
                    f"r' = r*e^(-1/4) = {v['r']/100*np.exp(-0.25)*100:.5f} cm\n"
                    f"GMD = {(v['D12']*v['D23']*v['D31'])**(1/3):.4f} m"),
                "#10b981", plot_fn=pfn_L),
            _step_widget(
                "L = (mu0 / 2*pi) * ln(GMD / r')\n"
                "  mu0 = 4*pi * 10^-7  H/m\n"
                "  r'  = r * e^(-1/4)  (radio reducido)",
                "Calcula la inductancia por fase y la reactancia inductiva.",
                [("r","Radio del conductor r (cm)","1.5"),
                 ("D12","D12 (m)","2.0"),("D23","D23 (m)","2.5"),("D31","D31 (m)","4.5"),
                 ("freq","Frecuencia (Hz)","60")],
                lambda v: (v, _calc_L(v)),
                "#10b981", plot_fn=pfn_L),
        ]
        self.step_titles = ["Geometria del Conductor","Calcular L y XL"]


def _calc_L(v):
    r=v['r']/100; rp=r*np.exp(-0.25); GMD=(v['D12']*v['D23']*v['D31'])**(1/3)
    L=2e-7*np.log(GMD/rp); XL=2*np.pi*v['freq']*L*1000
    return (f"r' = {rp*100:.5f} cm  GMD = {GMD:.4f} m\n"
            f"L  = 2x10^-7 * ln({GMD:.4f}/{rp:.6f})\n"
            f"L  = {L*1e6:.4f} uH/m  = {L*1e3:.5f} mH/km\n"
            f"XL = 2*pi*{v['freq']}*L = {XL:.5f} Ohm/km")


# ══════════════════════════════════════════════════════════════════
# TEMA 3 – Capacidad
# ══════════════════════════════════════════════════════════════════
class WizardCapacidad(ModuleWizard):
    MODULE_NAME = "Capacidad de Lineas"
    MODULE_COLOR = "#f59e0b"

    def _build_steps(self):
        self.step_widgets = [
            _step_widget(
                "    A     B     C\n"
                "    O-----O-----O\n"
                "Capacitancias de linea: Cab, Cbc, Cac\n"
                "C = 2*pi*eps0 / ln(GMD/r)",
                "Calcula la capacitancia y susceptancia capacitiva por fase.",
                [("r","Radio conductor r (cm)","1.5"),
                 ("D12","D12 (m)","2.0"),("D23","D23 (m)","2.5"),("D31","D31 (m)","4.5"),
                 ("freq","Frecuencia (Hz)","60")],
                lambda v: (v, _calc_C(v)),
                "#f59e0b"),
            _step_widget(
                "Potencia reactiva capacitiva:\n"
                "  QC = V^2 * BC   [VAR/m]\n"
                "  La linea GENERA MVAR (efecto Ferranti a carga ligera)",
                "Calcula la potencia reactiva generada por la capacitancia de la linea.",
                [("r","Radio conductor r (cm)","1.5"),
                 ("D12","D12 (m)","2.0"),("D23","D23 (m)","2.5"),("D31","D31 (m)","4.5"),
                 ("freq","Frecuencia (Hz)","60"),
                 ("VLN","Voltaje L-N (kV)","66.4"),
                 ("longitud","Longitud de la linea (km)","200")],
                lambda v: (v, _calc_QC(v)),
                "#f59e0b"),
        ]
        self.step_titles = ["Capacitancia y Susceptancia","Potencia Reactiva Generada"]


def _calc_C(v):
    r=v['r']/100; GMD=(v['D12']*v['D23']*v['D31'])**(1/3)
    C=2*np.pi*8.854e-12/np.log(GMD/r); BC=2*np.pi*v['freq']*C
    return (f"GMD = {GMD:.4f} m   r = {r*100:.2f} cm\n"
            f"C = 2*pi*8.854e-12 / ln({GMD:.4f}/{r:.4f})\n"
            f"C = {C*1e12:.4f} pF/m  = {C*1e9:.5f} nF/km\n"
            f"BC = 2*pi*{v['freq']}*C = {BC*1e6:.5f} uS/m  = {BC*1e3:.5f} mS/km")

def _calc_QC(v):
    r=v['r']/100; GMD=(v['D12']*v['D23']*v['D31'])**(1/3)
    C=2*np.pi*8.854e-12/np.log(GMD/r); BC=2*np.pi*v['freq']*C
    QC_m=((v['VLN']*1e3)**2)*BC; QC_total=QC_m*v['longitud']*1000/1e6
    return (f"BC por metro = {BC*1e6:.5f} uS/m\n"
            f"QC/m = V_LN^2 * BC = ({v['VLN']} kV)^2 * {BC:.4e}\n"
            f"QC/m = {QC_m:.4f} VAR/m\n"
            f"QC total ({v['longitud']} km) = {QC_total:.4f} MVAR (3 fases)")


# ══════════════════════════════════════════════════════════════════
# TEMA 4 – Lineas de Transmision
# ══════════════════════════════════════════════════════════════════
class WizardLineas(ModuleWizard):
    MODULE_NAME = "Lineas de Transmision"
    MODULE_COLOR = "#8b5cf6"

    def _build_steps(self):
        self.step_widgets = [
            # ── PASO 1: Hallar impedancias / Caso A (Inductivo, fp=0.9 atraso) ──
            _step_widget(
                "CASO A — CARGA INDUCTIVA (fp=0.9 atraso):\n"
                "  GEN ---[Za=R+jXL]--- CARGA\n"
                "  VS = VR + Za·IR    IR = |IR|∠-φ\n"
                "  φ = arccos(fp)     Za = impedancia serie",
                "Simula la linea corta (<80 km) con carga inductiva fp=0.9 en atraso. "
                "La corriente IR queda retrasada respecto a VR. Caso tipico de cargas industriales (motores).",
                [("R",  "Resistencia serie R (Ω)",       "5.0"),
                 ("X",  "Reactancia serie XL (Ω)",       "25.0"),
                 ("VR", "Tension receptora VR L-L (kV)", "115"),
                 ("IR", "Corriente de carga |IR| (A)",   "200"),
                 ("fp", "Factor de potencia fp (atraso)","0.9")],
                lambda v: (v, _calc_caso_A(v)),
                "#8b5cf6",
                plot_fn=lambda v: P.plot_lineas(
                    v['VR']*1e3/np.sqrt(3),
                    complex(v['VR']*1e3/np.sqrt(3),0)+complex(v['R'],v['X'])*complex(v['IR']*v['fp'],-v['IR']*np.sin(np.arccos(min(v['fp'],1.0)))),
                    complex(v['IR']*v['fp'],-v['IR']*np.sin(np.arccos(min(v['fp'],1.0)))),
                    complex(v['R'],v['X']),
                    (abs(complex(v['VR']*1e3/np.sqrt(3),0)+complex(v['R'],v['X'])*complex(v['IR']*v['fp'],-v['IR']*np.sin(np.arccos(min(v['fp'],1.0)))))-v['VR']*1e3/np.sqrt(3))/(v['VR']*1e3/np.sqrt(3))*100
                )),
            # ── PASO 2: Sumar impedancias en serie (Za) ──────────────────────
            _step_widget(
                "SUMA DE IMPEDANCIAS EN SERIE (Za):\n"
                "  Za = Z1 + Z2 = (R1+R2) + j(X1+X2)\n"
                "  |Za| = sqrt(Ra² + Xa²)\n"
                "  θza  = arctg(Xa / Ra)",
                "Suma los tramos resistivos e inductivos de la linea en serie. "
                "El resultado Za es la impedancia equivalente total que se usara en KVL.",
                [("R1","Resistencia tramo 1  R1 (Ω)","3.0"),
                 ("X1","Reactancia tramo 1   X1 (Ω)","15.0"),
                 ("R2","Resistancia tramo 2  R2 (Ω)","2.0"),
                 ("X2","Reactancia tramo 2   X2 (Ω)","10.0"),
                 ("freq","Frecuencia (Hz)","60")],
                lambda v: (v, _calc_Za(v)),
                "#8b5cf6"),
            # ── PASO 3: Definir fasores de la carga ───────────────────────────
            _step_widget(
                "FASORES DE LA CARGA:\n"
                "  VR = |VR·LN| ∠0°  (referencia de fase)\n"
                "  IR = |IR| ∠−φ    (atraso inductivo)\n"
                "  φ = arccos(fp)    Q_carga = |VR|·|IR|·sen(φ)",
                "Define el fasor VR como referencia (0°) y calcula el fasor IR con su angulo de desfase. "
                "Tambien calcula la potencia aparente, activa y reactiva de la carga.",
                [("VR_LL","VR Linea-Linea (kV)","115"),
                 ("IR_mag","Magnitud |IR| (A)","200"),
                 ("fp","Factor de potencia fp","0.9"),
                 ("tipo","Tipo: 1=inductiva  -1=capacitiva  0=resistiva","1")],
                lambda v: (v, _calc_fasores_carga(v)),
                "#8b5cf6"),
            # ── PASO 4: KCL (Kirchhoff de Corrientes) ─────────────────────────
            _step_widget(
                "LEY DE KIRCHHOFF DE CORRIENTES (KCL):\n"
                "  Modelo corto:  IS = IR  (sin shunt)\n"
                "  Modelo Pi:     IS = IR + I_shunt\n"
                "  I_shunt = (jBC/2)·VR   (ramificacion shunt)\n"
                "  Suma fasorial en el nodo receptor",
                "Aplica KCL en el nodo de carga. Para linea corta IS=IR. "
                "Para modelo Pi, la admitancia shunt BC/2 en el extremo receptor aporta corriente adicional.",
                [("IR_mag","|IR| corriente de carga (A)","200"),
                 ("fp","Factor potencia fp","0.9"),
                 ("tipo","1=inductivo  -1=capacitivo  0=resistivo","1"),
                 ("VR_LL","VR L-L (kV)","115"),
                 ("BC","Susceptancia shunt BC total (S)  [0=modelo corto]","0.002")],
                lambda v: (v, _calc_kcl_linea(v)),
                "#8b5cf6"),
            # ── PASO 5: KVL — Calcular VS ─────────────────────────────────────
            _step_widget(
                "LEY DE KIRCHHOFF DE VOLTAJES (KVL):\n"
                "  Malla: +VS − Za·IS − VR = 0\n"
                "  => VS = VR + Za·IS\n"
                "  RV% = (|VS|−|VR|)/|VR| × 100  [regulacion]",
                "Aplica KVL en la malla de la linea. Suma fasorialmente VR y la caida Za·IS "
                "para obtener VS. Calcula la regulacion de voltaje y las perdidas de potencia.",
                [("R",  "Resistencia Za real (Ω)",         "5.0"),
                 ("X",  "Reactancia  Za imag (Ω)",         "25.0"),
                 ("VR", "VR L-L (kV)",                     "115"),
                 ("IR", "|IR| (A)",                        "200"),
                 ("fp", "Factor potencia fp",               "0.9"),
                 ("tipo","1=ind(atraso) -1=cap(adelanto) 0=resis","1")],
                lambda v: (v, _calc_kvl_linea(v)),
                "#8b5cf6",
                plot_fn=lambda v: P.plot_lineas_kvl(v)),
            # ── CASO B: Carga Resistiva (F.P.=1.0) ────────────────────────────
            _step_widget(
                "CASO B — CARGA RESISTIVA (F.P. = 1.0):\n"
                "  φ = 0°  =>  IR en fase con VR\n"
                "  IR = |IR|·(1 + j0)\n"
                "  VS = VR + R·IR + jX·IR\n"
                "  Caida resistiva pura, sin componente reactiva",
                "Simula la linea con carga puramente resistiva (fp=1.0). "
                "La corriente esta en fase con VR => angulo cero. "
                "Comparar RV% con Caso A muestra cuanto aumenta la regulacion con carga inductiva.",
                [("R",  "Resistencia Za (Ω)",  "5.0"),
                 ("X",  "Reactancia Za (Ω)",   "25.0"),
                 ("VR", "VR L-L (kV)",         "115"),
                 ("IR", "|IR| (A)",             "200"),
                 ("BC", "BC shunt (S) [0=corto]","0.0")],
                lambda v: (v, _calc_caso_B(v)),
                "#8b5cf6",
                plot_fn=lambda v: P.plot_lineas_caso_B(v)),
            # ── CASO C: Carga Capacitiva (F.P.=0.9 adelanto) ─────────────────
            _step_widget(
                "CASO C — CARGA CAPACITIVA (F.P.=0.9 Adelanto):\n"
                "  φ = −arccos(0.9) = −25.84°\n"
                "  IR = |IR|∠+25.84°  (adelantada a VR)\n"
                "  La carga GENERA Q => jX·IR resta a VR\n"
                "  Puede dar |VS| < |VR| (Regulacion negativa!)",
                "Simula la linea con carga capacitiva a fp=0.9 en adelanto. "
                "Demuestra que la corriente adelantada puede reducir |VS| por debajo de |VR|, "
                "fenomeno conocido como regulacion negativa o efecto Ferranti en carga ligera.",
                [("R",  "Resistencia Za (Ω)",  "5.0"),
                 ("X",  "Reactancia Za (Ω)",   "25.0"),
                 ("VR", "VR L-L (kV)",         "115"),
                 ("IR", "|IR| (A)",             "200"),
                 ("BC", "BC shunt (S) [0=corto]","0.002")],
                lambda v: (v, _calc_caso_C(v)),
                "#8b5cf6",
                plot_fn=lambda v: P.plot_lineas_caso_C(v)),
            # ── MODELO PI (linea media) ────────────────────────────────────────
            _step_widget(
                "MODELO PI (80-250 km):\n"
                "  VS--[Z]--+--VR    Y/2 en cada extremo\n"
                "         [Y/2] [Y/2]\n"
                "  A=1+ZY/2  B=Z  C=Y(1+ZY/4)",
                "Modelo Pi para lineas medias. Incluye admitancia shunt distribuida en los extremos.",
                [("R","R total (Ω)","5.0"),("X","X total (Ω)","25.0"),("BC","BC total (S)","0.002"),
                 ("VR","VR L-L (kV)","115"),("IR","Magnitud IR (A)","200"),("fp","Factor potencia","0.9")],
                lambda v: (v, _calc_pi_line(v)),
                "#8b5cf6"),
            # ── DIAGNOSTICO FINAL: Comparacion A / B / C ──────────────────────
            _step_widget(
                "DIAGNOSTICO FINAL — COMPARACION A / B / C:\n"
                "  Caso A: fp=0.9 atraso  → RV% positivo y ALTO\n"
                "  Caso B: fp=1.0         → RV% moderado (minimo real)\n"
                "  Caso C: fp=0.9 adelanto→ RV% negativo (regulacion negativa)\n"
                "  REGLA: mayor fp => menor regulacion; adelantado mejora tension",
                "Evaluacion teorica comparando los tres escenarios A, B y C. "
                "Concluye el efecto del factor de potencia sobre la regulacion de voltaje, "
                "las perdidas en la linea y la potencia reactiva transportada.",
                [("R",    "Resistencia Za (Ω)",    "5.0"),
                 ("X",    "Reactancia Za (Ω)",     "25.0"),
                 ("VR",   "VR L-L (kV)",           "115"),
                 ("IR",   "|IR| (A)",               "200"),
                 ("BC",   "BC shunt (S)",            "0.002")],
                lambda v: (v, _calc_diagnostico_final(v)),
                "#8b5cf6",
                plot_fn=lambda v: P.plot_diagnostico_lineas(v)),
        ]
        self.step_titles = [
            "Caso A — Carga Inductiva (fp=0.9 atraso)",
            "Suma Impedancias en Serie (Za)",
            "Fasores de la Carga",
            "Kirchhoff de Corrientes (KCL)",
            "Kirchhoff de Voltajes (KVL) — Calcular VS",
            "Caso B — Carga Resistiva (fp=1.0)",
            "Caso C — Carga Capacitiva (fp=0.9 adelanto)",
            "Modelo Pi (Linea Media 80-250 km)",
            "Diagnostico Final — Comparacion Teorica A/B/C",
        ]


# ── helpers Tema 4 ────────────────────────────────────────────────────────────
def _linea_corta(R, X, VR_kv, IR_mag, fp_sign):
    """Calcula VS para linea corta. fp_sign: +1=atraso, -1=adelanto, 0=unidad.
    Devuelve (VS, IR_f, VR_f, phi, Z)"""
    fp_abs = abs(fp_sign) if fp_sign != 0 else 1.0
    phi = np.arccos(fp_abs)
    sign = np.sign(fp_sign) if fp_sign != 0 else 0
    Z = complex(R, X)
    VR_ln = VR_kv * 1e3 / np.sqrt(3)
    VR_f  = complex(VR_ln, 0)
    IR_f  = complex(IR_mag * fp_abs, -sign * IR_mag * np.sin(phi))
    VS    = VR_f + Z * IR_f
    return VS, IR_f, VR_f, phi, Z


def _calc_caso_A(v):
    """CASO A: carga inductiva fp=0.9 en atraso."""
    fp = min(max(v['fp'], 0.001), 1.0)
    VS, IR, VR_f, phi, Z = _linea_corta(v['R'], v['X'], v['VR'], v['IR'], fp)
    RV   = (abs(VS) - abs(VR_f)) / abs(VR_f) * 100
    Ploss = 3 * abs(IR)**2 * v['R'] / 1e6
    PS = abs(3 * VS * IR.conjugate()) / 1e6
    PR = abs(3 * VR_f * IR.conjugate()) / 1e6
    eta  = PR / PS * 100 if PS > 0 else 0
    QR   = 3 * abs(VR_f) * abs(IR) * np.sin(phi) / 1e6
    return (
        f"━━ DATOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Za = {v['R']}+j{v['X']} Ω     |Za|={abs(Z):.4f} Ω  ∠{np.degrees(np.angle(Z)):.2f}°\n"
        f"VR = {abs(VR_f)/1e3:.4f} kV L-N  = {v['VR']} kV L-L   ∠0° (ref.)\n"
        f"IR = {v['IR']:.2f} A    φ = arccos({fp:.4f}) = {np.degrees(phi):.4f}°\n"
        f"━━ FASOR IR (ATRASO) ━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"IR = {IR.real:.4f}{IR.imag:+.4f}j A   |IR|∠-{np.degrees(phi):.4f}°\n"
        f"━━ KIRCHHOFF DE VOLTAJES: VS=VR+Za·IR ━━━━━━━━━━\n"
        f"Za·IR = ({v['R']}+j{v['X']})·({IR.real:.2f}{IR.imag:+.2f}j)\n"
        f"Za·IR = {(Z*IR).real:.4f}{(Z*IR).imag:+.4f}j V L-N\n"
        f"VS = {VR_f.real:.2f} + {(Z*IR).real:.4f}{(Z*IR).imag:+.4f}j\n"
        f"VS = {VS.real:.4f}{VS.imag:+.4f}j V L-N\n"
        f"━━ RESULTADOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"|VS| = {abs(VS):.4f} V L-N = {abs(VS)*np.sqrt(3)/1e3:.5f} kV L-L\n"
        f"∠VS  = {np.degrees(np.angle(VS)):.4f}°\n"
        f"RV%  = (|VS|-|VR|)/|VR|×100 = {RV:.4f}%\n"
        f"PR   = {PR:.4f} MW   PS  = {PS:.4f} MW\n"
        f"QR   = {QR:.4f} MVAR (carga consume reactiva)\n"
        f"Perdidas = {Ploss:.5f} MW   Eficiencia = {eta:.4f}%"
    )


def _calc_Za(v):
    Ra = v['R1']+v['R2']; Xa = v['X1']+v['X2']
    Za = complex(Ra, Xa)
    theta = np.degrees(np.angle(Za))
    return (
        f"━━ TRAMO 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Z1 = {v['R1']} + j{v['X1']} Ω\n"
        f"━━ TRAMO 2 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Z2 = {v['R2']} + j{v['X2']} Ω\n"
        f"━━ SUMA EN SERIE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Za = Z1 + Z2\n"
        f"Ra = R1+R2 = {v['R1']}+{v['R2']} = {Ra:.4f} Ω\n"
        f"Xa = X1+X2 = {v['X1']}+{v['X2']} = {Xa:.4f} Ω\n"
        f"━━ FORMA POLAR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"|Za| = sqrt({Ra:.4f}²+{Xa:.4f}²) = {abs(Za):.6f} Ω\n"
        f"θza  = arctg({Xa:.4f}/{Ra:.4f}) = {theta:.4f}°\n"
        f"Za   = {abs(Za):.4f} ∠{theta:.4f}° Ω\n"
        f"━━ Verificacion ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Za = {Ra:.4f}+j{Xa:.4f} Ω  (forma rectangular)"
    )


def _calc_fasores_carga(v):
    fp = min(max(v['fp'], 0.001), 1.0)
    t  = int(v['tipo']) if v['tipo'] in (1.0,-1.0,0.0) else 1
    phi = np.arccos(fp)
    VR_ln = v['VR_LL']*1e3/np.sqrt(3)
    sign_q = t  # +1 lag, -1 lead, 0 res
    IR_f = complex(v['IR_mag']*fp, -t*v['IR_mag']*np.sin(phi))
    VR_f = complex(VR_ln, 0)
    SR   = 3*VR_f*IR_f.conjugate()
    tipo_txt = {1:"Inductiva (atraso)",0:"Resistiva",  -1:"Capacitiva (adelanto)"}[t]
    return (
        f"━━ FASOR VR (referencia) ━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"VR = {abs(VR_f)/1e3:.4f} kV L-N  ∠0°  (angulo de referencia)\n"
        f"VR = {VR_f.real:.4f}+j{VR_f.imag:.4f} V L-N\n"
        f"━━ ANGULO DE LA CORRIENTE ━━━━━━━━━━━━━━━━━━━━━━\n"
        f"fp = {fp:.4f}   φ = arccos({fp:.4f}) = {np.degrees(phi):.4f}°\n"
        f"Tipo: {tipo_txt}  =>  IR queda a {'−' if t==1 else '+' if t==-1 else ''}φ de VR\n"
        f"━━ FASOR IR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"IR = {v['IR_mag']:.4f}∠({'+' if t<0 else '-' if t>0 else ''}{np.degrees(phi):.4f}°) A\n"
        f"IR = {IR_f.real:.5f}{IR_f.imag:+.5f}j A (rectangular)\n"
        f"━━ POTENCIAS DE LA CARGA ━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"SR = 3·VR·IR* = {abs(SR)/1e6:.4f} MVA\n"
        f"PR = {SR.real/1e6:.4f} MW\n"
        f"QR = {SR.imag/1e6:.4f} MVAR  ({'consume' if SR.imag>0 else 'genera'})\n"
        f"fp_verif = PR/|SR| = {SR.real/abs(SR):.6f}"
    )


def _calc_kcl_linea(v):
    fp  = min(max(v['fp'], 0.001), 1.0)
    t   = int(v['tipo']) if v['tipo'] in (1.0,-1.0,0.0) else 1
    phi = np.arccos(fp)
    VR_ln = v['VR_LL']*1e3/np.sqrt(3)
    VR_f  = complex(VR_ln, 0)
    IR_f  = complex(v['IR_mag']*fp, -t*v['IR_mag']*np.sin(phi))
    Ish   = complex(0, v['BC']/2)*VR_f  # corriente shunt BC/2 en extremo receptor
    IS_pi = IR_f + Ish
    return (
        f"━━ NODO RECEPTOR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"KCL: IS = IR + I_shunt (suma fasorialmente)\n"
        f"━━ CORRIENTES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"IR    = {IR_f.real:.5f}{IR_f.imag:+.5f}j A   |IR|={abs(IR_f):.4f} A\n"
        f"I_sh  = jBC/2·VR = j{v['BC']/2:.5f}·{VR_ln:.2f}\n"
        f"I_sh  = {Ish.real:.6f}{Ish.imag:+.6f}j A   |I_sh|={abs(Ish):.6f} A\n"
        f"━━ SUMA FASORIAL ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"IS    = IR + I_sh = {IS_pi.real:.5f}{IS_pi.imag:+.5f}j A\n"
        f"|IS|  = {abs(IS_pi):.5f} A    ∠IS = {np.degrees(np.angle(IS_pi)):.4f}°\n"
        f"{'[Modelo corto: BC=0 => IS = IR]' if v['BC']==0 else '[Modelo Pi activo: IS != IR]'}"
    )


def _calc_kvl_linea(v):
    fp  = min(max(v['fp'], 0.001), 1.0)
    t   = int(v['tipo']) if v['tipo'] in (1.0,-1.0,0.0) else 1
    phi = np.arccos(fp)
    Z   = complex(v['R'], v['X'])
    VR_ln = v['VR']*1e3/np.sqrt(3)
    VR_f  = complex(VR_ln, 0)
    IS_f  = complex(v['IR']*fp, -t*v['IR']*np.sin(phi))
    VS    = VR_f + Z*IS_f
    RV    = (abs(VS)-abs(VR_f))/abs(VR_f)*100
    Ploss = 3*abs(IS_f)**2*v['R']/1e6
    PR    = (3*VR_f*IS_f.conjugate()).real/1e6
    PS    = (3*VS*IS_f.conjugate()).real/1e6
    eta   = PR/PS*100 if PS>0 else 0
    caida = Z*IS_f
    return (
        f"━━ KVL — MALLA DE LA LINEA ━━━━━━━━━━━━━━━━━━━━━\n"
        f"Ecuacion: VS − Za·IS − VR = 0  =>  VS = VR + Za·IS\n"
        f"━━ DATOS FASORIALES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"VR  = {VR_f.real:.4f} + j0  V L-N    (ref.)\n"
        f"Za  = {v['R']}+j{v['X']} Ω    |Za|={abs(Z):.4f} Ω\n"
        f"IS  = {IS_f.real:.4f}{IS_f.imag:+.4f}j A   (tipo={'atraso' if t==1 else 'adelanto' if t==-1 else 'en fase'})\n"
        f"━━ CAIDA DE TENSION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Za·IS = ({v['R']}+j{v['X']})·({IS_f.real:.4f}{IS_f.imag:+.4f}j)\n"
        f"Za·IS = {caida.real:.4f}{caida.imag:+.4f}j V L-N\n"
        f"━━ TENSION DE ENVIO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"VS = {VR_f.real:.4f} + ({caida.real:.4f}{caida.imag:+.4f}j)\n"
        f"VS = {VS.real:.4f}{VS.imag:+.4f}j V L-N\n"
        f"|VS|= {abs(VS):.4f} V L-N = {abs(VS)*np.sqrt(3)/1e3:.5f} kV L-L\n"
        f"∠VS = {np.degrees(np.angle(VS)):.4f}°\n"
        f"━━ REGULACION y PERDIDAS ━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"RV% = ({abs(VS):.2f}−{abs(VR_f):.2f})/{abs(VR_f):.2f}×100 = {RV:.4f}%\n"
        f"Ploss = 3·|IS|²·R = {Ploss:.5f} MW  (calor)\n"
        f"PR = {PR:.4f} MW    PS = {PS:.4f} MW\n"
        f"Eficiencia = {eta:.4f}%"
    )


def _calc_caso_B(v):
    """CASO B: fp=1.0 (resistiva)."""
    VS, IR, VR_f, phi, Z = _linea_corta(v['R'], v['X'], v['VR'], v['IR'], 0)
    RV    = (abs(VS)-abs(VR_f))/abs(VR_f)*100
    Ploss = 3*abs(IR)**2*v['R']/1e6
    PR    = (3*VR_f*IR.conjugate()).real/1e6
    PS    = (3*VS*IR.conjugate()).real/1e6
    eta   = PR/PS*100 if PS>0 else 0
    caida = Z*IR
    return (
        f"━━ CASO B: CARGA RESISTIVA (fp = 1.0) ━━━━━━━━━━\n"
        f"Za = {v['R']}+j{v['X']} Ω    |Za|={abs(Z):.4f} Ω  ∠{np.degrees(np.angle(Z)):.2f}°\n"
        f"VR = {abs(VR_f)/1e3:.4f} kV L-N  = {v['VR']} kV L-L   ∠0°\n"
        f"━━ FASOR IR (fp=1 => φ=0°, en fase con VR) ━━━━━\n"
        f"IR = {abs(IR):.4f}∠0° A  =  {IR.real:.4f}+j{IR.imag:.4f} A\n"
        f"━━ CAIDA DE TENSION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Za·IR = ({v['R']}+j{v['X']})·{abs(IR):.2f}\n"
        f"Za·IR = {caida.real:.4f}{caida.imag:+.4f}j V L-N\n"
        f"━━ VS = VR + Za·IR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"VS = {VS.real:.4f}{VS.imag:+.4f}j V L-N\n"
        f"|VS|= {abs(VS):.4f} V L-N = {abs(VS)*np.sqrt(3)/1e3:.5f} kV L-L\n"
        f"∠VS = {np.degrees(np.angle(VS)):.4f}°\n"
        f"━━ REGULACION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"RV% = {RV:.4f}%  (MODERADA — sin Q en la carga)\n"
        f"Ploss = {Ploss:.5f} MW   Eficiencia = {eta:.4f}%\n"
        f"PR = {PR:.4f} MW    PS = {PS:.4f} MW"
    )


def _calc_caso_C(v):
    """CASO C: fp=0.9 en adelanto (capacitiva)."""
    VS, IR, VR_f, phi, Z = _linea_corta(v['R'], v['X'], v['VR'], v['IR'], -0.9)
    RV    = (abs(VS)-abs(VR_f))/abs(VR_f)*100
    Ploss = 3*abs(IR)**2*v['R']/1e6
    PR    = (3*VR_f*IR.conjugate()).real/1e6
    PS    = (3*VS*IR.conjugate()).real/1e6
    eta   = PR/PS*100 if PS>0 else 0
    caida = Z*IR
    phi_deg = np.degrees(phi)
    return (
        f"━━ CASO C: CARGA CAPACITIVA (fp=0.9 adelanto) ━━━\n"
        f"Za = {v['R']}+j{v['X']} Ω    |Za|={abs(Z):.4f} Ω\n"
        f"VR = {abs(VR_f)/1e3:.4f} kV L-N  = {v['VR']} kV L-L   ∠0°\n"
        f"━━ FASOR IR (ADELANTADO a VR) ━━━━━━━━━━━━━━━━━━\n"
        f"φ = arccos(0.9) = {phi_deg:.4f}°  => IR adelanta φ grados\n"
        f"IR = {abs(IR):.4f}∠+{phi_deg:.4f}° A  =  {IR.real:.4f}{IR.imag:+.4f}j A\n"
        f"━━ CAIDA DE TENSION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Za·IR = {caida.real:.4f}{caida.imag:+.4f}j V L-N\n"
        f"(Componente imaginaria NEGATIVA => jX·IR REDUCE |VS|)\n"
        f"━━ VS = VR + Za·IR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"VS = {VS.real:.4f}{VS.imag:+.4f}j V L-N\n"
        f"|VS|= {abs(VS):.4f} V L-N = {abs(VS)*np.sqrt(3)/1e3:.5f} kV L-L\n"
        f"∠VS = {np.degrees(np.angle(VS)):.4f}°\n"
        f"━━ REGULACION NEGATIVA ━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"RV% = {RV:.4f}%  {'<= NEGATIVA: |VS|<|VR| !' if RV<0 else ''}\n"
        f"Ploss = {Ploss:.5f} MW   Eficiencia = {eta:.4f}%\n"
        f"PR = {PR:.4f} MW    PS = {PS:.4f} MW\n"
        f"CONCLUSION: carga capacitiva MEJORA el perfil de tension"
    )


def _calc_diagnostico_final(v):
    """Calcula los 3 casos y emite la tabla diagnostica."""
    def caso(fp_val, t):
        VS, IR, VR_f, phi, Z = _linea_corta(v['R'], v['X'], v['VR'], v['IR'], t*fp_val)
        RV = (abs(VS)-abs(VR_f))/abs(VR_f)*100
        Ploss = 3*abs(IR)**2*v['R']/1e6
        PR = (3*VR_f*IR.conjugate()).real/1e6
        PS = (3*VS*IR.conjugate()).real/1e6
        eta = PR/PS*100 if PS>0 else 0
        return abs(VS)*np.sqrt(3)/1e3, RV, Ploss, eta
    vA, rvA, plA, etA = caso(0.9,  1)
    vB, rvB, plB, etB = caso(1.0,  0)
    vC, rvC, plC, etC = caso(0.9, -1)
    return (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"TABLA COMPARATIVA  (R={v['R']}Ω  X={v['X']}Ω  VR={v['VR']}kV  IR={v['IR']}A)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{'Caso':<8}{'fp':<8}{'Tipo':<15}{'|VS|kV':<12}{'RV%':<12}{'Ploss MW':<13}{'Eta%':<8}\n"
        f"{'─'*72}\n"
        f"{'A':<8}{'0.9':<8}{'Inductiva':<15}{vA:<12.5f}{rvA:<12.4f}{plA:<13.5f}{etA:<8.4f}\n"
        f"{'B':<8}{'1.0':<8}{'Resistiva':<15}{vB:<12.5f}{rvB:<12.4f}{plB:<13.5f}{etB:<8.4f}\n"
        f"{'C':<8}{'0.9':<8}{'Capacitiva':<15}{vC:<12.5f}{rvC:<12.4f}{plC:<13.5f}{etC:<8.4f}\n"
        f"{'─'*72}\n"
        f"━━ CONCLUSIONES TEORICAS ━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"[1] Mayor fp => menor regulacion de voltaje\n"
        f"[2] Carga inductiva (A) genera la MAYOR caida de tension\n"
        f"[3] fp=1.0 (B) reduce las perdidas vs carga inductiva\n"
        f"[4] Carga capacitiva (C) RV%={'NEGATIVA' if rvC<0 else 'positiva'} => tension en envio MENOR\n"
        f"[5] Correc. de fp con condensadores => reduce RV% y Ploss\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def _calc_pi_line(v):
    """Modelo Pi: VS = A·VR + B·IR  con A=1+ZY/2, B=Z, C=Y(1+ZY/4)."""
    Z = complex(v['R'], v['X']); Y = complex(0, v['BC'])
    phi = np.arccos(min(max(v['fp'], 0.001), 1.0))
    A = 1 + Z*Y/2; B = Z; C = Y*(1+Z*Y/4)
    VRln = v['VR']*1e3/np.sqrt(3)
    IR   = complex(v['IR']*v['fp'], -v['IR']*np.sin(phi))
    VR_f = complex(VRln, 0)
    VS   = A*VR_f + B*IR; IS = C*VR_f + A*IR
    RV   = (abs(VS)-abs(VR_f))/abs(VR_f)*100
    Ploss = 3*abs(IR)**2*v['R']/1e6
    return (
        f"━━ CONSTANTES ABCD (MODELO PI) ━━━━━━━━━━━━━━━━━━\n"
        f"Z = {v['R']}+j{v['X']} Ω    Y = j{v['BC']} S\n"
        f"A = 1+ZY/2 = {A.real:.8f}{A.imag:+.8f}j\n"
        f"B = Z      = {B.real:.4f}{B.imag:+.4f}j Ω\n"
        f"C = Y(1+ZY/4) = {C.real:.10f}{C.imag:+.10f}j S\n"
        f"D = A (linea simetrica)    AD-BC = {(A*A-B*C).real:.8f} (=1.0)\n"
        f"━━ RESULTADOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"VS = A·VR + B·IR = {abs(VS):.4f} V L-N = {abs(VS)*np.sqrt(3)/1e3:.5f} kV L-L\n"
        f"∠VS = {np.degrees(np.angle(VS)):.4f}°\n"
        f"IS = C·VR + D·IR = {abs(IS):.5f} A   ∠IS={np.degrees(np.angle(IS)):.4f}°\n"
        f"RV% = {RV:.4f}%    Ploss = {Ploss:.5f} MW"
    )


# ══════════════════════════════════════════════════════════════════
# TEMA 5 – Constantes ABCD
# ══════════════════════════════════════════════════════════════════
class WizardABCD(ModuleWizard):
    MODULE_NAME = "Constantes Generalizadas ABCD"
    MODULE_COLOR = "#f472b6"

    def _build_steps(self):
        self.step_widgets = [
            _step_widget(
                "Cuadripolo de 2 puertos:\n"
                "  |VS|   |A  B| |VR|\n"
                "  |IS| = |C  D| |IR|\n"
                "  Corta: A=D=1  B=Z  C=0",
                "Calcula las constantes ABCD para el modelo Pi.",
                [("R","R total (Ohm)","5"),("X","X total (Ohm)","30"),("BC","BC total (S)","0.002")],
                lambda v: (v, _calc_abcd(v)),
                "#f472b6"),
            _step_widget(
                "Aplicar ABCD para encontrar VS e IS:\n"
                "  VS = A*VR + B*IR\n"
                "  IS = C*VR + D*IR",
                "Aplica las constantes para determinar voltaje y corriente en el extremo envio.",
                [("A_real","Re(A)","0.996"),("A_imag","Im(A)","0.0001"),
                 ("B_real","Re(B) Ohm","5"),("B_imag","Im(B) Ohm","30"),
                 ("VR","VR L-L (kV)","115"),("IR","IR (A)","200"),("fp","F.P.","0.85")],
                lambda v: (v, _apply_abcd(v)),
                "#f472b6"),
        ]
        self.step_titles = ["Calcular Constantes ABCD","Aplicar ABCD"]


def _calc_abcd(v):
    Z=complex(v['R'],v['X']); Y=complex(0,v['BC'])
    A=1+Z*Y/2; B=Z; C=Y*(1+Z*Y/4)
    return (f"Z = {v['R']}+j{v['X']} Ohm   Y = j{v['BC']} S\n"
            f"A = 1+ZY/2 = {A.real:.8f}{A.imag:+.8f}j\n"
            f"B = Z      = {B.real:.4f}{B.imag:+.4f}j Ohm\n"
            f"C = Y(1+ZY/4) = {C.real:.10f}{C.imag:+.10f}j S\n"
            f"D = A (linea simetrica)\nVerif AD-BC = {(A*A-B*C).real:.8f} (= 1.0)")

def _apply_abcd(v):
    A=complex(v['A_real'],v['A_imag']); B=complex(v['B_real'],v['B_imag'])
    phi=np.arccos(v['fp']); VRln=v['VR']*1e3/np.sqrt(3)
    IR=complex(v['IR']*v['fp'],-v['IR']*np.sin(phi)); VR_f=complex(VRln,0)
    VS=A*VR_f+B*IR
    return (f"VS = A*VR + B*IR\n"
            f"VS = ({A.real:.4f}+j{A.imag:.4f})*{VRln:.1f} + ({B.real:.2f}+j{B.imag:.2f})*({IR.real:.1f}+j{IR.imag:.1f})\n"
            f"VS = {VS.real:.2f}{VS.imag:+.2f}j V L-N\n"
            f"|VS| = {abs(VS):.2f} V = {abs(VS)*np.sqrt(3)/1e3:.5f} kV L-L\nAngulo = {np.degrees(np.angle(VS)):.4f} deg")


# ══════════════════════════════════════════════════════════════════
# TEMA 6 – Diagramas Circulares
# ══════════════════════════════════════════════════════════════════
class WizardCirculares(ModuleWizard):
    MODULE_NAME = "Diagramas Circulares de Potencia"
    MODULE_COLOR = "#fb923c"

    def _build_steps(self):
        self.step_widgets = [
            _step_widget(
                "Circulo de Recepcion:\n"
                "  Centro OR = |A|/|B| * VR^2  (en zona Q negativa)\n"
                "  Radio RR  = |VS|*|VR| / |B|",
                "Determina el centro y radio del circulo de recepcion P-Q.",
                [("VS","VS L-L (kV)","132"),("VR","VR L-L (kV)","115"),
                 ("A_mag","|A|","0.99"),("A_ang","ang A (deg)","1.5"),
                 ("B_mag","|B| Ohm","35"),("B_ang","ang B (deg)","80")],
                lambda v: (v, _calc_circle_params(v)),
                "#fb923c",
                plot_fn=lambda v: P.plot_circulares(v['VS'],v['VR'],v['A_mag'],v['A_ang'],v['B_mag'],v['B_ang'])),
            _step_widget(
                "Potencia transferida a angulo delta:\n"
                "  PR = RR*sin(delta + beta - pi/2) - |OR|*sin(beta-alpha-pi/2)\n"
                "  PR_max ocurre cuando delta = 90 - (beta - alpha)",
                "Calcula la potencia activa y reactiva transferida para un angulo delta.",
                [("VS","VS L-L (kV)","132"),("VR","VR L-L (kV)","115"),
                 ("A_mag","|A|","0.99"),("A_ang","ang A (deg)","1.5"),
                 ("B_mag","|B| Ohm","35"),("B_ang","ang B (deg)","80"),
                 ("delta","angulo delta (deg)","20")],
                lambda v: (v, _calc_circle_power(v)),
                "#fb923c"),
        ]
        self.step_titles = ["Centro y Radio","Potencia Transferida"]


def _calc_circle_params(v):
    VS=v['VS']*1e3/np.sqrt(3); VR=v['VR']*1e3/np.sqrt(3)
    OR_mag=v['A_mag']*VR**2/v['B_mag']; RR=VS*VR/v['B_mag']
    OR_mag3=3*OR_mag/1e6; RR3=3*RR/1e6
    return (f"|OR| = |A|*VR^2/|B| = {v['A_mag']}*{VR:.0f}^2/{v['B_mag']} = {OR_mag:.2f} VA L-N\n"
            f"RR   = |VS|*|VR|/|B| = {VS:.0f}*{VR:.0f}/{v['B_mag']} = {RR:.2f} VA L-N\n"
            f"(3 fases):\n  |OR| x3 = {OR_mag3:.4f} MW/MVAR\n  RR x3   = {RR3:.4f} MW/MVAR\n"
            f"PR_max = RR - |OR| = {RR3-OR_mag3:.4f} MW (aprox, sin perdidas)")

def _calc_circle_power(v):
    VS=v['VS']*1e3/np.sqrt(3); VR=v['VR']*1e3/np.sqrt(3)
    Ba=np.radians(v['B_ang']); Aa=np.radians(v['A_ang']); d=np.radians(v['delta'])
    RR=VS*VR/v['B_mag']; OR=v['A_mag']*VR**2/v['B_mag']
    PR=3*(RR*np.sin(d-(Ba-np.pi/2))+OR*np.sin(Ba-Aa-np.pi/2))/1e6
    QR=3*(-RR*np.cos(d-(Ba-np.pi/2))+OR*np.cos(Ba-Aa-np.pi/2))/1e6
    SR=np.sqrt(PR**2+QR**2)
    return (f"delta = {v['delta']} deg\n"
            f"PR = {PR:.4f} MW\nQR = {QR:.4f} MVAR\n|SR| = {SR:.4f} MVA\nfp = {PR/SR:.4f}")


# ══════════════════════════════════════════════════════════════════
# TEMA 7 – Flujo de Potencia
# ══════════════════════════════════════════════════════════════════
class WizardFlujoPotencia(ModuleWizard):
    MODULE_NAME = "Flujo de Potencia"
    MODULE_COLOR = "#22d3ee"

    def _build_steps(self):
        self.step_widgets = [
            _step_widget(
                "Sistema 3 barras:\n"
                "  Bus1(slack) --Y12-- Bus2(PQ) --Y23-- Bus3(PQ)\n"
                "                       |Y13|\n"
                "Formar la matriz Ybus: diagonal = suma admitancias",
                "Forma la matriz Ybus del sistema.",
                [("y12","|Y12| linea 1-2 (pu)","10"),("y13","|Y13| linea 1-3 (pu)","8"),
                 ("y23","|Y23| linea 2-3 (pu)","12")],
                lambda v: (v, _build_ybus(v)),
                "#22d3ee"),
            _step_widget(
                "Gauss-Seidel:\n"
                "  Vi(k+1) = [1/Yii] * [(Pi-jQi)/Vi*(k) - sum_j!=i Yij*Vj]\n"
                "  Iterar hasta |dV| < epsilon",
                "Ejecuta el metodo de Gauss-Seidel para calcular voltajes nodales.",
                [("y12","|Y12| (pu)","10"),("y13","|Y13| (pu)","8"),("y23","|Y23| (pu)","12"),
                 ("V1","V1 slack (pu)","1.05"),
                 ("P2","P2 inyectada (pu)","-0.5"),("Q2","Q2 inyectada (pu)","-0.2"),
                 ("P3","P3 inyectada (pu)","-0.8"),("Q3","Q3 inyectada (pu)","-0.3"),
                 ("eps","Tolerancia epsilon","0.0001")],
                lambda v: (v, _gauss_seidel_3bus(v)),
                "#22d3ee"),
            _step_widget(
                "Flujos en las ramas:\n"
                "  Sij = Vi * (Vi - Vj)* * Yij*\n"
                "  Perdidas Pij = Sij + Sji (real)",
                "Calcula los flujos de potencia activa y reactiva en cada linea.",
                [("V1_mag","|V1| (pu)","1.05"),("V1_ang","ang V1 (deg)","0"),
                 ("V2_mag","|V2| (pu)","0.982"),("V2_ang","ang V2 (deg)","-4.5"),
                 ("V3_mag","|V3| (pu)","0.975"),("V3_ang","ang V3 (deg)","-7.2"),
                 ("y12","Y12 (pu)","10"),("y13","Y13 (pu)","8"),("y23","Y23 (pu)","12"),
                 ("Sbase","Sbase (MVA)","100")],
                lambda v: (v, _calc_flows(v)),
                "#22d3ee"),
        ]
        self.step_titles = ["Formar Ybus","Iteracion Gauss-Seidel","Flujos en las Ramas"]


def _build_ybus(v):
    Y11=v['y12']+v['y13']; Y22=v['y12']+v['y23']; Y33=v['y13']+v['y23']
    return (f"Ybus (3x3):\n"
            f"  [ {Y11:.2f}   -{v['y12']:.2f}   -{v['y13']:.2f}]\n"
            f"  [-{v['y12']:.2f}    {Y22:.2f}   -{v['y23']:.2f}]\n"
            f"  [-{v['y13']:.2f}   -{v['y23']:.2f}    {Y33:.2f}]\n"
            f"(todos imaginarios puros si solo reactancias)")

def _gauss_seidel_3bus(v):
    Y12=complex(0,-v['y12']); Y13=complex(0,-v['y13']); Y23=complex(0,-v['y23'])
    Y11=-(Y12+Y13); Y22=-(Y12+Y23); Y33=-(Y13+Y23)
    V1=complex(v['V1'],0); V2=complex(1,0); V3=complex(1,0)
    res="Iteraciones:\n"
    for k in range(30):
        S2c=complex(v['P2'],-v['Q2']); S3c=complex(v['P3'],-v['Q3'])
        V2n=(S2c/V2.conjugate()-Y12*V1-Y23*V3)/Y22
        V3n=(S3c/V3.conjugate()-Y13*V1-Y23*V2n)/Y33
        dV=max(abs(V2n-V2),abs(V3n-V3))
        V2=V2n; V3=V3n
        res+=f" k={k+1}: |V2|={abs(V2):.5f}∠{np.degrees(np.angle(V2)):+.3f}  |V3|={abs(V3):.5f}∠{np.degrees(np.angle(V3)):+.3f}  |dV|={dV:.2e}\n"
        if dV<v['eps']: res+=f"CONVERGENCIA en {k+1} iteraciones\n"; break
    return res

def _calc_flows(v):
    V1=complex(v['V1_mag']*np.cos(np.radians(v['V1_ang'])),v['V1_mag']*np.sin(np.radians(v['V1_ang'])))
    V2=complex(v['V2_mag']*np.cos(np.radians(v['V2_ang'])),v['V2_mag']*np.sin(np.radians(v['V2_ang'])))
    V3=complex(v['V3_mag']*np.cos(np.radians(v['V3_ang'])),v['V3_mag']*np.sin(np.radians(v['V3_ang'])))
    Y12=complex(0,-v['y12']); Y13=complex(0,-v['y13']); Y23=complex(0,-v['y23'])
    S12=V1*(V1-V2).conjugate()*(-Y12).conjugate(); S13=V1*(V1-V3).conjugate()*(-Y13).conjugate()
    S23=V2*(V2-V3).conjugate()*(-Y23).conjugate()
    sb=v['Sbase']
    return (f"Flujo P12 = {S12.real*sb:.3f} MW   Q12 = {S12.imag*sb:.3f} MVAR\n"
            f"Flujo P13 = {S13.real*sb:.3f} MW   Q13 = {S13.imag*sb:.3f} MVAR\n"
            f"Flujo P23 = {S23.real*sb:.3f} MW   Q23 = {S23.imag*sb:.3f} MVAR\n"
            f"Perdidas P12+P21 = {(S12+V2*(V2-V1).conjugate()*(-Y12).conjugate()).real*sb:.4f} MW")


# ══════════════════════════════════════════════════════════════════
# TEMA 8 – Despacho Economico
# ══════════════════════════════════════════════════════════════════
class WizardDespacho(ModuleWizard):
    MODULE_NAME = "Despacho Economico de Centrales Termicas"
    MODULE_COLOR = "#facc15"

    def _build_steps(self):
        self.step_widgets = [
            _step_widget(
                "Funciones de costo:\n"
                "  Ci(Pi) = ai + bi*Pi + ci*Pi^2  [$/h]\n"
                "  Curva dCi/dPi = bi + 2*ci*Pi  (costo incremental)",
                "Define las funciones de costo de cada central termica.",
                [("a1","a1 ($/h)","200"),("b1","b1 ($/MWh)","9"),("c1","c1 ($/MW^2h)","0.01"),
                 ("a2","a2","180"),("b2","b2","7.5"),("c2","c2","0.012"),
                 ("a3","a3","140"),("b3","b3","8.0"),("c3","c3","0.008")],
                lambda v: (v,
                    f"dC1/dP = {v['b1']} + {2*v['c1']}*P\n"
                    f"dC2/dP = {v['b2']} + {2*v['c2']}*P\n"
                    f"dC3/dP = {v['b3']} + {2*v['c3']}*P\n\n"
                    f"Punto minimo si P=0:\n"
                    f"  lam_min arranque G1 = {v['b1']}, G2 = {v['b2']}, G3 = {v['b3']} $/MWh"),
                "#facc15"),
            _step_widget(
                "Lambda Iteration:\n"
                "  Pi = (lambda - bi) / (2*ci)\n"
                "  Condicion: sum(Pi) = PD",
                "Calcula el despacho optimo por iteracion de lambda.",
                [("b1","b1","9"),("c1","c1","0.01"),("b2","b2","7.5"),("c2","c2","0.012"),
                 ("b3","b3","8.0"),("c3","c3","0.008"),
                 ("Pmin1","Pmin1 (MW)","50"),("Pmax1","Pmax1 (MW)","200"),
                 ("Pmin2","Pmin2 (MW)","40"),("Pmax2","Pmax2 (MW)","150"),
                 ("Pmin3","Pmin3 (MW)","30"),("Pmax3","Pmax3 (MW)","250"),
                 ("PD","Demanda PD (MW)","400")],
                lambda v: (v, _lambda_iter(v)),
                "#facc15"),
            _step_widget(
                "Costo total y verificacion:\n"
                "  CT = sum(Ci(Pi))\n"
                "  Verificar sum(Pi) = PD",
                "Verifica el despacho y calcula el costo total optimo.",
                [("P1","P1 optimo (MW)","150"),("P2","P2 optimo (MW)","110"),("P3","P3 optimo (MW)","140"),
                 ("a1","a1","200"),("b1","b1","9"),("c1","c1","0.01"),
                 ("a2","a2","180"),("b2","b2","7.5"),("c2","c2","0.012"),
                 ("a3","a3","140"),("b3","b3","8"),("c3","c3","0.008"),("PD","PD (MW)","400")],
                lambda v: (v,
                    f"C1({v['P1']:.0f}) = {v['a1']+v['b1']*v['P1']+v['c1']*v['P1']**2:.2f} $/h\n"
                    f"C2({v['P2']:.0f}) = {v['a2']+v['b2']*v['P2']+v['c2']*v['P2']**2:.2f} $/h\n"
                    f"C3({v['P3']:.0f}) = {v['a3']+v['b3']*v['P3']+v['c3']*v['P3']**2:.2f} $/h\n"
                    f"CT_total = {sum([v['a1']+v['b1']*v['P1']+v['c1']*v['P1']**2,v['a2']+v['b2']*v['P2']+v['c2']*v['P2']**2,v['a3']+v['b3']*v['P3']+v['c3']*v['P3']**2]):.2f} $/h\n"
                    f"sum(Pi) = {v['P1']+v['P2']+v['P3']:.2f} MW  (PD={v['PD']} MW)"),
                "#facc15",
                plot_fn=lambda v: P.plot_despacho(
                    [v['b1'],v['b2'],v['b3']],[v['c1'],v['c2'],v['c3']],
                    [v['a1'],v['a2'],v['a3']],[v['P1'],v['P2'],v['P3']],
                    (v['b1']+2*v['c1']*v['P1']+v['b2']+2*v['c2']*v['P2'])/2,
                    v['PD'],[50,40,30],[200,150,250])),
        ]
        self.step_titles = ["Funciones de Costo","Lambda Iteration","Verificacion y Costo Total"]


def _lambda_iter(v):
    b=[v['b1'],v['b2'],v['b3']]; c=[v['c1'],v['c2'],v['c3']]
    Pmn=[v['Pmin1'],v['Pmin2'],v['Pmin3']]; Pmx=[v['Pmax1'],v['Pmax2'],v['Pmax3']]
    lm=max(b[i]+2*c[i]*Pmn[i] for i in range(3)); lx=min(b[i]+2*c[i]*Pmx[i] for i in range(3))
    lam=(lm+lx)/2; P=[0.0]*3; res=f"Rango lambda: [{lm:.3f}, {lx:.3f}]\n"
    for it in range(60):
        Pn=[(lam-b[i])/(2*c[i]) for i in range(3)]
        Pn=[max(Pmn[i],min(Pmx[i],Pn[i])) for i in range(3)]
        err=sum(Pn)-v['PD']; P=Pn
        if abs(err)<0.01: res+=f"Convergencia en {it+1} iters\n"; break
        if err>0: lx=lam
        else: lm=lam
        lam=(lm+lx)/2
    res+=f"lambda_opt = {lam:.5f} $/MWh\n"
    for i in range(3): res+=f"P{i+1} = ({lam:.4f}-{b[i]})/{2*c[i]} = {P[i]:.2f} MW\n"
    res+=f"sum(Pi) = {sum(P):.2f} MW  (PD={v['PD']} MW)"
    return res


# ══════════════════════════════════════════════════════════════════
# TEMA 9 – Teoria de Fallas
# ══════════════════════════════════════════════════════════════════
class WizardFallas(ModuleWizard):
    MODULE_NAME = "Teoria de Fallas"
    MODULE_COLOR = "#ef4444"

    def _build_steps(self):
        self.step_widgets = [
            _step_widget(
                "Pre-falla: calcular Ibase y condicion pre-falla\n"
                "  Ibase = Sbase / (sqrt(3)*Vbase)\n"
                "  V_pre-falla = 1.0 pu (tension nominal)",
                "Establece las bases y la condicion pre-falla del sistema.",
                [("Sbase","Sbase (MVA)","100"),("Vbase","Vbase (kV)","115"),
                 ("Vpf","V_prefalla (pu)","1.0")],
                lambda v: (v,
                    f"Ibase = {v['Sbase']}e6 / (sqrt(3)*{v['Vbase']}e3)\n"
                    f"Ibase = {v['Sbase']*1e6/(np.sqrt(3)*v['Vbase']*1e3):.4f} A\n"
                    f"V_prefalla = {v['Vpf']} pu = {v['Vpf']*v['Vbase']/np.sqrt(3):.4f} kV L-N"),
                "#ef4444"),
            _step_widget(
                "Falla Trifasica simetrica (peor caso):\n"
                "  Solo red de secuencia positiva\n"
                "  Ia1 = Vpf / Z1",
                "Calcula la corriente de falla trifasica simetrica.",
                [("Vpf","V_prefalla (pu)","1.0"),("Z1","Z1 seq+ (pu)","0.1"),
                 ("Ibase","Ibase (A)","502.0")],
                lambda v: (v,
                    f"Falla 3-fases:\n"
                    f"  Ia1 = {v['Vpf']} / j{v['Z1']} = {v['Vpf']/v['Z1']:.4f} pu (magnitud)\n"
                    f"  Ia  = Ia1 = {v['Vpf']/v['Z1']:.4f} pu\n"
                    f"  |If| = {v['Vpf']/v['Z1']*v['Ibase']:.2f} A rms"),
                "#ef4444"),
            _step_widget(
                "Falla Monofasica a tierra (SLG):\n"
                "  Z1, Z2, Z0 en SERIE\n"
                "  Ia1 = Vpf/(Z1+Z2+Z0)\n"
                "  Ia  = 3*Ia1",
                "Calcula la corriente de falla monofasica a tierra (SLG).",
                [("Vpf","V_prefalla (pu)","1.0"),("Z1","Z1 (pu)","0.1"),
                 ("Z2","Z2 (pu)","0.1"),("Z0","Z0 (pu)","0.3"),("Ibase","Ibase (A)","502.0")],
                lambda v: (v,
                    f"Falla SLG (fase A a tierra):\n"
                    f"  Zlotal = Z1+Z2+Z0 = j{v['Z1']+v['Z2']+v['Z0']:.3f} pu\n"
                    f"  Ia1 = {v['Vpf']}/j{v['Z1']+v['Z2']+v['Z0']:.3f} = {v['Vpf']/(v['Z1']+v['Z2']+v['Z0']):.4f} pu\n"
                    f"  Ia  = 3*Ia1 = {3*v['Vpf']/(v['Z1']+v['Z2']+v['Z0']):.4f} pu\n"
                    f"  |If| = {3*v['Vpf']/(v['Z1']+v['Z2']+v['Z0'])*v['Ibase']:.2f} A rms"),
                "#ef4444"),
            _step_widget(
                "Falla Bifasica LL (fases B-C):\n"
                "  Z1, Z2 en SERIE  (Z0 no interviene)\n"
                "  Ia1 = Vpf/(Z1+Z2)\n"
                "  |Ib| = |Ic| = sqrt(3)*|Ia1|",
                "Calcula la corriente de falla bifasica entre fases.",
                [("Vpf","V_prefalla (pu)","1.0"),("Z1","Z1 (pu)","0.1"),
                 ("Z2","Z2 (pu)","0.1"),("Z0","Z0 (pu, para comparar)","0.3"),
                 ("Ibase","Ibase (A)","502.0")],
                lambda v: (v,
                    f"Falla LL (B-C):\n"
                    f"  Ia1 = {v['Vpf']}/j{v['Z1']+v['Z2']:.3f} = {v['Vpf']/(v['Z1']+v['Z2']):.4f} pu\n"
                    f"  |Ib|=|Ic| = sqrt(3)*|Ia1| = {np.sqrt(3)*v['Vpf']/(v['Z1']+v['Z2']):.4f} pu\n"
                    f"  |If| = {np.sqrt(3)*v['Vpf']/(v['Z1']+v['Z2'])*v['Ibase']:.2f} A rms"),
                "#ef4444",
                plot_fn=lambda v: P.plot_fallas(v['Vpf'],v['Z1'],v['Z2'],v['Z0'],v['Ibase'])),
        ]
        self.step_titles = ["Condicion Pre-Falla","Falla Trifasica 3phi","Falla SLG","Falla Bifasica LL"]
