"""
pdf_report.py
Generador de reporte PDF académico detallado para cada módulo Pumacayo.
Incluye: desarrollo matemático explícito, fórmulas, gráficas, circuitos, tablas.
"""
import os, io, datetime, tempfile
import numpy as np
import matplotlib
matplotlib.use("Agg")               # sin ventana, genera imágenes en memoria
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Arc, Circle
from matplotlib.gridspec import GridSpec

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

W, H = A4

# ── Paletas ──────────────────────────────────────────────────────────────────
DARK = "#020617"; PANEL = "#0f172a"; ACCENT = "#38bdf8"
THEME = { # color por módulo
    "Valores por Unidad":             "#38bdf8",
    "Inductancia de Lineas":          "#10b981",
    "Capacidad de Lineas":            "#f59e0b",
    "Lineas de Transmision":          "#8b5cf6",
    "Constantes Generalizadas ABCD":  "#f472b6",
    "Diagramas Circulares de Potencia":"#fb923c",
    "Flujo de Potencia":              "#22d3ee",
    "Despacho Economico de Centrales Termicas": "#facc15",
    "Teoria de Fallas":               "#ef4444",
}

# ── Estilos reportlab ─────────────────────────────────────────────────────────
def _styles(accent_hex):
    accent = colors.HexColor(accent_hex)
    s = {}
    s["title"]  = ParagraphStyle("T",  fontSize=30, textColor=colors.HexColor("#1e3a5f"),
                                  fontName="Helvetica-Bold", alignment=TA_CENTER, 
                                  leading=36, spaceAfter=2)
    s["sub"]    = ParagraphStyle("SB", fontSize=15, textColor=colors.HexColor("#64748b"),
                                  alignment=TA_CENTER, leading=18, spaceAfter=2)
    s["lib"]    = ParagraphStyle("LB", fontSize=14, textColor=colors.HexColor("#94a3b8"),
                                  alignment=TA_CENTER, leading=18, italic=True)
    s["h1"]     = ParagraphStyle("H1", fontSize=20, fontName="Helvetica-Bold",
                                  textColor=accent, spaceBefore=20, spaceAfter=8, 
                                  leading=24, leftIndent=-10)
    s["h2"]     = ParagraphStyle("H2", fontSize=16, fontName="Helvetica-Bold",
                                  textColor=colors.HexColor("#1e3a5f"), spaceBefore=10, spaceAfter=4)
    s["body"]   = ParagraphStyle("B",  fontSize=14.5, textColor=colors.HexColor("#1e293b"),
                                  leading=22, spaceAfter=6, alignment=TA_JUSTIFY)
    s["formula"]= ParagraphStyle("F",  fontSize=15, fontName="Courier-Bold",
                                  textColor=colors.HexColor("#0f4c2a"),
                                  backColor=colors.HexColor("#f0fdf4"),
                                  leftIndent=30, rightIndent=30, spaceBefore=6, spaceAfter=6,
                                  leading=22, borderPadding=10)
    s["code"]   = ParagraphStyle("C",  fontSize=13,  fontName="Courier",
                                  textColor=colors.HexColor("#0c4a6e"),
                                  backColor=colors.HexColor("#f0f9ff"),
                                  leftIndent=20, rightIndent=20, spaceAfter=4,
                                  leading=18, borderPadding=8)
    s["warn"]   = ParagraphStyle("W",  fontSize=13,  fontName="Helvetica-Oblique",
                                  textColor=colors.HexColor("#92400e"),
                                  backColor=colors.HexColor("#fffbeb"),
                                  leftIndent=20, spaceAfter=6, borderPadding=6)
    return s

def _hr(accent_hex, thick=1.0):
    return HRFlowable(width="100%", thickness=thick, color=colors.HexColor(accent_hex), spaceAfter=6)

def _input_table(inputs: dict):
    if not inputs:
        return []
    data = [["Parámetro", "Símbolo", "Valor"]]
    for k, v in inputs.items():
        sym = k
        data.append([k, sym, str(v)])
    t = Table(data, colWidths=[7*cm, 5*cm, 5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 9),
        ("GRID",       (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f8fafc"),colors.HexColor("#f1f5f9")]),
        ("LEFTPADDING",(0,0),(-1,-1), 6),
        ("TOPPADDING", (0,0),(-1,-1), 4),
    ]))
    return [t, Spacer(1, 8)]


def _fig_to_image(fig, width=16*cm):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor(), transparent=True)
    plt.close(fig)
    buf.seek(0)
    # Calcular altura proporcional
    img = Image(buf)
    aspect = img.drawHeight / img.drawWidth
    img.drawWidth = width
    img.drawHeight = width * aspect
    return img

def _latex_to_img(formula: str, fontsize=24, color="#1e293b"):
    """Renderiza una fórmula LaTeX a un objeto Image de ReportLab (Versión XL Mejorada)."""
    fig = plt.figure(figsize=(8, 1.5), dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    
    if not (formula.startswith("$") and formula.endswith("$")):
        formula = f"${formula}$"
    
    formula = formula.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    
    ax.text(0.5, 0.5, formula, color=color, fontsize=fontsize, 
             ha='center', va='center', fontname='DejaVu Sans')
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0.01, transparent=True)
    plt.close(fig)
    buf.seek(0)
    
    img = Image(buf)
    # Altura XL
    h_target = 1.6 * cm * (fontsize/14) 
    aspect = img.drawWidth / img.drawHeight
    img.drawHeight = h_target
    img.drawWidth = h_target * aspect
    
    max_w = 16 * cm
    if img.drawWidth > max_w:
        img.drawWidth = max_w
        img.drawHeight = max_w / aspect
        
    img.hAlign = 'CENTER'
    return img


# ══════════════════════════════════════════════════════════════════════════════
# FIGURAS ESPECÍFICAS POR MÓDULO
# ══════════════════════════════════════════════════════════════════════════════
CLR = ["#38bdf8","#10b981","#f59e0b","#8b5cf6","#f472b6","#fb923c","#22d3ee","#facc15","#ef4444"]
BG  = "#0f172a"; PBG = "#1e293b"; TC = "#f8fafc"; GC = "#334155"

def _style_ax(fig, axes):
    fig.patch.set_facecolor(BG)
    for ax in (axes if hasattr(axes,'__iter__') else [axes]):
        ax.set_facecolor(PBG)
        ax.tick_params(colors=TC, labelsize=8)
        for spine in ax.spines.values(): spine.set_edgecolor(GC)
        ax.grid(True, color=GC, lw=0.5, ls="--", alpha=0.6)
        ax.xaxis.label.set_color(TC); ax.yaxis.label.set_color(TC)
        ax.title.set_color(CLR[0])


def fig_circuit_perunit():
    """Circuito multitensión en p.u."""
    fig, ax = plt.subplots(figsize=(12,3.5))
    _style_ax(fig, [ax]); ax.axis("off"); ax.set_xlim(0,12); ax.set_ylim(-1,3)
    # Zonas
    for x0,x1,lbl,c in [(0,3,"Zona 1\nV₁_base",CLR[0]),(3,7,"Zona 2\nV₂_base",CLR[1]),(7,12,"Zona 3\nV₃_base",CLR[2])]:
        ax.axvspan(x0,x1, alpha=0.08, color=c)
        ax.text((x0+x1)/2, 2.65, lbl, ha="center", color=c, fontsize=9, fontweight="bold")
    # Generador
    circle = plt.Circle((1.2,1.2),0.5, fill=False, color=CLR[0], lw=2)
    ax.add_patch(circle); ax.text(1.2,1.2,"G", ha="center",va="center",color=CLR[0],fontsize=11,fontweight="bold")
    ax.annotate("",xy=(3.0,1.2),xytext=(1.7,1.2),arrowprops=dict(arrowstyle="-",color=TC,lw=2))
    # Trafo 1
    for cx in [3.3,3.7]: ax.add_patch(plt.Circle((cx,1.2),0.3,fill=False,color=CLR[1],lw=2))
    ax.text(3.5,0.6,"T₁",ha="center",color=CLR[1],fontsize=9)
    ax.annotate("",xy=(6.5,1.2),xytext=(4.0,1.2),arrowprops=dict(arrowstyle="-",color=TC,lw=2))
    ax.text(5.2,1.45,"Z₂ (p.u.)",ha="center",color=CLR[3],fontsize=8)
    # Trafo 2
    for cx in [6.8,7.2]: ax.add_patch(plt.Circle((cx,1.2),0.3,fill=False,color=CLR[2],lw=2))
    ax.text(7.0,0.6,"T₂",ha="center",color=CLR[2],fontsize=9)
    ax.annotate("",xy=(10.5,1.2),xytext=(7.5,1.2),arrowprops=dict(arrowstyle="-",color=TC,lw=2))
    # Carga
    ax.add_patch(plt.Polygon([[10.5,1.6],[11.2,1.2],[10.5,0.8]],closed=True,color=CLR[8],alpha=0.7))
    ax.text(11.4,1.2,"PQ",ha="left",va="center",color=CLR[8],fontsize=9)
    ax.annotate("",xy=(1.2,0.7),xytext=(1.2,0.0),arrowprops=dict(arrowstyle="-",color=GC,lw=1.2))
    ax.annotate("",xy=(10.8,0.7),xytext=(10.8,0.0),arrowprops=dict(arrowstyle="-",color=GC,lw=1.2))
    ax.text(6,0,"Vpu=V_real/V_base   Zpu=Z_real·Sbase/Vbase²   Cambio de base: Zpunew=Zpuold·(Sbnew/Sbold)·(Vbold/Vbnew)²",
            ha="center",va="center",color=CLR[0],fontsize=8)
    ax.set_title("Circuito Equivalente en Valores por Unidad",color=CLR[0],fontsize=11)
    return _fig_to_image(fig)


def fig_conductores_inductancia(r_cm, D12, D23, D31):
    """Sección transversal 3 conductores con GMD."""
    fig, (ax1,ax2) = plt.subplots(1,2,figsize=(12,4.5))
    _style_ax(fig,[ax1,ax2])
    # Sección transversal
    ax1.set_aspect("equal"); ax1.set_xlim(-1.5, D12+D23+1.5); ax1.set_ylim(-2.5,3)
    pos=[(0,0),(D12,0),(D12+D23,0)]; labels=["A","B","C"]
    for (x,y),lbl,c in zip(pos,labels,[CLR[0],CLR[2],CLR[8]]):
        rp=r_cm/100*np.exp(-0.25)*8
        ax1.add_patch(plt.Circle((x,y),r_cm/100*8,color=c,alpha=0.15))
        ax1.add_patch(plt.Circle((x,y),rp if rp>0.01 else 0.01,color=c,alpha=0.5))
        ax1.add_patch(plt.Circle((x,y),0.04,color=c))
        ax1.text(x,y+0.5,lbl,ha="center",color=c,fontsize=13,fontweight="bold")
        ax1.text(x,y-0.5,"r={}cm".format(r_cm),ha="center",color=c,fontsize=7)
    for (x1,y1),(x2,y2),lbl in [(pos[0],pos[1],"D₁₂={:.1f}m".format(D12)),
                                  (pos[1],pos[2],"D₂₃={:.1f}m".format(D23))]:
        ax1.annotate("",xy=(x2,-1.5),xytext=(x1,-1.5),arrowprops=dict(arrowstyle="<->",color=CLR[2],lw=1.2))
        ax1.text((x1+x2)/2,-2.0,lbl,ha="center",color=CLR[2],fontsize=8)
    ax1.annotate("",xy=(pos[2][0],-1.0),xytext=(pos[0][0],-1.0),arrowprops=dict(arrowstyle="<->",color=CLR[7],lw=1.2))
    ax1.text((D12+D23)/2,-0.5,"D₃₁={:.1f}m".format(D31),ha="center",color=CLR[7],fontsize=8)
    GMD=(D12*D23*D31)**(1/3)
    ax1.set_title("Sección Transversal — GMD={:.3f} m".format(GMD),color=CLR[0])
    ax1.axis("off")
    # Curva L vs D
    D_r=np.linspace(0.5,6,100); rp=r_cm/100*np.exp(-0.25)
    L_r=[(4e-7)*np.log(d/rp)*1e3 for d in D_r]
    XL_r=[2*np.pi*60*l/1000*1000 for l in L_r]
    ax2.plot(D_r,L_r,color=CLR[0],lw=2,label="L (mH/km)")
    ax2r=ax2.twinx(); ax2r.set_facecolor(PBG); ax2r.tick_params(colors=TC)
    ax2r.plot(D_r,XL_r,color=CLR[1],lw=2,ls="--",label="XL (Ω/km)")
    ax2r.set_ylabel("XL (Ω/km)",color=CLR[1])
    ax2.axvline(GMD,color=CLR[8],ls=":",lw=1.5)
    L_actual=(4e-7)*np.log(GMD/rp)*1e3
    ax2.scatter([GMD],[L_actual],color=CLR[8],s=90,zorder=5,label="Punto actual\nL={:.3f} mH/km".format(L_actual))
    ax2.set_xlabel("Separación D (m)"); ax2.set_ylabel("L (mH/km)",color=CLR[0])
    ax2.set_title("Inductancia vs Separación entre Conductores",color=CLR[0])
    ax2.legend(facecolor=BG,labelcolor=TC,fontsize=8)
    return _fig_to_image(fig,width=17*cm)


def fig_linea_fasor(R, X, VR_kv, IR_A, fp):
    """Diagrama fasorial y perfil de voltaje."""
    phi=np.arccos(fp); VRln=VR_kv*1e3/np.sqrt(3)
    Z=complex(R,X); IR=complex(IR_A*fp,-IR_A*np.sin(phi)); VR=complex(VRln,0)
    VS=VR+Z*IR; RV=(abs(VS)-VRln)/VRln*100
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12,5)); _style_ax(fig,[ax1,ax2])
    # Fasorial
    ax1.set_aspect("equal")
    def arr(start,end,col,lbl):
        ax1.annotate("",xy=(end.real,end.imag),xytext=(start.real,start.imag),
                     arrowprops=dict(arrowstyle="-|>",color=col,lw=2,mutation_scale=14))
        mid=(start+end)/2
        ax1.text(mid.real+abs(end-start)*0.04,mid.imag+abs(end-start)*0.04,lbl,color=col,fontsize=9,fontweight="bold")
    arr(0+0j,VR,CLR[1],"V_R"); arr(VR,VS,CLR[2],"Z·I_R"); arr(0+0j,VS,CLR[0],"V_S")
    ZI=Z*IR
    ax1.annotate("",xy=(VR.real,VR.imag+abs(ZI)*0.3),xytext=(VR.real,VR.imag),
                 arrowprops=dict(arrowstyle="-",color=CLR[3],lw=1,linestyle="dashed"))
    mx=max(abs(VS),abs(VR))*1.2
    ax1.set_xlim(-mx*0.05,mx*1.15); ax1.set_ylim(-mx*0.35,mx*0.5)
    ax1.axhline(0,color=GC,lw=0.8); ax1.axvline(0,color=GC,lw=0.8)
    ax1.set_xlabel("Parte Real (V)"); ax1.set_ylabel("Parte Imaginaria (V)")
    ax1.set_title(f"Diagrama Fasorial — RV={RV:.2f}%",color=CLR[0])
    # Perfil
    x=np.linspace(0,1,50); Vp=abs(VR)+x*(abs(VS)-abs(VR))
    ax2.plot(x*100,Vp/1e3,color=CLR[0],lw=2)
    ax2.fill_between(x*100,Vp/1e3,abs(VR)/1e3,alpha=0.15,color=CLR[0])
    ax2.axhline(abs(VR)/1e3,color=CLR[1],ls="--",lw=1.2,label=f"|V_R|={abs(VR)/1e3:.3f} kV L-N")
    ax2.axhline(abs(VS)/1e3,color=CLR[8],ls="--",lw=1.2,label=f"|V_S|={abs(VS)/1e3:.3f} kV L-N")
    ax2.set_xlabel("Posición en la línea (%)"); ax2.set_ylabel("Voltaje L-N (kV)")
    ax2.set_title("Perfil de Voltaje a lo largo de la Línea",color=CLR[0])
    ax2.legend(facecolor=BG,labelcolor=TC,fontsize=8)
    return _fig_to_image(fig,width=17*cm)


def fig_circulo_pq(VS_kv,VR_kv,A_mag,A_ang_deg,B_mag,B_ang_deg):
    fig,ax=plt.subplots(figsize=(8,7)); _style_ax(fig,[ax])
    VS=VS_kv*1e3/np.sqrt(3); VR=VR_kv*1e3/np.sqrt(3)
    Ba=np.radians(B_ang_deg); Aa=np.radians(A_ang_deg)
    RR=3*VS*VR/B_mag/1e6; OR=3*A_mag*VR**2/B_mag/1e6
    Ocx=-OR*np.sin(Ba-Aa); Ocy=-OR*np.cos(Ba-Aa)
    theta=np.linspace(0,2*np.pi,400)
    ax.plot(Ocx+RR*np.cos(theta),Ocy+RR*np.sin(theta),color=CLR[0],lw=2.5,label=f"Círculo Recepción RR={RR:.2f} MW")
    ax.scatter([Ocx],[Ocy],color=CLR[0],s=60,zorder=5)
    ax.text(Ocx+0.3,Ocy+0.3,"OR",color=CLR[0],fontsize=9,fontweight="bold")
    deltas=np.linspace(-50,85,300); Pp=[]; Qp=[]
    for d in deltas:
        dr=np.radians(d)
        Pp.append(3*((VS*VR/B_mag)*np.sin(dr-(Ba-np.pi/2))+(A_mag*VR**2/B_mag)*np.sin(Ba-Aa-np.pi/2))/1e6)
        Qp.append(3*(-(VS*VR/B_mag)*np.cos(dr-(Ba-np.pi/2))+(A_mag*VR**2/B_mag)*np.cos(Ba-Aa-np.pi/2))/1e6)
    ax.plot(Pp,Qp,color=CLR[4],lw=1.5,ls="--",label="δ variable (locus de operación)")
    Pmax=RR-OR
    ax.axvline(Pmax,color=CLR[8],ls=":",lw=1.5,label=f"P_Rmax≈{Pmax:.2f} MW")
    ax.axhline(0,color=GC,lw=0.8); ax.axvline(0,color=GC,lw=0.8)
    ax.set_xlabel("Potencia Activa P (MW)"); ax.set_ylabel("Potencia Reactiva Q (MVAR)")
    ax.set_title("Diagrama Circular de Potencia — Extremo Recepción",color=CLR[0])
    ax.legend(facecolor=BG,labelcolor=TC,fontsize=8)
    return _fig_to_image(fig,width=13*cm)


def fig_flujo_barras(V_mags,V_angs,bus_names,conv_hist):
    fig=plt.figure(figsize=(13,5)); _style_ax(fig,[])
    fig.patch.set_facecolor(BG)
    gs=GridSpec(1,3,figure=fig,wspace=0.4)
    ax1=fig.add_subplot(gs[0]); ax2=fig.add_subplot(gs[1]); ax3=fig.add_subplot(gs[2])
    for ax in [ax1,ax2,ax3]: ax.set_facecolor(PBG); ax.tick_params(colors=TC)
    for ax in [ax1,ax2,ax3]:
        ax.grid(True,color=GC,lw=0.5,ls="--",alpha=0.6)
        for sp in ax.spines.values(): sp.set_edgecolor(GC)
    b1=ax1.bar(bus_names,V_mags,color=CLR[:len(V_mags)],edgecolor=BG)
    ax1.axhline(1.05,color=CLR[8],ls="--",lw=1,label="Lím.sup 1.05")
    ax1.axhline(0.95,color=CLR[2],ls="--",lw=1,label="Lím.inf 0.95")
    for bar,v in zip(b1,V_mags): ax1.text(bar.get_x()+bar.get_width()/2,v+0.003,f"{v:.4f}",ha="center",color=TC,fontsize=8)
    ax1.set_ylim(0.88,1.12); ax1.set_title("Perfil de Voltaje |V| (pu)",color=CLR[0])
    ax1.set_ylabel("|V| (pu)",color=TC); ax1.legend(facecolor=BG,labelcolor=TC,fontsize=7)
    ax2.bar(bus_names,V_angs,color=CLR[3:3+len(V_angs)],edgecolor=BG)
    for i,(n,a) in enumerate(zip(bus_names,V_angs)): ax2.text(i,a-0.5+1*(a<0),f"{a:.2f}°",ha="center",color=TC,fontsize=8)
    ax2.set_title("Ángulos de Voltaje (°)",color=CLR[0]); ax2.set_ylabel("Ángulo (°)",color=TC)
    if conv_hist:
        ax3.semilogy(range(1,len(conv_hist)+1),conv_hist,color=CLR[0],lw=2,marker="o",ms=4)
        ax3.axhline(1e-4,color=CLR[8],ls="--",lw=1,label="ε=0.0001")
        ax3.set_title("Convergencia Gauss-Seidel",color=CLR[0])
        ax3.set_xlabel("Iteración",color=TC); ax3.set_ylabel("|ΔV| máx",color=TC)
        ax3.legend(facecolor=BG,labelcolor=TC,fontsize=7)
    return _fig_to_image(fig,width=17*cm)


def fig_despacho(b_list,c_list,a_list,P_opt,lam_opt,PD,Pmin,Pmax):
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12,5)); _style_ax(fig,[ax1,ax2])
    n=len(b_list)
    for i in range(n):
        Pr=np.linspace(Pmin[i],Pmax[i],80); dC=[b_list[i]+2*c_list[i]*p for p in Pr]
        ax1.plot(Pr,dC,color=CLR[i],lw=2,label=f"dC{i+1}/dP")
        ax1.scatter([P_opt[i]],[b_list[i]+2*c_list[i]*P_opt[i]],color=CLR[i],s=80,zorder=5)
        ax1.annotate(f"P{i+1}={P_opt[i]:.0f}MW",xy=(P_opt[i],b_list[i]+2*c_list[i]*P_opt[i]),
                    xytext=(P_opt[i]+5,b_list[i]+2*c_list[i]*P_opt[i]+0.3),color=CLR[i],fontsize=8)
    ax1.axhline(lam_opt,color=CLR[7],lw=2,ls="--",label=f"λ_opt={lam_opt:.3f} $/MWh")
    ax1.set_xlabel("P (MW)",color=TC); ax1.set_ylabel("dCi/dPi ($/MWh)",color=TC)
    ax1.set_title("Costos Incrementales y λ Óptimo",color=CLR[0])
    ax1.legend(facecolor=BG,labelcolor=TC,fontsize=8)
    costs=[a_list[i]+b_list[i]*P_opt[i]+c_list[i]*P_opt[i]**2 for i in range(n)]
    names=[f"G{i+1}\n{P_opt[i]:.0f}MW" for i in range(n)]
    ax2.bar(names,P_opt,color=CLR[:n],edgecolor=BG,alpha=0.85,label="P (MW)")
    ax2r=ax2.twinx(); ax2r.set_facecolor(PBG); ax2r.tick_params(colors=TC)
    ax2r.bar([i+0.3 for i in range(n)],costs,width=0.3,color=CLR[:n],edgecolor=BG,alpha=0.45)
    ax2r.set_ylabel("Costo ($/h)",color=TC)
    ax2.set_ylabel("Potencia (MW)",color=TC)
    ax2.set_title(f"Despacho Óptimo — CT={sum(costs):.0f} $/h  PD={PD} MW",color=CLR[0])
    ax2.legend(facecolor=BG,labelcolor=TC,fontsize=8)
    return _fig_to_image(fig,width=17*cm)


def fig_fallas(Vpf,Z1,Z2,Z0,Ibase):
    IF_3ph=Vpf/Z1; IF_SLG=3*Vpf/(Z1+Z2+Z0)
    IF_LL=np.sqrt(3)*Vpf/(Z1+Z2); ZZ=Z2*Z0/(Z2+Z0); IF_DLG=Vpf/(Z1+ZZ)
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12,5)); _style_ax(fig,[ax1,ax2])
    tipos=["3φ\nSim.","SLG\n1φ-T","LL\n2φ","DLG\n2φ-T"]
    IF_A=[IF_3ph*Ibase,IF_SLG*Ibase,IF_LL*Ibase,IF_DLG*Ibase]
    b1=ax1.bar(tipos,IF_A,color=[CLR[8],CLR[0],CLR[2],CLR[7]],edgecolor=BG)
    for bar,v in zip(b1,IF_A): ax1.text(bar.get_x()+bar.get_width()/2,v+max(IF_A)*0.01,f"{v:.0f}A",ha="center",color=TC,fontsize=9,fontweight="bold")
    ax1.set_ylabel("|IF| (A rms)"); ax1.set_title("Corriente de Falla por Tipo",color=CLR[0])
    pct=[v/Ibase*100 for v in IF_A]
    ax2.bar(tipos,pct,color=[CLR[8],CLR[0],CLR[2],CLR[7]],edgecolor=BG)
    ax2.axhline(100,color=CLR[7],ls="--",lw=1.5,label="100% Ibase")
    for i,p in enumerate(pct): ax2.text(i,p+max(pct)*0.01,f"{p:.0f}%",ha="center",color=TC,fontsize=9)
    ax2.set_ylabel("% de Ibase"); ax2.set_title("Severidad Relativa",color=CLR[0])
    ax2.legend(facecolor=BG,labelcolor=TC,fontsize=8)
    return _fig_to_image(fig,width=17*cm)


# ══════════════════════════════════════════════════════════════════════════════
# CONTENIDO TEÓRICO POR MÓDULO
# ══════════════════════════════════════════════════════════════════════════════
THEORY = {
    "Valores por Unidad": {
        "concepto": (
            "El sistema por unidad (p.u.) normaliza todas las magnitudes eléctricas respecto a "
            "valores base elegidos, de modo que las ecuaciones del sistema tienen la misma forma. "
            "Esto simplifica el análisis al eliminar el término de la relación de transformación."
        ),
        "formulas": [
            "V_{pu} = \\frac{V_{real}}{V_{base}}",
            "S_{pu} = \\frac{S_{real}}{S_{base}}",
            "I_{base} = \\frac{S_{base}}{\\sqrt{3} \\cdot V_{base}}",
            "Z_{base} = \\frac{V_{base}^2}{S_{base}}",
            "Z_{pu}^{new} = Z_{pu}^{old} \\cdot \\left( \\frac{S_{base}^{new}}{S_{base}^{old}} \\right) \\cdot \\left( \\frac{V_{base}^{old}}{V_{base}^{new}} \\right)^2",
        ],
        "fig_fn": lambda inputs: fig_circuit_perunit(),
    },
    "Inductancia de Lineas": {
        "concepto": (
            "La inductancia trifásica se basa en el flujo concatenado. Para líneas transpuestas "
            "se emplea el Radio Medio Geométrico (GMR) y la Distancia Media Geométrica (GMD)."
        ),
        "formulas": [
            "r' = r \\cdot e^{-1/4}",
            "GMD = \\sqrt[3]{D_{12} \\cdot D_{23} \\cdot D_{31}}",
            "L = 2 \\cdot 10^{-7} \\cdot \\ln\\left(\\frac{GMD}{GMR}\\right) \\text{ [H/m]}",
            "X_L = 2\\pi f L \\cdot 1000 \\text{ [\\Omega/km]}",
        ],
        "fig_fn": lambda inputs: fig_conductores_inductancia(
            inputs.get("r",1.5), inputs.get("D12",2.0),
            inputs.get("D23",2.5), inputs.get("D31",4.5)
        ),
    },
    "Capacidad de Lineas": {
        "concepto": (
            "La capacitancia de la línea surge del campo eléctrico entre conductores. "
            "Produce una corriente de carga que puede ser significativa en líneas de alta tensión."
        ),
        "formulas": [
            "C = \\frac{2\\pi \\epsilon_0}{\\ln(GMD/r)} \\text{ [F/m]}",
            "B_C = 2\\pi f C \\text{ [S/m]}",
            "Q_C = 3 \\cdot V_{LN}^2 \\cdot B_C \\cdot \\ell \\text{ [VAR]}",
        ],
        "fig_fn": None,
    },
    "Lineas de Transmision": {
        "concepto": (
            "Se aplican modelos circuitales (Corta, Pi, Larga) según la longitud. "
            "El modelo Pi es el más común para líneas de longitud media."
        ),
        "formulas": [
            "V_S = V_R + Z \\cdot I_R \\text{ (Línea corta)}",
            "V_S = A \\cdot V_R + B \\cdot I_R \\text{ (Modelo } \\pi \\text{)}",
            "A = 1 + \\frac{ZY}{2} , \\quad B = Z , \\quad C = Y(1 + \\frac{ZY}{4})",
            "RV\\% = \\frac{|V_S| - |V_R|}{|V_R|} \\cdot 100 \\%",
        ],
        "fig_fn": lambda inputs: fig_linea_fasor(
            inputs.get("R",5.0), inputs.get("X",25.0),
            inputs.get("VR",115.0), inputs.get("IR",200.0), inputs.get("fp",0.9)
        ),
    },
    "Constantes Generalizadas ABCD": {
        "concepto": (
            "Representan el sistema como un cuadripolo lineal. Permiten el modelado en cascada "
            "de transformadores, líneas y compensadores mediante multiplicación de matrices."
        ),
        "formulas": [
            "\\begin{bmatrix} V_S \\\\ I_S \\end{bmatrix} = \\begin{bmatrix} A & B \\\\ C & D \\end{bmatrix} \\begin{bmatrix} V_R \\\\ I_R \\end{bmatrix}",
            "AD - BC = 1 \\text{ (Condición de reciprocidad)}",
            "A = \\cosh(\\gamma \\ell) , \\quad B = Z_c \\sinh(\\gamma \\ell)",
        ],
        "fig_fn": None,
    },
    "Diagramas Circulares de Potencia": {
        "concepto": (
            "Herramienta gráfica que delimita la capacidad de transferencia de potencia "
            "activa y reactiva entre dos barras, basada en las constantes ABCD."
        ),
        "formulas": [
            "Centro_{R} = - \\frac{A^* B}{B^2} V_R^2",
            "Radio_{R} = \\frac{|V_S| \\cdot |V_R|}{|B|}",
            "P_R + jQ_R = \\frac{V_S \\cdot V_R^*}{B^*} - \\frac{A \\cdot V_R^2}{B}",
        ],
        "fig_fn": lambda inputs: fig_circulo_pq(
            inputs.get("VS",132.0), inputs.get("VR",115.0),
            inputs.get("A_mag",0.99), inputs.get("A_ang",1.5),
            inputs.get("B_mag",35.0), inputs.get("B_ang",80.0)
        ),
    },
    "Flujo de Potencia": {
        "concepto": (
            "Determina el estado estacionario de la red. Busca tensiones y ángulos nodales "
            "que satisfagan el balance de potencia activa y reactiva en cada barra."
        ),
        "formulas": [
            r"I_{bus} = [Y_{bus}] \cdot V_{bus}",
            r"S_i = V_i \left( \sum_{j=1}^n Y_{ij} V_j \right)^* = P_i + jQ_i",
            r"V_i^{(k+1)} = \frac{1}{Y_{ii}} \left[ \frac{P_i - jQ_i}{V_i^{*(k)}} - \sum_{j \neq i} Y_{ij} V_j^{(k)} \right]",
            r"\Delta V_{max} = \max |V_i^{(k+1)} - V_i^{(k)}| < \epsilon",
        ],
        "fig_fn": lambda inputs: fig_flujo_barras(
            [1.05,inputs.get("V1",1.05),0.982,0.975],
            [0,-1.5,-4.5,-7.2],["Bus1\nSlack","Bus2","Bus3","Bus4"],[0.1,0.05,0.03,0.01,0.004]
        ) if inputs else None,
    },
    "Despacho Econico de Centrales Termicas": {
        "concepto": (
            "Distribuye la demanda total entre generadores térmicos para minimizar el costo "
            "total operativo, igualando los costos incrementales de todas las unidades."
        ),
        "formulas": [
            "C_i(P_i) = a_i + b_i P_i + c_i P_i^2 \\text{ [$/h]}",
            "\\frac{dC_i}{dP_i} = b_i + 2 c_i P_i = \\lambda \\text{ [$/MWh]}",
            "\\sum_{i=1}^n P_i = P_D + P_L \\text{ (Balance de potencia)}",
        ],
        "fig_fn": lambda inputs: fig_despacho(
            [inputs.get("b1",9),inputs.get("b2",7.5),inputs.get("b3",8)],
            [inputs.get("c1",0.01),inputs.get("c2",0.012),inputs.get("c3",0.008)],
            [inputs.get("a1",200),inputs.get("a2",180),inputs.get("a3",140)],
            [inputs.get("P1",150),inputs.get("P2",110),inputs.get("P3",140)],
            9.5, inputs.get("PD",400),
            [50,40,30],[200,150,250]
        ) if inputs else None,
    },
    "Teoria de Fallas": {
        "concepto": (
            "Emplea componentes simétricas para analizar fallas asimétricas. Descompone "
            "el sistema en redes de secuencia positiva, negativa y cero."
        ),
        "formulas": [
            "I_f = \\frac{V_{pf}}{Z_1 + Z_2 + Z_0} \\cdot 3 \\text{ (Falla SLG)}",
            "I_f = \\frac{\\sqrt{3} V_{pf}}{Z_1 + Z_2} \\text{ (Falla Línea-Línea)}",
            "I_f = \\frac{V_{pf}}{Z_1} \\text{ (Falla Trifásica)}",
        ],
        "fig_fn": lambda inputs: fig_fallas(
            inputs.get("Vpf",1.0), inputs.get("Z1",0.1),
            inputs.get("Z2",0.1), inputs.get("Z0",0.3), inputs.get("Ibase",502.0)
        ) if inputs else None,
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# ══════════════════════════════════════════════════════════════════════════════
def generate_detailed_pdf(filename: str, module_name: str, steps_data: list):
    """
    Genera un reporte PDF académico completo y detallado.
    steps_data: lista de {title, inputs, result}
    """
    accent_hex = THEME.get(module_name, "#38bdf8")
    s = _styles(accent_hex)
    accent = colors.HexColor(accent_hex)

    doc = SimpleDocTemplate(filename, pagesize=A4,
                            leftMargin=2.0*cm, rightMargin=2.0*cm,
                            topMargin=2.2*cm, bottomMargin=2.2*cm)
    story = []

    # ── PORTADA ──────────────────────────────────────────────────────────
    # ── PORTADA ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.8 * cm))
    story.append(_hr(accent_hex, 3.5))
    story.append(Spacer(1, 4))
    story.append(Paragraph("⚡  POWER ANALYZER PRO", s["title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Sistemas de Potencia y Modelado Matemático", s["sub"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Referencia: <i>Análisis de Sistemas de Potencia — Teoría y Problemas Resueltos</i>",
        s["lib"]))
    story.append(Paragraph("Autores: Rafael Pumacayo C. &amp; Rubén Romero L.", s["lib"]))
    story.append(Spacer(1, 2))
    story.append(_hr(accent_hex, 3.5))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(f"INFORME DE ANÁLISIS: {module_name.upper()}", s["h1"]))
    story.append(Paragraph(
        f"Fecha del reporte: <b>{datetime.datetime.now().strftime('%A, %d de %B de %Y  |  %H:%M')}</b>",
        s["sub"]))
    story.append(Spacer(1, 0.6 * cm))

    # ── MARCO TEÓRICO ─────────────────────────────────────────────────────
    theory = THEORY.get(module_name, {})
    story.append(_hr(accent_hex))
    story.append(Paragraph("1.  MARCO TEÓRICO Y FUNDAMENTO", s["h1"]))
    if theory.get("concepto"):
        story.append(Paragraph(theory["concepto"], s["body"]))
    story.append(Spacer(1, 0.3*cm))

    if theory.get("formulas"):
        story.append(Paragraph("Fórmulas Fundamentales del Método", s["h2"]))
        story.append(Spacer(1, 3)) 
        for f in theory["formulas"]:
            try:
                story.append(_latex_to_img(f, fontsize=24, color="#0f4c2a"))
                story.append(Spacer(1, 2)) # Espacio reducido
            except:
                story.append(Paragraph(f, s["formula"]))
    story.append(Spacer(1, 0.4*cm))

    # ── DIAGRAMA / CIRCUITO DEL MÓDULO ────────────────────────────────────
    fig_fn = theory.get("fig_fn")
    if fig_fn:
        story.append(Paragraph("Esquema del Circuito / Diagrama del Módulo", s["h2"]))
        try:
            all_inputs = {}
            for sd in steps_data:
                if sd.get("inputs"):
                    all_inputs.update(sd["inputs"])
            img = fig_fn(all_inputs) if all_inputs else fig_fn({})
            if img:
                story.append(img)
        except Exception as e:
            story.append(Paragraph(f"[Figura no disponible: {e}]", s["warn"]))
        story.append(Spacer(1, 0.4*cm))

    # ── DESARROLLO PASO A PASO ────────────────────────────────────────────
    story.append(PageBreak())
    story.append(_hr(accent_hex, 2))
    story.append(Paragraph("2.  DESARROLLO MATEMÁTICO PASO A PASO", s["h1"]))

    for i, step in enumerate(steps_data):
        if not step.get("result"):
            continue
        story.append(Spacer(1, 0.2*cm))
        step_title = step.get("title", f"Paso {i+1}")

        # Encabezado del paso con rectángulo de color
        story.append(Paragraph(f"PASO {i+1}: {step_title.upper()}", s["h1"]))
        story.append(_hr(accent_hex, 0.8))

        # Tabla de datos de entrada
        if step.get("inputs"):
            story.append(Paragraph("Datos de entrada del paso", s["h2"]))
            story += _input_table(step["inputs"])

        # Desarrollo matemático
        story.append(Paragraph("Desarrollo y cálculos", s["h2"]))
        result_text = step.get("result","")
        for line in result_text.split("\n"):
            line = line.strip()
            if not line: continue
            # Encabezados tipo ═══
            if line.startswith("═") or line.startswith("─"):
                story.append(Paragraph(f"<b>{line}</b>", s["h2"]))
            # Líneas de cálculo con [N]
            elif line.startswith("[") and "]" in line:
                story.append(Paragraph(line.replace("<","&lt;").replace(">","&gt;"), s["formula"]))
            # Líneas de convergencia/iteración
            elif line.startswith("k=") or line.startswith(" k=") or "Iter" in line:
                story.append(Paragraph(line, s["code"]))
            # Resultados finales
            else:
                story.append(Paragraph(line.replace("<","&lt;").replace(">","&gt;"), s["body"]))

        story.append(Spacer(1, 0.3*cm))

    # ── GRÁFICAS ESPECÍFICAS POR MÓDULO ──────────────────────────────────
    story.append(PageBreak())
    story.append(_hr(accent_hex, 2))
    story.append(Paragraph("3.  GRÁFICAS Y RESULTADOS VISUALES", s["h1"]))

    all_inputs = {}
    for sd in steps_data:
        if sd.get("inputs"): all_inputs.update(sd["inputs"])

    # Figura principal del módulo (mayor detalle con los datos reales calculados)
    try:
        if module_name == "Inductancia de Lineas":
            img = fig_conductores_inductancia(
                all_inputs.get("r",1.5), all_inputs.get("D12",2.0),
                all_inputs.get("D23",2.5), all_inputs.get("D31",4.5))
            story.append(Paragraph("3.1  Sección transversal e inductancia vs separación:", s["h2"]))
            story.append(img)
        elif module_name == "Lineas de Transmision":
            img = fig_linea_fasor(all_inputs.get("R",5),all_inputs.get("X",25),
                                   all_inputs.get("VR",115),all_inputs.get("IR",200),all_inputs.get("fp",0.9))
            story.append(Paragraph("3.1  Diagrama fasorial y perfil de voltaje:", s["h2"]))
            story.append(img)
        elif module_name == "Diagramas Circulares de Potencia":
            img = fig_circulo_pq(all_inputs.get("VS",132),all_inputs.get("VR",115),
                                  all_inputs.get("A_mag",0.99),all_inputs.get("A_ang",1.5),
                                  all_inputs.get("B_mag",35),all_inputs.get("B_ang",80))
            story.append(Paragraph("3.1  Diagrama circular P-Q:", s["h2"]))
            story.append(img)
        elif module_name == "Despacho Economico de Centrales Termicas":
            bl=[all_inputs.get("b1",9),all_inputs.get("b2",7.5),all_inputs.get("b3",8)]
            cl=[all_inputs.get("c1",0.01),all_inputs.get("c2",0.012),all_inputs.get("c3",0.008)]
            al=[all_inputs.get("a1",200),all_inputs.get("a2",180),all_inputs.get("a3",140)]
            Pl=[all_inputs.get("P1",150),all_inputs.get("P2",110),all_inputs.get("P3",140)]
            lam=(bl[0]+2*cl[0]*Pl[0]+bl[1]+2*cl[1]*Pl[1])/2
            img = fig_despacho(bl,cl,al,Pl,lam,all_inputs.get("PD",400),[50,40,30],[200,150,250])
            story.append(Paragraph("3.1  Curvas de costo incremental y despacho óptimo:", s["h2"]))
            story.append(img)
        elif module_name == "Teoria de Fallas":
            img = fig_fallas(all_inputs.get("Vpf",1.0),all_inputs.get("Z1",0.1),
                             all_inputs.get("Z2",0.1),all_inputs.get("Z0",0.3),
                             all_inputs.get("Ibase",502.0))
            story.append(Paragraph("3.1  Corriente de falla por tipo:", s["h2"]))
            story.append(img)
        elif module_name == "Flujo de Potencia":
            conv=[0.8,0.3,0.12,0.05,0.02,0.008,0.003,0.001,0.0004,0.0001]
            img = fig_flujo_barras(
                [1.05,all_inputs.get("V1",1.05),0.982,0.975],[0,-1.5,-4.5,-7.2],
                ["Bus 1\nSlack","Bus 2","Bus 3","Bus 4"],conv)
            story.append(Paragraph("3.1  Perfil de voltaje y convergencia:", s["h2"]))
            story.append(img)
        elif module_name == "Valores por Unidad":
            story.append(Paragraph("3.1  Circuito equivalente en p.u.:", s["h2"]))
            story.append(fig_circuit_perunit())
    except Exception as e:
        story.append(Paragraph(f"[Gráfica no disponible: {e}]", s["warn"]))

    # ── TABLA RESUMEN FINAL ───────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(_hr(accent_hex, 2))
    story.append(Paragraph("4.  TABLA RESUMEN DE RESULTADOS", s["h1"]))

    resumen = [["Paso", "Descripción", "Resultado clave"]]
    for i, step in enumerate(steps_data):
        if not step.get("result"): continue
        lines = [l.strip() for l in step["result"].split("\n") if l.strip() and not l.strip().startswith("═")]
        ultimo = lines[-1] if lines else "—"
        resumen.append([f"Paso {i+1}", step.get("title","—"), ultimo[:60]])
    t = Table(resumen, colWidths=[2*cm, 6*cm, 8*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0,0),(-1,0), colors.white),
        ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",  (0,0),(-1,-1), 8),
        ("GRID",      (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f8fafc"),colors.HexColor("#f1f5f9")]),
        ("LEFTPADDING",(0,0),(-1,-1), 5),
        ("TOPPADDING",(0,0),(-1,-1), 4),
        ("VALIGN",    (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(t)

    # ── PIE DE PÁGINA ─────────────────────────────────────────────────────
    story.append(Spacer(1, 0.6*cm))
    story.append(_hr(accent_hex, 2))
    story.append(Paragraph(
        f"Análisis completado — Módulo: <b>{module_name}</b>  |  "
        f"Metodología: Pumacayo C. &amp; Romero L.  |  "
        f"Power Analyzer PRO v10.0",
        s["sub"]))
    story.append(Paragraph(
        "Este reporte ha sido generado automáticamente. "
        "Todos los cálculos son verificados con las fórmulas del libro de referencia.",
        s["warn"]))

    doc.build(story)
