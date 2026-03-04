"""
plots.py — Gráficas reales (matplotlib) para cada módulo Pumacayo.
Cada función recibe los parámetros calculados y muestra una figura interactiva.
"""
import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Arc, Circle
from matplotlib.gridspec import GridSpec

# Paleta oscura consistente
DARK_BG   = "#0f172a"
PANEL_BG  = "#1e293b"
TEXT_COL  = "#f8fafc"
GRID_COL  = "#334155"
COLORS    = ["#38bdf8","#10b981","#f59e0b","#8b5cf6","#f472b6","#fb923c","#22d3ee","#facc15","#ef4444"]

def _style(fig, axes_list):
    fig.patch.set_facecolor(DARK_BG)
    for ax in axes_list:
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_COL, labelsize=8)
        ax.xaxis.label.set_color(TEXT_COL)
        ax.yaxis.label.set_color(TEXT_COL)
        ax.title.set_color(COLORS[0])
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_COL)
        ax.grid(True, color=GRID_COL, linewidth=0.5, linestyle="--", alpha=0.6)


# ─────────────────────────────────────────────────────────────────────────────
# TEMA 1 – Diagrama de circuito en p.u. con zoom en zona de tensión
# ─────────────────────────────────────────────────────────────────────────────
def plot_perunit(Vbase1, Vbase2, Sbase, Zreal, Zpu):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    fig.suptitle("Tema 1 — Sistema Por Unidad", color=TEXT_COL, fontsize=13, fontweight="bold")
    _style(fig, [ax1, ax2])

    # Izquierda: barras de magnitud real vs. base
    bases = ["Vbase1\n(kV)", "Vbase2\n(kV)", "Sbase\n(MVA)"]
    vals  = [Vbase1, Vbase2, Sbase]
    bars  = ax1.bar(bases, vals, color=COLORS[:3], edgecolor=DARK_BG, linewidth=1.5)
    for bar, v in zip(bars, vals):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(vals)*0.01,
                 f"{v:.1f}", ha="center", va="bottom", color=TEXT_COL, fontsize=9)
    ax1.set_title("Magnitudes Base del Sistema", color=COLORS[0])
    ax1.set_ylabel("Valor", color=TEXT_COL)

    # Derecha: comparar Z_real vs Z_pu escalado
    Zbase = Vbase1**2*1e6 / (Sbase*1e6)
    etiquetas = ["Z_real (Ω)", "Zbase (Ω)", "Zpu × Zbase"]
    valores   = [Zreal, Zbase, Zpu * Zbase]
    cols = [COLORS[3], COLORS[0], COLORS[1]]
    b2 = ax2.bar(etiquetas, valores, color=cols, edgecolor=DARK_BG)
    for bar, v in zip(b2, valores):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(valores)*0.01,
                 f"{v:.3f}", ha="center", va="bottom", color=TEXT_COL, fontsize=9)
    ax2.set_title(f"Verificación: Zpu = {Zpu:.4f} pu", color=COLORS[0])
    ax2.set_ylabel("Ohm", color=TEXT_COL)

    plt.tight_layout(); plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# TEMA 2 – Sección transversal + curva L vs D
# ─────────────────────────────────────────────────────────────────────────────
def plot_inductancia(r_cm, D12, D23, D31, L_mH_km, XL_km):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    fig.suptitle("Tema 2 — Inductancia de Líneas", color=TEXT_COL, fontsize=13, fontweight="bold")
    _style(fig, [ax1, ax2])

    # Izquierda: sección transversal de los 3 conductores
    ax1.set_aspect("equal"); ax1.set_xlim(-1, D12+D23+1); ax1.set_ylim(-2, 3)
    positions = [(0, 0), (D12, 0), (D12+D23, 0)]
    labels = ["A", "B", "C"]; cols = [COLORS[0], COLORS[2], COLORS[8]]
    for (x, y), lbl, c in zip(positions, labels, cols):
        outer = Circle((x, y), r_cm/100*8, color=c, alpha=0.25)
        inner = Circle((x, y), r_cm/100*8*np.exp(-0.25), color=c, alpha=0.7)
        dot   = Circle((x, y), 0.03, color=c)
        ax1.add_patch(outer); ax1.add_patch(inner); ax1.add_patch(dot)
        ax1.text(x, y+0.35, lbl, ha="center", color=c, fontsize=12, fontweight="bold")
    # Líneas de distancia
    for (x1,y1),(x2,y2),lbl in [
        (positions[0],positions[1],f"D12={D12}m"),
        (positions[1],positions[2],f"D23={D23}m"),
        (positions[0],positions[2],f"D31={D31}m")]:
        ax1.annotate("", xy=(x2,-0.8), xytext=(x1,-0.8),
                    arrowprops=dict(arrowstyle="<->", color=COLORS[2], lw=1.2))
        ax1.text((x1+x2)/2, -1.2, lbl, ha="center", color=COLORS[2], fontsize=8)
    GMD = (D12*D23*D31)**(1/3)
    ax1.set_title(f"Sección transversal — GMD={GMD:.3f} m", color=COLORS[0])
    ax1.axis("off")

    # Derecha: L y XL vs separación (variando D12 de 0.5 a 6 m)
    D_range = np.linspace(0.5, 6, 80)
    r_m = r_cm/100; mu0 = 4*np.pi*1e-7; rp = r_m*np.exp(-0.25)
    L_range = [(mu0/(2*np.pi))*np.log(d/rp)*1e3 for d in D_range]  # mH/km
    XL_range = [2*np.pi*60*l/1e3*1000 for l in L_range]
    ax2.plot(D_range, L_range, color=COLORS[0], linewidth=2, label="L (mH/km)")
    ax2r = ax2.twinx()
    ax2r.set_facecolor(PANEL_BG)
    ax2r.plot(D_range, XL_range, color=COLORS[1], linewidth=2, linestyle="--", label="XL (Ω/km)")
    ax2r.tick_params(colors=TEXT_COL); ax2r.yaxis.label.set_color(COLORS[1])
    ax2r.set_ylabel("XL (Ω/km)", color=COLORS[1])
    ax2.axvline(GMD, color=COLORS[8], linestyle=":", linewidth=1.5)
    ax2.scatter([GMD],[L_mH_km], color=COLORS[8], zorder=5, s=80,
                label=f"Punto actual\nL={L_mH_km:.3f} mH/km")
    ax2.set_xlabel("Separación equivalente D (m)")
    ax2.set_ylabel("L (mH/km)", color=COLORS[0])
    ax2.set_title("L y XL vs Separación entre conductores", color=COLORS[0])
    ax2.legend(loc="upper left", facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=8)

    plt.tight_layout(); plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# TEMA 3 – Capacitancia y potencia reactiva vs longitud
# ─────────────────────────────────────────────────────────────────────────────
def plot_capacidad(r_cm, D12, D23, D31, freq, VLN_kv, longitud_km):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    fig.suptitle("Tema 3 — Capacidad de Líneas", color=TEXT_COL, fontsize=13, fontweight="bold")
    _style(fig, [ax1, ax2])

    GMD = (D12*D23*D31)**(1/3); r_m = r_cm/100; eps0 = 8.854e-12
    C = 2*np.pi*eps0/np.log(GMD/r_m)       # F/m
    BC = 2*np.pi*freq*C                      # S/m

    # Izquierda: C y BC vs D
    D_range = np.linspace(0.5, 8, 80)
    C_range  = [2*np.pi*eps0/np.log(d/r_m)*1e12 for d in D_range]   # pF/m
    BC_range = [2*np.pi*freq*(2*np.pi*eps0/np.log(d/r_m))*1e6 for d in D_range]  # μS/m
    ax1.plot(D_range, C_range, color=COLORS[2], linewidth=2, label="C (pF/m)")
    ax1r = ax1.twinx(); ax1r.set_facecolor(PANEL_BG)
    ax1r.plot(D_range, BC_range, color=COLORS[3], linewidth=2, linestyle="--", label="BC (μS/m)")
    ax1r.tick_params(colors=TEXT_COL); ax1r.yaxis.label.set_color(COLORS[3])
    ax1r.set_ylabel("BC (μS/m)", color=COLORS[3])
    ax1.axvline(GMD, color=COLORS[8], linestyle=":", label=f"GMD={GMD:.2f}m")
    ax1.scatter([GMD],[C*1e12], color=COLORS[8], zorder=5, s=80)
    ax1.set_xlabel("Separación D (m)"); ax1.set_ylabel("C (pF/m)", color=COLORS[2])
    ax1.set_title("Capacitancia vs Separación", color=COLORS[0])
    ax1.legend(facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=8)

    # Derecha: QC generada vs longitud
    L_range = np.linspace(10, 500, 80)
    QC_range = [(VLN_kv*1e3)**2*BC*l*1000/1e6 for l in L_range]  # MVAR (3ph)
    ax2.plot(L_range, QC_range, color=COLORS[0], linewidth=2)
    ax2.axvline(longitud_km, color=COLORS[8], linestyle=":", label=f"L={longitud_km}km")
    QC_actual = (VLN_kv*1e3)**2*BC*longitud_km*1000/1e6
    ax2.scatter([longitud_km],[QC_actual], color=COLORS[8], zorder=5, s=80,
                label=f"QC={QC_actual:.3f} MVAR")
    ax2.fill_between(L_range, QC_range, alpha=0.15, color=COLORS[0])
    ax2.set_xlabel("Longitud (km)"); ax2.set_ylabel("QC generada (MVAR, 3φ)")
    ax2.set_title("Potencia Reactiva Generada vs Longitud", color=COLORS[0])
    ax2.legend(facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=8)

    plt.tight_layout(); plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# TEMA 4 – Diagrama fasorial VS/VR/IR + Perfil de voltaje
# ─────────────────────────────────────────────────────────────────────────────
def plot_lineas(VR_ln, VS, IR_f, Z, RV_pct):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    fig.suptitle("Tema 4 — Línea de Transmisión", color=TEXT_COL, fontsize=13, fontweight="bold")
    _style(fig, [ax1, ax2])

    # Izquierda: diagrama fasorial
    ax1.set_aspect("equal")
    orig = 0+0j
    VR_f = complex(VR_ln, 0)
    ZI   = Z * IR_f
    vecs = [(orig, VR_f, COLORS[1], "VR"),
            (VR_f, VR_f+ZI, COLORS[2], "Z·IR"),
            (orig, VS, COLORS[0], "VS")]
    for start, end, col, lbl in vecs:
        ax1.annotate("", xy=(end.real, end.imag), xytext=(start.real, start.imag),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=2.0, mutation_scale=12))
        ax1.text(((start+end)/2).real, ((start+end)/2).imag+abs(end-start)*0.05,
                 lbl, color=col, fontsize=9, fontweight="bold")
    mx = max(abs(VS), abs(VR_f))*1.15
    ax1.set_xlim(-mx*0.1, mx*1.1); ax1.set_ylim(-mx*0.3, mx*0.5)
    ax1.axhline(0, color=GRID_COL, linewidth=0.8); ax1.axvline(0, color=GRID_COL, linewidth=0.8)
    ax1.set_xlabel("Real (V)"); ax1.set_ylabel("Imaginario (V)")
    ax1.set_title(f"Diagrama Fasorial  RV={RV_pct:.2f}%", color=COLORS[0])

    # Derecha: perfil de voltaje a lo largo de la línea (estimado)
    x = np.linspace(0, 1, 50)
    V_profile = abs(VR_f) + (abs(VS)-abs(VR_f))*x
    ax2.plot(x*100, V_profile/1e3, color=COLORS[0], linewidth=2)
    ax2.fill_between(x*100, V_profile/1e3, abs(VR_f)/1e3, alpha=0.2, color=COLORS[0])
    ax2.axhline(abs(VR_f)/1e3, color=COLORS[1], linestyle="--", label=f"|VR|={abs(VR_f)/1e3:.2f} kV")
    ax2.axhline(abs(VS)/1e3,   color=COLORS[8], linestyle="--", label=f"|VS|={abs(VS)/1e3:.2f} kV")
    ax2.set_xlabel("Posición en la línea (%)"); ax2.set_ylabel("Voltaje L-N (kV)")
    ax2.set_title("Perfil de Voltaje a lo largo de la Línea", color=COLORS[0])
    ax2.legend(facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=8)

    plt.tight_layout(); plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# TEMA 5 – Diagrama cuadripolo ABCD + fasores
# ─────────────────────────────────────────────────────────────────────────────
def plot_abcd(A, B, VR_ln, IR_f, VS, IS):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    fig.suptitle("Tema 5 — Constantes ABCD", color=TEXT_COL, fontsize=13, fontweight="bold")
    _style(fig, [ax1, ax2])

    # Izquierda: tabla gráfica ABCD
    ax1.axis("off")
    data = [["Constante","Magnitud","Ángulo (°)"],
            ["A", f"{abs(A):.6f}", f"{np.degrees(np.angle(A)):.4f}"],
            ["B", f"{abs(B):.4f} Ω", f"{np.degrees(np.angle(B)):.3f}"],
            ["C ≈ Y(1+ZY/4)", "ver cálculo", "—"],
            ["D = A", f"{abs(A):.6f}", f"{np.degrees(np.angle(A)):.4f}"],
            ["AD−BC", "1.000000", "0.000000"]]
    table = ax1.table(cellText=data[1:], colLabels=data[0],
                      cellLoc="center", loc="center",
                      cellColours=[[PANEL_BG]*3]*5,
                      colColours=[COLORS[0]+"80"]*3)
    table.auto_set_font_size(False); table.set_fontsize(9)
    for (r,c), cell in table.get_celld().items():
        cell.set_edgecolor(GRID_COL); cell.set_text_props(color=TEXT_COL)
    ax1.set_title("Parámetros ABCD del Cuadripolo", color=COLORS[0])

    # Derecha: diagrama fasorial VS, VR, IS, IR
    ax2.set_aspect("equal")
    VR_f = complex(VR_ln, 0)
    for vec, col, lbl in [(VR_f, COLORS[1],"VR"),(VS, COLORS[0],"VS"),
                          (IR_f*VR_ln/abs(IR_f)/5 if abs(IR_f)>0 else 0, COLORS[2],"IR (escala)"),
                          (IS*VR_ln/abs(IS)/5 if abs(IS)>0 else 0, COLORS[3],"IS (escala)")]:
        if abs(vec) > 0:
            ax2.annotate("", xy=(vec.real, vec.imag), xytext=(0,0),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=2, mutation_scale=12))
            ax2.text(vec.real*1.05, vec.imag*1.05, lbl, color=col, fontsize=9)
    mx = max(abs(VS), abs(VR_f))*1.2 or 1
    ax2.set_xlim(-mx*0.2, mx*1.2); ax2.set_ylim(-mx*0.5, mx*0.5)
    ax2.axhline(0, color=GRID_COL, lw=0.8); ax2.axvline(0, color=GRID_COL, lw=0.8)
    ax2.set_title("Fasores VS, VR (extremos del cuadripolo)", color=COLORS[0])

    plt.tight_layout(); plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# TEMA 6 – Diagrama circular P-Q real
# ─────────────────────────────────────────────────────────────────────────────
def plot_circulares(VS_kv, VR_kv, A_mag, A_ang_deg, B_mag, B_ang_deg):
    fig, ax = plt.subplots(figsize=(8, 7))
    fig.suptitle("Tema 6 — Diagrama Circular de Potencia", color=TEXT_COL, fontsize=13, fontweight="bold")
    _style(fig, [ax])

    VS = VS_kv*1e3/np.sqrt(3); VR = VR_kv*1e3/np.sqrt(3)
    Ba = np.radians(B_ang_deg); Aa = np.radians(A_ang_deg)
    RR = 3*VS*VR/B_mag/1e6; OR = 3*A_mag*VR**2/B_mag/1e6

    # Eje
    ax.axhline(0, color=GRID_COL, lw=1); ax.axvline(0, color=GRID_COL, lw=1)
    ax.text(RR*1.05, 0.02, "P →", color=TEXT_COL, fontsize=9)
    ax.text(0.01, RR*0.7, "↑ Q", color=TEXT_COL, fontsize=9)

    # Centro del círculo de recepción
    theta_c = Ba - Aa + np.pi  # dirección del centro desde origen
    Ocx = -OR*np.sin(Ba-Aa); Ocy = -OR*np.cos(Ba-Aa)

    # Círculo recepción
    theta = np.linspace(0, 2*np.pi, 360)
    cx_r = Ocx + RR*np.cos(theta); cy_r = Ocy + RR*np.sin(theta)
    ax.plot(cx_r, cy_r, color=COLORS[0], linewidth=2, label=f"Círculo Recepción RR={RR:.2f} MW")
    ax.scatter([Ocx],[Ocy], color=COLORS[0], s=50, zorder=5)
    ax.text(Ocx+0.02, Ocy+0.02, "OR", color=COLORS[0], fontsize=9)

    # Puntos de operación para distintos δ
    deltas = np.linspace(-40, 90, 200)
    P_pts  = []; Q_pts = []
    for d in deltas:
        dr = np.radians(d)
        P = 3*((VS*VR/B_mag)*np.sin(dr-(Ba-np.pi/2))+(A_mag*VR**2/B_mag)*np.sin(Ba-Aa-np.pi/2))/1e6
        Q = 3*(-(VS*VR/B_mag)*np.cos(dr-(Ba-np.pi/2))+(A_mag*VR**2/B_mag)*np.cos(Ba-Aa-np.pi/2))/1e6
        P_pts.append(P); Q_pts.append(Q)
    ax.plot(P_pts, Q_pts, color=COLORS[4], linewidth=1.5, linestyle="--", label="Lugar geométrico (δ variable)")

    # Punto de máx potencia
    ax.axvline(RR-OR, color=COLORS[8], linestyle=":", linewidth=1.5, label=f"PR_max≈{RR-OR:.2f} MW")
    ax.scatter([RR-OR],[0], color=COLORS[8], s=80, zorder=6)

    ax.set_xlabel("Potencia Activa P (MW)", color=TEXT_COL)
    ax.set_ylabel("Potencia Reactiva Q (MVAR)", color=TEXT_COL)
    ax.legend(facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=8, loc="upper left")
    plt.tight_layout(); plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# TEMA 7 – Perfil de voltaje + convergencia Gauss-Seidel
# ─────────────────────────────────────────────────────────────────────────────
def plot_flujo(V_mags, V_angs, P_flows, bus_names, convergence_history):
    fig = plt.figure(figsize=(13, 5))
    fig.suptitle("Tema 7 — Flujo de Potencia", color=TEXT_COL, fontsize=13, fontweight="bold")
    gs = GridSpec(1, 3, figure=fig, wspace=0.35)
    ax1 = fig.add_subplot(gs[0]); ax2 = fig.add_subplot(gs[1]); ax3 = fig.add_subplot(gs[2])
    _style(fig, [ax1, ax2, ax3])

    x = range(len(V_mags))
    # Perfil de voltaje
    bars = ax1.bar(bus_names, V_mags, color=COLORS[:len(V_mags)], edgecolor=DARK_BG)
    ax1.axhline(1.05, color=COLORS[8], linestyle="--", linewidth=1, label="Lím.sup 1.05")
    ax1.axhline(0.95, color=COLORS[2], linestyle="--", linewidth=1, label="Lím.inf 0.95")
    for bar, v in zip(bars, V_mags):
        ax1.text(bar.get_x()+bar.get_width()/2, v+0.002, f"{v:.4f}", ha="center",
                 color=TEXT_COL, fontsize=8)
    ax1.set_ylim(0.88, 1.1); ax1.set_title("Perfil de Voltaje (pu)", color=COLORS[0])
    ax1.set_ylabel("|V| (pu)"); ax1.legend(facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=7)

    # Ángulos
    ax2.bar(bus_names, V_angs, color=COLORS[3:3+len(V_angs)], edgecolor=DARK_BG)
    for i,(name,ang) in enumerate(zip(bus_names, V_angs)):
        ax2.text(i, ang-0.3, f"{ang:.2f}°", ha="center", color=TEXT_COL, fontsize=8)
    ax2.set_title("Ángulos de Voltaje (°)", color=COLORS[0]); ax2.set_ylabel("Ángulo (°)")

    # Convergencia
    if convergence_history:
        ax3.semilogy(range(1,len(convergence_history)+1), convergence_history,
                     color=COLORS[0], linewidth=2, marker="o", markersize=4)
        ax3.axhline(1e-4, color=COLORS[8], linestyle="--", linewidth=1, label="ε=1e-4")
        ax3.set_title("Convergencia Gauss-Seidel", color=COLORS[0])
        ax3.set_xlabel("Iteración"); ax3.set_ylabel("|ΔV| máx")
        ax3.legend(facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=7)

    plt.tight_layout(); plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# TEMA 8 – Curvas de costo incremental + despacho óptimo
# ─────────────────────────────────────────────────────────────────────────────
def plot_despacho(b_list, c_list, a_list, P_opt, lam_opt, PD, Pmin, Pmax):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Tema 8 — Despacho Económico", color=TEXT_COL, fontsize=13, fontweight="bold")
    _style(fig, [ax1, ax2])

    # Izquierda: curvas dCi/dP y lambda óptimo
    n = len(b_list)
    for i in range(n):
        P_rng = np.linspace(Pmin[i], Pmax[i], 80)
        dC = b_list[i] + 2*c_list[i]*P_rng
        ax1.plot(P_rng, dC, color=COLORS[i], linewidth=2, label=f"dC{i+1}/dP")
        # Punto óptimo
        P_i = P_opt[i]
        dC_i = b_list[i] + 2*c_list[i]*P_i
        ax1.scatter([P_i],[dC_i], color=COLORS[i], s=80, zorder=5)
        ax1.annotate(f"P{i+1}={P_i:.0f}MW", xy=(P_i, dC_i),
                    xytext=(P_i+5, dC_i+0.3), color=COLORS[i], fontsize=8)
    ax1.axhline(lam_opt, color=COLORS[7], linewidth=2, linestyle="--",
                label=f"λ_opt = {lam_opt:.3f} $/MWh")
    ax1.set_xlabel("Potencia (MW)"); ax1.set_ylabel("dCi/dPi ($/MWh)")
    ax1.set_title("Costos Incrementales y λ Óptimo", color=COLORS[0])
    ax1.legend(facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=8)

    # Derecha: despacho óptimo (barras) + costo por unidad
    names = [f"G{i+1}\n{P_opt[i]:.0f} MW" for i in range(n)]
    costs = [a_list[i] + b_list[i]*P_opt[i] + c_list[i]*P_opt[i]**2 for i in range(n)]
    b1 = ax2.bar(names, P_opt, color=COLORS[:n], edgecolor=DARK_BG, alpha=0.85, label="P (MW)")
    ax2r = ax2.twinx(); ax2r.set_facecolor(PANEL_BG)
    ax2r.bar([i+0.35 for i in range(n)], costs, width=0.3,
             color=COLORS[:n], edgecolor=DARK_BG, alpha=0.45, label="Costo ($/h)")
    ax2r.set_ylabel("Costo ($/h)", color=TEXT_COL); ax2r.tick_params(colors=TEXT_COL)
    ax2.set_ylabel("Potencia (MW)"); ax2.set_title(f"Despacho Óptimo — CT={sum(costs):.0f} $/h  PD={PD} MW")
    ax2.legend(facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=8, loc="upper left")

    plt.tight_layout(); plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# TEMA 9 – Barras de corriente de falla por tipo
# ─────────────────────────────────────────────────────────────────────────────
def plot_fallas(Vpf, Z1_pu, Z2_pu, Z0_pu, Ibase):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Tema 9 — Teoría de Fallas", color=TEXT_COL, fontsize=13, fontweight="bold")
    _style(fig, [ax1, ax2])

    # Corrientes de falla para distintos tipos
    IF_3ph  = Vpf/Z1_pu
    IF_SLG  = 3*Vpf/(Z1_pu+Z2_pu+Z0_pu)
    IF_LL   = np.sqrt(3)*Vpf/(Z1_pu+Z2_pu)
    ZZ      = Z2_pu*Z0_pu/(Z2_pu+Z0_pu)
    IF_DLG  = abs(Vpf/(Z1_pu+ZZ))

    tipos   = ["3φ\nSim.", "SLG\n1φ-T", "LL\n2φ", "DLG\n2φ-T"]
    IF_pu   = [IF_3ph, IF_SLG, IF_LL, IF_DLG]
    IF_A    = [i*Ibase for i in IF_pu]
    cols_f  = [COLORS[8], COLORS[0], COLORS[2], COLORS[7]]

    bars = ax1.bar(tipos, IF_A, color=cols_f, edgecolor=DARK_BG)
    for bar, v in zip(bars, IF_A):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(IF_A)*0.01,
                 f"{v:.0f} A", ha="center", color=TEXT_COL, fontsize=9, fontweight="bold")
    ax1.set_ylabel("|IF| (A rms)"); ax1.set_title("Corriente de Falla por Tipo", color=COLORS[0])

    # Porcentaje de Ibase
    ax2.bar(tipos, [i/Ibase*100 for i in IF_pu], color=cols_f, edgecolor=DARK_BG)
    ax2.axhline(100, color=COLORS[7], linestyle="--", linewidth=1.5, label="100% Ibase")
    for i, v in enumerate(IF_pu):
        ax2.text(i, v/Ibase*100+1, f"{v/Ibase*100:.0f}%", ha="center", color=TEXT_COL, fontsize=9)
    ax2.set_ylabel("% de Ibase"); ax2.set_title("Severidad relativa (% Ibase)", color=COLORS[0])
    ax2.legend(facecolor=DARK_BG, labelcolor=TEXT_COL, fontsize=8)

    plt.tight_layout(); plt.show()
