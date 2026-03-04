"""9 módulos wizard paso a paso - Pumacayo & Romero"""
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from app.ui.wizard_module import ModuleWizard, _lbl, _field, _box, _result_box, _sep
import app.ui.plots as P


def _step_widget(schema_txt, desc_txt, fields_def, calc_fn, color="#38bdf8", plot_fn=None):
    """
    Construye un widget de paso estandar.
    calc_fn(vals) -> (inputs_dict, result_str)
    plot_fn(vals) -> None (abre matplotlib)   [opcional]
    """
    w = QWidget(); w.setStyleSheet("background:#020617;")
    lay = QVBoxLayout(w); lay.setSpacing(6); lay.setContentsMargins(14,10,14,10)

    # Esquema ASCII
    schema = QTextEdit(); schema.setReadOnly(True)
    schema.setPlainText(schema_txt)
    schema.setStyleSheet(f"background:#0f172a;color:{color};font-family:Consolas;font-size:11px;"
                         "border:1px solid #1e293b;border-radius:6px;")
    schema.setMaximumHeight(115); lay.addWidget(schema)
    lay.addWidget(_lbl(desc_txt, "#94a3b8", size=11))
    lay.addWidget(_sep())

    # Campos
    fields = {}
    box = _box("Datos de Entrada", color); form = QFormLayout()
    for name, lbl, default in fields_def:
        e = _field(default); fields[name] = e
        form.addRow(_lbl(lbl, "#64748b", size=11), e)
    box.setLayout(form); lay.addWidget(box)

    # Fila de botones
    btn_row = QHBoxLayout(); btn_row.setSpacing(8)
    btn_calc = QPushButton("⚡ Calcular este paso")
    btn_calc.setStyleSheet(f"background:{color};color:#020617;font-weight:900;"
                           "padding:10px;border-radius:6px;font-size:13px;")
    btn_row.addWidget(btn_calc)

    last_vals = {}  # guardamos para el botón de gráfica

    if plot_fn:
        btn_plot = QPushButton("📊 Ver Gráfica")
        btn_plot.setStyleSheet(f"background:#1e293b;color:{color};border:1px solid {color};"
                               "padding:10px;border-radius:6px;font-weight:700;font-size:13px;")
        btn_plot.setEnabled(False)   # sólo activo después de calcular
        btn_row.addWidget(btn_plot)

    lay.addLayout(btn_row)
    res = _result_box(); lay.addWidget(res, stretch=1)
    step_data = {"inputs": {}, "result": ""}

    def on_calc():
        try:
            vals = {k: float(v.text()) for k, v in fields.items()}
            last_vals.clear(); last_vals.update(vals)
            inp, txt = calc_fn(vals)
            res.setPlainText(txt)
            step_data["inputs"] = inp
            step_data["result"] = txt
            if plot_fn:
                btn_plot.setEnabled(True)
        except Exception as ex:
            res.setPlainText(f"Error: {ex}")

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
            _step_widget(
                "MODELO LINEA CORTA (< 80 km):\n"
                "  VS ---[Z=R+jX]--- VR\n"
                "  VS = VR + Z*IR",
                "Modelo serie puro. Ideal para lineas cortas (< 80 km).",
                [("R","Resistencia total R (Ohm)","5.0"),("X","Reactancia total X (Ohm)","25.0"),
                 ("VR","VR L-L (kV)","115"),("IR","Magnitud IR (A)","200"),("fp","Factor potencia","0.9")],
                lambda v: (v, _calc_short_line(v)),
                "#8b5cf6",
                plot_fn=lambda v: P.plot_lineas(
                    v['VR']*1e3/np.sqrt(3),
                    complex(v['VR']*1e3/np.sqrt(3),0)+complex(v['R'],v['X'])*complex(v['IR']*v['fp'],-v['IR']*np.sin(np.arccos(v['fp']))),
                    complex(v['IR']*v['fp'],-v['IR']*np.sin(np.arccos(v['fp']))),
                    complex(v['R'],v['X']),
                    (abs(complex(v['VR']*1e3/np.sqrt(3),0)+complex(v['R'],v['X'])*complex(v['IR']*v['fp'],-v['IR']*np.sin(np.arccos(v['fp']))))-v['VR']*1e3/np.sqrt(3))/(v['VR']*1e3/np.sqrt(3))*100
                )),
            _step_widget(
                "MODELO PI (80-250 km):\n"
                "   VS--[Z]--+--VR    Y/2 en cada extremo\n"
                "           [Y/2]  [Y/2]\n"
                "  A = 1 + ZY/2   B = Z",
                "Modelo Pi para lineas medias. Incluye la admitancia shunt.",
                [("R","R total (Ohm)","5.0"),("X","X total (Ohm)","25.0"),("BC","BC total (S)","0.002"),
                 ("VR","VR L-L (kV)","115"),("IR","Magnitud IR (A)","200"),("fp","Factor potencia","0.9")],
                lambda v: (v, _calc_pi_line(v)),
                "#8b5cf6"),
            _step_widget(
                "REGULACION DE VOLTAJE Y EFICIENCIA:\n"
                "  RV% = (|VS|-|VR|)/|VR| x 100\n"
                "  Eta% = PR/PS x 100",
                "Evalua la calidad de la transmision.",
                [("VS_kv","VS L-L (kV) calculado","118.5"),("VR_kv","VR L-L (kV)","115"),
                 ("PR","Potencia recibida PR (MW)","40"),("PS","Potencia enviada PS (MW)","41.5")],
                lambda v: (v,
                    f"Regulacion = ({v['VS_kv']}-{v['VR_kv']})/{v['VR_kv']} x 100 = "
                    f"{(v['VS_kv']-v['VR_kv'])/v['VR_kv']*100:.3f}%\n"
                    f"Eficiencia = {v['PR']}/{v['PS']} x 100 = {v['PR']/v['PS']*100:.3f}%\n"
                    f"Perdidas   = {v['PS']-v['PR']:.3f} MW"),
                "#8b5cf6"),
        ]
        self.step_titles = ["Modelo Linea Corta","Modelo Pi (Media)","Regulacion y Eficiencia"]


def _calc_short_line(v):
    Z=complex(v['R'],v['X']); phi=np.arccos(v['fp']); VRln=v['VR']*1e3/np.sqrt(3)
    IR=complex(v['IR']*v['fp'],-v['IR']*np.sin(phi)); VR_f=complex(VRln,0)
    VS=VR_f+Z*IR; RV=(abs(VS)-abs(VRln))/VRln*100; Ploss=abs(IR)**2*v['R']/1e6
    return (f"Z = {v['R']}+j{v['X']} Ohm\n"
            f"IR = {v['IR']}A / {np.degrees(phi):.2f}deg lagging\n"
            f"VS = VR + Z*IR = {VS.real:.2f}{VS.imag:+.2f}j  V L-N\n"
            f"|VS| = {abs(VS):.2f} V L-N  = {abs(VS)*np.sqrt(3)/1e3:.4f} kV L-L\n"
            f"Angulo VS = {np.degrees(np.angle(VS)):.3f} deg\n"
            f"Regulacion = {RV:.3f}%\n"
            f"Perdidas = {Ploss:.4f} MW")

def _calc_pi_line(v):
    Z=complex(v['R'],v['X']); Y=complex(0,v['BC']); phi=np.arccos(v['fp'])
    A=1+Z*Y/2; B=Z; C=Y*(1+Z*Y/4)
    VRln=v['VR']*1e3/np.sqrt(3); IR=complex(v['IR']*v['fp'],-v['IR']*np.sin(phi))
    VR_f=complex(VRln,0); VS=A*VR_f+B*IR; IS=C*VR_f+A*IR
    return (f"A = 1+ZY/2 = {A.real:.6f}{A.imag:+.6f}j\n"
            f"B = Z      = {B.real:.4f}{B.imag:+.4f}j Ohm\n"
            f"C = Y(1+ZY/4) = {C.real:.8f}{C.imag:+.8f}j S\n"
            f"VS = A*VR + B*IR = {abs(VS):.2f} V L-N = {abs(VS)*np.sqrt(3)/1e3:.4f} kV L-L\n"
            f"IS = {abs(IS):.4f} A")


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
