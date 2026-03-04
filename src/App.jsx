import React, { useState, useRef, useCallback, useEffect } from "react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

// Import components
import {
    Inp, Sel, Btn, KPI, StepCard, SLD, Inspector,
    HarmonicTab, StabilityTab, DispatchTab, LoadProfileTab,
    ProtectionsTab, AutoFlowTab, ReportTab, GuideTab,
    SwingChart, SpectrumChart, LoadChart, RelayChart
} from "./components";

// Import constants
import { THEMES } from "./constants/themes";
import { TOPOS, LOAD_PROFILE } from "./constants/topologies";
import { LIB_CABLES, LIB_TX } from "./constants/libraries";

// Import engines
import { runLF, runSC, runHarmonics, runStability, runN1, runED, runLoadProfile, runProtections } from "./engine/solvers";

const TABS = [
    { id: "sld", l: "💻 Diagrama" },
    { id: "harm", l: "📉 Armónicos" },
    { id: "stab", l: "🪐 Estabilidad" },
    { id: "ed", l: "💰 Despacho" },
    { id: "prof", l: "📅 Curva Carga" },
    { id: "prot", l: "🛡️ Protecciones" },
    { id: "auto", l: "🤖 Auto-Flow" },
    { id: "rep", l: "📄 Reporte" },
    { id: "guide", l: "❓ Ayuda" },
];

const EMODES = [
    { id: "select", l: "✋ Selección", c: "#3b82f6", g: "tools" },
    { id: "delete", l: "🗑️ Eliminar", c: "#ef4444", g: "tools" },
    { id: "addSlack", l: "🌐 Red/Slack", c: "#f59e0b", g: "nodes" },
    { id: "addPV", l: "⚙️ Gen (PV)", c: "#10b981", g: "nodes" },
    { id: "addPQ", l: "🏢 Carga (PQ)", c: "#8b5cf6", g: "nodes" },
    { id: "addBus", l: "▥ Barra Bus", c: "#64748b", g: "nodes" },
    { id: "addWind", l: "🍃 Eólico", c: "#2dd4bf", g: "nodes" },
    { id: "addSolar", l: "☀️ Solar PV", c: "#fbbf24", g: "nodes" },
    { id: "addStorage", l: "🔋 Battería", c: "#4ade80", g: "nodes" },
    { id: "addMotor", l: "🔄 Motor Ind.", c: "#f87171", g: "nodes" },
    { id: "connect", l: "⌇ Línea T.", c: "#94a3b8", g: "branches" },
    { id: "addTx", l: "⊛ Transformador", c: "#8b5cf6", g: "branches" },
    { id: "addShunt", l: "⊣ Shunt/Cap", c: "#06b6d4", g: "branches" },
    { id: "addSVC", l: "⚡ SVC/COMP", c: "#f472b6", g: "branches" },
];

export default function App() {
    const [themeKey, setThemeKey] = useState("proMidnight");
    const C = THEMES[themeKey] || THEMES.proSilver;

    const [topoKey, setTopoKey] = useState("custom");
    const [buses, setBuses] = useState([
        { id: "b1", name: "CENTRO_CARGA", type: "slack", x: 500, y: 400, Vmag: 1.0, Vang: 0, vBase: 13.8, Psch: 0, Qsch: 0, Pgen: 50, Pload: 0, specialType: "slack" },
        { id: "b2", name: "INDUSTRIA1", type: "PQ", x: 380, y: 520, Vmag: 1.0, Vang: 0, vBase: 13.8, Psch: -30, Qsch: -15, Pgen: 0, Pload: 30, specialType: "motor" },
        { id: "b3", name: "RESIDENCIAL", type: "PQ", x: 620, y: 520, Vmag: 1.0, Vang: 0, vBase: 13.8, Psch: -20, Qsch: -10, Pgen: 0, Pload: 20, specialType: null },
        { id: "b4", name: "GEN_EOLICA", type: "PV", x: 500, y: 250, Vmag: 1.02, Vang: 0, vBase: 13.8, Psch: 25, Qsch: 0, Pgen: 25, Pload: 0, specialType: "wind" },
    ]);
    const [lines, setLines] = useState([
        { id: "l1", from: "b1", to: "b2", r: 0.02, x: 0.08, b: 0.02, tap: 1, type: "line" },
        { id: "l2", from: "b1", to: "b3", r: 0.03, x: 0.12, b: 0.03, tap: 1, type: "line" },
        { id: "l3", from: "b4", to: "b1", r: 0.015, x: 0.05, b: 0.01, tap: 1, type: "line" },
    ]);
    const [transformers, setTransformers] = useState([]);
    const [tab, setTab] = useState("sld");
    const [logs, setLogs] = useState([{ t: new Date().toLocaleTimeString(), m: "Sistema inicializado. Listo para análisis.", c: "ok" }]);

    const [openGroup, setOpenGroup] = useState("nodes");
    const addLog = (m, c = "accent") => setLogs(p => [...p.slice(-19), { t: new Date().toLocaleTimeString(), m, c }]);
    const [edMode, setEdMode] = useState("select");

    const [lfR, setLfR] = useState(null);
    const [scR, setScR] = useState(null);
    const [harmR, setHarmR] = useState(null);
    const [stabR, setStabR] = useState(null);
    const [n1R, setN1R] = useState(null);
    const [edR, setEdR] = useState(null);
    const [profR, setProfR] = useState(null);
    const [protR, setProtR] = useState(null);
    const [selId, setSelId] = useState(null);
    const [selType, setSelType] = useState(null);
    const [faultBus, setFaultBus] = useState("0");
    const [faultType, setFaultType] = useState("3F");
    const [animFault, setAnimFault] = useState(false);
    const [fundV, setFundV] = useState("220");
    const [harmOrds, setHarmOrds] = useState("3,5,7,11,13");
    const [harmMags, setHarmMags] = useState("8,15,6,3,2");
    const [H, setH] = useState("5");
    const [Pm, setPm] = useState("0.8");
    const [Pe, setPe] = useState("2.0");
    const [d0, setD0] = useState("20");
    const [tcl, setTcl] = useState("0.3");
    const [gens, setGens] = useState([
        { name: "G1", Pmin: 10, Pmax: 200, a: 200, b: 7.0, c: 0.012 },
        { name: "G2", Pmin: 20, Pmax: 300, a: 180, b: 6.5, c: 0.006 },
        { name: "G3", Pmin: 5, Pmax: 150, a: 220, b: 7.8, c: 0.010 }
    ]);
    const [totLoad, setTotLoad] = useState("350");
    const [relays, setRelays] = useState([
        { name: "R1", Ipickup: 400, TDS: 0.5, Iinst: 2000 },
        { name: "R2", Ipickup: 300, TDS: 0.3, Iinst: 1500 }
    ]);
    const [autoR, setAutoR] = useState(null);

    const clearCalc = () => { setLfR(null); setN1R(null); setProfR(null); };

    const loadTopo = (k) => {
        setTopoKey(k);
        setBuses(TOPOS[k].buses.map(b => ({ ...b })));
        setLines(TOPOS[k].lines.map(l => ({ ...l })));
        setTransformers([]);
        setSelId(null);
        setSelType(null);
        setAnimFault(false);
        clearCalc();
        setScR(null);
    };

    const onAddLine = useCallback((f, t) => {
        const id = Math.max(-1, ...lines.map(l => l.id)) + 1;
        setLines(p => [...p, { id, from: f, to: t, R: 0.02, X: 0.08 }]);
        clearCalc();
    }, [lines]);

    const onAddTx = useCallback((f, t) => {
        const id = Math.max(-1, ...transformers.map(x => x.id || 0)) + 1;
        setTransformers(p => [...p, { id, from: f, to: t, R: 0.005, X: 0.06, tap: 1.0 }]);
        clearCalc();
    }, [transformers]);

    const onAddSVC = useCallback((f, t) => {
        const id = Math.max(-1, ...lines.map(l => l.id)) + 1;
        setLines(p => [...p, { id, from: f, to: t, R: 0, X: 0.01, isSVC: true }]);
        clearCalc();
    }, [lines]);

    const onAddShunt = useCallback((f, t) => {
        const id = Math.max(-1, ...lines.map(l => l.id)) + 1;
        setLines(p => [...p, { id, from: f, to: t, R: 0, X: -0.1, isShunt: true }]);
        clearCalc();
    }, [lines]);

    const onDelBus = useCallback(id => {
        setBuses(p => p.filter(b => b.id !== id));
        setLines(p => p.filter(l => (l.from !== id && l.to !== id)));
        setTransformers(p => p.filter(t => (t.from !== id && t.to !== id)));
        if (selId === id) setSelId(null);
        clearCalc();
    }, [selId]);

    const onDelLineEl = useCallback((id, isTx) => {
        if (isTx) setTransformers(p => p.filter(t => t.id !== id));
        else setLines(p => p.filter(l => l.id !== id));
        if (selId === id) setSelId(null);
        clearCalc();
    }, [selId]);

    const onDrag = useCallback((id, x, y) => setBuses(p => p.map(b => b.id === id ? { ...b, x, y } : b)), []);

    const updBus = (id, field, val) => {
        setBuses(p => p.map(b => b.id === id ? { ...b, [field]: isNaN(parseFloat(val)) ? val : parseFloat(val) } : b));
        clearCalc();
    };

    const updLine = (id, field, val) => {
        setLines(p => p.map(l => l.id === id ? { ...l, [field]: parseFloat(val) || 0 } : l));
        clearCalc();
    };

    const updTx = (id, field, val) => {
        setTransformers(p => p.map(t => t.id === id ? { ...t, [field]: parseFloat(val) || 0 } : t));
        clearCalc();
    };

    const saveProject = () => {
        const data = JSON.stringify({ buses, lines, transformers, topoKey });
        const blob = new Blob([data], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Project_${new Date().getTime()}.psim`;
        a.click();
    };

    const clearProject = () => {
        console.log("Wiping project...");
        setBuses([]);
        setLines([]);
        setTransformers([]);
        setSelId(null);
        setSelType(null);
        setLfR(null); setScR(null); setHarmR(null); setStabR(null); setN1R(null); setEdR(null); setAutoR(null);
        setTopoKey("custom");
        setLogs([{ t: new Date().toLocaleTimeString(), m: "CANVAS RESET: Listo para nuevo diseño.", c: "fault" }]);
    };

    const addTemplate = (type) => {
        // Clear state immediately without recursion
        setBuses([]); setLines([]); setTransformers([]);
        setSelId(null); setLfR(null); setScR(null);

        setTimeout(() => {
            if (type === "star") {
                const b = [
                    { id: "b1", x: 600, y: 350, name: "B1_SLACK", type: "slack", Psch: 0, Qsch: 0, vBase: 13.8, vTarg: 1.0, G: 0, B: 0 },
                    { id: "b2", x: 450, y: 550, name: "B2_LOAD", type: "PQ", Psch: -20, Qsch: -10, vBase: 13.8, vTarg: 1.0, G: 0, B: 0, Pload: 20 },
                    { id: "b3", x: 750, y: 550, name: "B3_LOAD", type: "PQ", Psch: -30, Qsch: -15, vBase: 13.8, vTarg: 1.0, G: 0, B: 0, Pload: 30 },
                    { id: "b4", x: 600, y: 150, name: "B4_GEN", type: "PV", Psch: 50, Qsch: 0, vBase: 13.8, vTarg: 1.04, G: 0, B: 0 }
                ];
                const l = [
                    { id: "l1", from: "b1", to: "b2", r: 0.02, x: 0.1, b: 0.05, code: "L1", type: "line" },
                    { id: "l2", from: "b1", to: "b3", r: 0.02, x: 0.1, b: 0.05, code: "L2", type: "line" },
                    { id: "l3", from: "b1", to: "b4", r: 0.01, x: 0.05, b: 0.1, code: "L3", type: "line" }
                ];
                setBuses(b); setLines(l);
                addLog("Plantilla ESTRELLA cargada correctamente.", "ok");
            } else if (type === "parallel") {
                const b = [
                    { id: "b1", x: 400, y: 350, name: "FUENTE", type: "slack", Psch: 0, Qsch: 0, vBase: 13.8, vTarg: 1.0, G: 0, B: 0 },
                    { id: "b2", x: 800, y: 350, name: "CARGA", type: "PQ", Psch: -10, Qsch: -5, vBase: 13.8, vTarg: 1.0, G: 0, B: 0, Pload: 10 }
                ];
                const l = [
                    { id: "l1", from: "b1", to: "b2", r: 0.05, x: 0.2, b: 0, code: "LP1", type: "line" },
                    { id: "l2", from: "b1", to: "b2", r: 0.05, x: 0.2, b: 0, code: "LP2", type: "line" }
                ];
                setBuses(b); setLines(l);
                addLog("Plantilla PARALELO cargada correctamente.", "ok");
            }
        }, 100);
    };

    const loadProject = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            const data = JSON.parse(ev.target.result);
            setBuses(data.buses);
            setLines(data.lines);
            setTransformers(data.transformers || []);
            setTopoKey(data.topoKey || "custom");
            clearCalc();
        };
        reader.readAsText(file);
    };

    const execLF = () => {
        addLog("Iniciando Flujo de Potencia (Newton-Raphson)...");
        const idMap = new Map(buses.map((b, i) => [b.id, i]));
        const solverBuses = buses.map(b => ({ ...b }));
        const solverLines = lines.map(l => ({ ...l, from: idMap.get(l.from), to: idMap.get(l.to) }));
        const solverTx = transformers.map(t => ({ ...t, from: idMap.get(t.from), to: idMap.get(t.to) }));

        const r = runLF(solverBuses, solverLines, solverTx);
        setLfR(r);
        if (r?.converged) addLog(`Convergencia exitosa en ${r.iters.length} iteraciones.`, "ok");
        else addLog("Error: El flujo no convergió.", "fault");
    };
    const execSC = () => {
        setAnimFault(true);
        const targetBus = faultBus !== undefined ? faultBus : (selType === "bus" ? selId : "b1");
        addLog(`Simulando falla ${faultType} en Barra ${targetBus}...`, "fault");
        setTimeout(() => {
            const idMap = new Map(buses.map((b, i) => [b.id, i]));
            const solverBuses = buses.map(b => ({ ...b }));
            const solverLines = lines.map(l => ({ ...l, from: idMap.get(l.from), to: idMap.get(l.to) }));
            const solverTx = transformers.map(t => ({ ...t, from: idMap.get(t.from), to: idMap.get(t.to) }));
            const faultIdx = idMap.get(targetBus) !== undefined ? idMap.get(targetBus) : 0;

            const r = runSC(solverBuses, solverLines, solverTx, faultIdx, faultType);
            setScR(r);
            setAnimFault(false);
            addLog(`Cortocircuito resuelto: Icc = ${r.Icc} kA.`, "ok");
        }, 600);
    };
    const execHarm = () => {
        addLog("Analizando espectro armónico (IEEE 519)...");
        const r = runHarmonics(fundV, harmOrds, harmMags);
        setHarmR(r);
        addLog(`THD calculado: ${r.THD}%.`, r.THD < 5 ? "ok" : "warn");
    };
    const execStab = () => {
        addLog("Ejecutando simulación de estabilidad transitoria...");
        const r = runStability(parseFloat(H), parseFloat(Pm), parseFloat(Pe), parseFloat(d0), tcl);
        setStabR(r);
        addLog(r.stable ? "Sistema Estable tras despeje." : "⚠️ Sistema Inestable.", r.stable ? "ok" : "fault");
    };
    const execN1 = () => { const r = runN1(buses, lines, transformers, C); setN1R(r); };
    const execED = () => {
        const r = runED(gens, totLoad);
        setEdR(r);
        addLog("Despacho Económico Optimizado.", "ok");
    };

    const applyED = () => {
        if (!edR) return;
        const disp = edR.dispatch; // Array with optimal powers [P1, P2, P3]
        let gIdx = 0;
        setBuses(prev => prev.map(b => {
            if (b.type === "PV" || b.type === "slack") {
                const val = parseFloat(disp[gIdx] || 0);
                gIdx++;
                return { ...b, Psch: val, Pgen: val };
            }
            return b;
        }));
        addLog("Configuración óptima aplicada a generadores.", "ok");
        setTab("sld");
        clearCalc();
    };

    const execProf = () => {
        const idMap = new Map(buses.map((b, i) => [b.id, i]));
        const solverBuses = buses.map(b => ({ ...b }));
        const solverLines = lines.map(l => ({ ...l, from: idMap.get(l.from), to: idMap.get(l.to) }));
        const solverTx = transformers.map(t => ({ ...t, from: idMap.get(t.from), to: idMap.get(t.to) }));
        const r = runLoadProfile(solverBuses, solverLines, solverTx, LOAD_PROFILE);
        setProfR(r);
        addLog(`Perfil 24h generado. Pico: ${toFixedSafe(r.peakH.load, 2)} MW.`, "ok");
    };

    const execProt = () => {
        addLog("Calculando curvas de coordinación TCC...");
        const r = runProtections(relays, scR);
        setProtR(r);
    };

    const execAuto = () => {
        addLog("🚀 Invocando Pipeline Maestro de Ingeniería (ISO-8000)...");
        const idMap = new Map(buses.map((b, i) => [b.id, i]));
        const solverBuses = buses.map(b => ({ ...b }));
        const solverLines = lines.map(l => ({ ...l, from: idMap.get(l.from), to: idMap.get(l.to) }));
        const solverTx = transformers.map(t => ({ ...t, from: idMap.get(t.from), to: idMap.get(t.to) }));

        // 1. Ejecutar batería completa de simulaciones
        const lf = runLF(solverBuses, solverLines, solverTx);
        const sc = runSC(solverBuses, solverLines, solverTx, 0, "3F");
        const harm = runHarmonics(fundV, harmOrds, harmMags);
        const stab = runStability(parseFloat(H), parseFloat(Pm), parseFloat(Pe), parseFloat(d0), tcl);
        const n1 = runN1(solverBuses, solverLines, solverTx, C);
        const ed = runED(gens, totLoad);
        const prof = runLoadProfile(solverBuses, solverLines, solverTx, LOAD_PROFILE);
        const prot = runProtections([], sc); // Fallback si no hay relés

        // 2. Sincronizar estados para Reporte y Tableros
        setLfR(lf); setScR(sc); setHarmR(harm); setStabR(stab);
        setN1R(n1); setEdR(ed); setProfR(prof); setProtR(prot);

        setAutoR({ lf, n1, ed, scOverall: { bestIcc: sc.Icc } });

        addLog("✅ Análisis Multidisciplinario Completado. Dossier listo.", "ok");
        setTab("rep"); // Ir directamente al reporte para ver resultados
    };

    const exportPDF = async () => {
        const el = document.getElementById("report-area");
        if (!el) return;
        const canvas = await html2canvas(el, { scale: 2 });
        const imgData = canvas.toDataURL("image/png");
        const pdf = new jsPDF("p", "mm", "a4");
        const pdfW = 210, pdfH = (canvas.height * pdfW) / canvas.width;
        pdf.addImage(imgData, "PNG", 0, 0, pdfW, pdfH);
        pdf.save(`Power_Report_${new Date().getTime()}.pdf`);
    };

    const selBus = buses.find(b => b.id === selId && selType === "bus");
    const selLineEl = [...lines, ...transformers].find(l => l.id === selId && selType === "line");

    return (
        <div style={{ height: "100vh", display: "flex", flexDirection: "column", background: C.bg, color: C.text, fontFamily: "'Inter', sans-serif" }}>
            {/* HEADER */}
            <div style={{ background: C.panel, borderBottom: `1px solid ${C.border}`, padding: "12px 20px", display: "flex", justifyContent: "space-between", alignItems: "center", zIndex: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                    <div style={{ background: C.accent, width: 32, height: 32, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 900 }}>⚡</div>
                    <div>
                        <div style={{ fontWeight: 900, fontSize: 16, letterSpacing: -0.5 }}>POWER ANALYZER <span style={{ color: C.accent }}>PRO</span></div>
                        <div style={{ fontSize: 9, color: C.muted, fontWeight: 700, textTransform: "uppercase" }}>IEEE/IEC Engineering Suite v3.2</div>
                    </div>
                </div>
                <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                    <div style={{ display: "flex", gap: 6, marginRight: 10 }}>
                        <Btn sm color={C.fault} onClick={clearProject} C={C}>✨ Nuevo</Btn>
                        <Btn sm color={C.accent} onClick={saveProject} C={C}>💾 Guardar</Btn>
                        <label style={{ cursor: "pointer" }}>
                            <div style={{ padding: "6px 12px", background: C.panel, border: `1.5px solid ${C.accent}`, borderRadius: 8, fontSize: 10, fontWeight: 800, color: C.accent }}>📁 Cargar</div>
                            <input type="file" style={{ display: "none" }} onChange={loadProject} accept=".psim" />
                        </label>
                    </div>
                    <div style={{ background: C.dim, padding: "4px 8px", borderRadius: 8, display: "flex", gap: 4 }}>
                        <Btn sm active={themeKey === "proSilver"} color={C.accent} onClick={() => setThemeKey("proSilver")} C={C}>☀️</Btn>
                        <Btn sm active={themeKey === "proMidnight"} color={C.accent} onClick={() => setThemeKey("proMidnight")} C={C}>🌙</Btn>
                    </div>
                    <div style={{ display: "flex", gap: 3, marginLeft: 4 }}>
                        {[lfR, scR, harmR, stabR, n1R, edR, profR, protR].map((r, i) => (
                            <div key={i} title={`Análisis ${i + 1}`} style={{ width: 7, height: 7, borderRadius: "50%", background: r ? C.ok : C.border }} />
                        ))}
                    </div>
                </div>
            </div>

            {/* TABS Navigation */}
            <div style={{ display: "flex", background: C.panel, borderBottom: `1px solid ${C.border}`, overflowX: "auto", flexShrink: 0, padding: "0 10px" }}>
                {TABS.map(t => (
                    <button key={t.id} onClick={() => setTab(t.id)}
                        style={{ padding: "12px 18px", background: "transparent", border: "none", borderBottom: `3px solid ${tab === t.id ? C.accent : "transparent"}`, color: tab === t.id ? C.accent : C.muted, transition: "all 0.2s", cursor: "pointer", fontWeight: tab === t.id ? 800 : 500, fontSize: 11, whiteSpace: "nowrap", display: "flex", alignItems: "center", gap: 8 }}>
                        {t.l}
                    </button>
                ))}
            </div>

            {/* CONTENIDO PRINCIPAL: SIDEBAR + CANVAS + INSPECTOR */}
            <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
                {tab === "sld" && (
                    <>
                        {/* PALETA DE COMPONENTES PROFESIONAL (ACORDEÓN - MATCH SCREENSHOT) */}
                        <div style={{ width: 160, background: C.panel, borderRight: `1px solid ${C.border}`, display: "flex", flexDirection: "column", padding: "12px 0", gap: 6, flexShrink: 0, overflowY: "auto" }}>
                            <div style={{ fontSize: 9, fontWeight: 800, color: C.muted, textTransform: "uppercase", letterSpacing: 1, marginBottom: 12, paddingLeft: 14 }}>Menú Componentes</div>

                            {[
                                { id: "nodes", l: "ENERGÍA & GEN", bg: "#10b981" },
                                { id: "branches", l: "DISTRIBUCIÓN", bg: "#6366f1" },
                                { id: "tools", l: "EDICIÓN", bg: "#3b82f6" }
                            ].map(group => {
                                const isOpen = openGroup === group.id;
                                return (
                                    <div key={group.id} style={{ display: "flex", flexDirection: "column" }}>
                                        {/* Dropdown Header (Ultra-Compact) */}
                                        <div onClick={() => setOpenGroup(isOpen ? null : group.id)}
                                            style={{
                                                display: "flex", alignItems: "center", justifyContent: "space-between",
                                                padding: "8px 12px", cursor: "pointer",
                                                background: isOpen ? group.bg : "transparent",
                                                color: isOpen ? "#ffffff" : C.text,
                                                fontWeight: 800, fontSize: 8,
                                                borderLeft: isOpen ? "none" : `3px solid transparent`,
                                                transition: "all 0.1s"
                                            }}>
                                            <span style={{ letterSpacing: 0.5 }}>{group.l}</span>
                                            <span style={{ fontSize: 7, transform: isOpen ? "rotate(180deg)" : "rotate(0deg)" }}>▼</span>
                                        </div>

                                        {/* Dropdown Content (Compact) */}
                                        <div style={{
                                            display: "flex", flexDirection: "column", gap: 0,
                                            maxHeight: isOpen ? 600 : 0, overflow: "hidden",
                                            transition: "max-height 0.3s ease-out"
                                        }}>
                                            {EMODES.filter(m => m.g === group.id).map(m => (
                                                <button key={m.id} onClick={() => setEdMode(m.id)}
                                                    style={{
                                                        display: "flex", alignItems: "center", gap: 10,
                                                        padding: "6px 14px", cursor: "pointer", transition: "all 0.1s",
                                                        background: edMode === m.id ? `${m.c}15` : "transparent",
                                                        border: "none",
                                                        borderLeft: `3px solid ${edMode === m.id ? m.c : "transparent"}`,
                                                        textAlign: "left", width: "100%"
                                                    }}>
                                                    <span style={{ fontSize: 13, opacity: edMode === m.id ? 1 : 0.7 }}>{m.l.split(" ")[0]}</span>
                                                    <span style={{
                                                        fontSize: 8.5, fontWeight: 700,
                                                        color: edMode === m.id ? m.c : C.text,
                                                        opacity: edMode === m.id ? 1 : 0.75
                                                    }}>
                                                        {m.l.split(" ").slice(1).join(" ")}
                                                    </span>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* ÁREA DE TRABAJO (CENTRO) */}
                        <div style={{ flex: 1, display: "flex", flexDirection: "column", background: C.bg, position: "relative" }}>
                            {/* Toolbar de Análisis (Superior del Canvas) */}
                            <div style={{ display: "flex", gap: 8, padding: "8px 16px", background: `${C.panel}aa`, borderBottom: `1px solid ${C.border}`, alignItems: "center", zIndex: 5, backdropFilter: "blur(4px)" }}>
                                <Btn sm color={C.accent} onClick={execLF} title="Calcular Flujo de Potencia Normal" C={C}>▶ Correr Flujo</Btn>
                                <Btn sm color={C.fault} onClick={execSC} title="Simular Cortocircuito Seleccionado" C={C}>⚡ Corto</Btn>
                                <Btn sm color={C.pv} onClick={execN1} title="Análisis de Contingencias N-1" C={C}>🔄 N-1</Btn>
                                <Btn sm color={C.a4} onClick={execAuto} title="Optimización IA Automática" C={C}>🤖 Auto</Btn>

                                <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
                                    <div style={{ fontSize: 10, color: C.muted, fontWeight: 600 }}>Modo Actual:</div>
                                    <div style={{ height: 26, padding: "0 12px", background: C.dim, borderRadius: 13, border: `1px solid ${C.border}`, display: "flex", alignItems: "center", fontSize: 9, fontWeight: 900, color: EMODES.find(m => m.id === edMode)?.c }}>
                                        {EMODES.find(m => m.id === edMode)?.l.toUpperCase()}
                                    </div>
                                </div>
                            </div>

                            <div style={{ flex: 1, position: "relative" }}
                                onClick={(e) => {
                                    if (!edMode.startsWith("add")) return;
                                    const svg = document.getElementById("sld-svg");
                                    if (!svg) return;
                                    const pt = svg.createSVGPoint();
                                    pt.x = e.clientX; pt.y = e.clientY;
                                    const sp = pt.matrixTransform(svg.getScreenCTM().inverse());
                                    const newId = `b${Math.max(-1, ...buses.map(b => parseInt(b.id.substring(1)))) + 1}`;

                                    let type = "PQ", p = -10, q = -5, pgen = 0, namePrefix = "B";
                                    if (edMode === "addSlack") { type = "slack"; p = 0; q = 0; pgen = 50; namePrefix = "RED"; }
                                    else if (edMode === "addPV") { type = "PV"; p = 0; q = 0; pgen = 30; namePrefix = "GEN"; }
                                    else if (edMode === "addPQ") { type = "PQ"; p = -20; q = -10; pgen = 0; namePrefix = "CARGA"; }
                                    else if (edMode === "addBus") { type = "PQ"; p = 0; q = 0; pgen = 0; namePrefix = "B"; }
                                    else if (edMode === "addWind") { type = "PV"; p = 0; q = 0; pgen = 15; namePrefix = "WIND"; }
                                    else if (edMode === "addSolar") { type = "PV"; p = 0; q = 0; pgen = 10; namePrefix = "SOLAR"; }
                                    else if (edMode === "addStorage") { type = "PQ"; p = 5; q = 2; pgen = 0; namePrefix = "BATT"; }
                                    else if (edMode === "addMotor") { type = "PQ"; p = -25; q = -15; pgen = 0; namePrefix = "MOTOR"; }

                                    setBuses(prev => [...prev, {
                                        id: newId, name: `${namePrefix}${parseInt(newId.substring(1)) + 1}`,
                                        type, x: sp.x, y: sp.y, Vmag: 1.0, Vang: 0, vBase: 13.8, Psch: p, Qsch: q, Pgen: pgen, Pload: type === "PQ" ? Math.abs(p) : 0,
                                        specialType: edMode.substring(3).toLowerCase()
                                    }]);
                                    addLog(`Componente ${(EMODES.find(m => m.id === edMode)?.l || "").split(" ")[1]} añadido.`);
                                    clearCalc();
                                }}>
                                <SLD
                                    buses={buses} lines={lines} transformers={transformers}
                                    lfResult={lfR} scResult={scR}
                                    faultBusId={parseInt(faultBus)} animFault={animFault}
                                    onSelBus={id => { setSelId(id); setSelType("bus"); }}
                                    onSelLine={id => { setSelId(id); setSelType("line"); }}
                                    selId={selId} selType={selType} onDrag={onDrag}
                                    edMode={edMode} onAddLine={onAddLine} onAddTx={onAddTx}
                                    onAddSVC={onAddSVC} onAddShunt={onAddShunt}
                                    onDelBus={onDelBus} addTemplate={addTemplate} themeKey={themeKey} C={C}
                                />
                            </div>
                        </div>

                        {/* INSPECTOR (DERECHO) */}
                        <Inspector
                            selBus={selBus} selLineEl={selLineEl} lfR={lfR} scR={scR}
                            faultBus={faultBus} setFaultBus={setFaultBus} execSC={execSC}
                            transformers={transformers} flows={lfR?.flows || []} C={C}
                            updBus={updBus} updLine={updLine} updTx={updTx}
                            onDelBus={onDelBus} onDelLineEl={onDelLineEl}
                        />
                    </>
                )}

                {tab !== "sld" && (
                    <div style={{ flex: 1, overflowY: "auto", background: C.bg, paddingTop: 20, paddingBottom: 40 }}>
                        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 20px" }}>
                            {tab === "harm" && <HarmonicTab fundV={fundV} setFundV={setFundV} harmOrds={harmOrds} setHarmOrds={setHarmOrds} harmMags={harmMags} setHarmMags={setHarmMags} execHarm={execHarm} harmR={harmR} themeKey={themeKey} C={C} />}
                            {tab === "stab" && <StabilityTab H={H} setH={setH} Pm={Pm} setPm={setPm} Pe={Pe} setPe={setPe} d0={d0} setD0={setD0} tcl={tcl} setTcl={setTcl} execStab={execStab} stabR={stabR} themeKey={themeKey} C={C} />}
                            {tab === "ed" && <DispatchTab totLoad={totLoad} setTotLoad={setTotLoad} gens={gens} execED={execED} applyED={applyED} edR={edR} themeKey={themeKey} C={C} />}
                            {tab === "prof" && <LoadProfileTab execProf={execProf} profR={profR} themeKey={themeKey} C={C} />}
                            {tab === "prot" && <ProtectionsTab relays={relays} setRelays={setRelays} execProt={execProt} protR={protR} scR={scR} themeKey={themeKey} C={C} />}
                            {tab === "auto" && <AutoFlowTab execAuto={execAuto} autoR={autoR} C={C} />}
                            {tab === "rep" && <ReportTab buses={buses} lines={lines} transformers={transformers} lfR={lfR} scR={scR} harmR={harmR} stabR={stabR} n1R={n1R} edR={edR} profR={profR} protR={protR} exportPDF={exportPDF} themeKey={themeKey} C={C} />}
                            {tab === "guide" && <GuideTab C={C} />}
                        </div>
                    </div>
                )}
            </div>

            {/* FOOTER / STATUS BAR / LOGS */}
            <div style={{ background: C.dim, borderTop: `1px solid ${C.border}`, display: "flex", flexDirection: "column" }}>
                <div style={{ maxHeight: 60, overflowY: "auto", padding: "6px 20px", fontSize: 9, display: "flex", flexDirection: "column", gap: 2, background: themeKey === "proMidnight" ? "#00000033" : "#00000008" }}>
                    {logs.map((l, i) => (
                        <div key={i} style={{ display: "flex", gap: 10 }}>
                            <span style={{ color: C.muted, fontWeight: 800 }}>[{l.t}]</span>
                            <span style={{ color: C[l.c] || C.text, fontWeight: 600 }}>{l.m}</span>
                        </div>
                    ))}
                </div>
                <div style={{ background: C.panel, padding: "6px 20px", fontSize: 10, display: "flex", justifyContent: "space-between", color: C.muted, fontWeight: 700, borderTop: `1px solid ${C.border}` }}>
                    <div>SISTEMA: {topoKey === "s3" ? "3-BUS DEMO" : "IEEE 5-BUS"} | BARRAS: {buses.length} | RAMAS: {lines.length + transformers.length}</div>
                    <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                            <div style={{ width: 8, height: 8, borderRadius: "50%", background: C.ok }} /> ENGINE READY
                        </div>
                        <div>PRO V3.2 | SESIÓN: {new Date().toLocaleDateString()} | RE-BUILD: 4</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
