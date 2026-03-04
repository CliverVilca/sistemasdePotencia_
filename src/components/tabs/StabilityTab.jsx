import React from 'react';
import { Inp, Btn, KPI } from '../UI';
import { SwingChart } from '../Charts';
import { StepCard } from '../StepCard';

export const StabilityTab = ({
    H, setH, Pm, setPm, Pe, setPe, d0, setD0, tcl, setTcl,
    execStab, stabR, themeKey, C
}) => {
    return (
        <div style={{ width: "100%" }}>
            <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 20 }}>
                <div style={{ background: C.panel, padding: 20, borderRadius: 20, border: `1px solid ${C.border}`, boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)", alignSelf: "start" }}>
                    <div style={{ fontWeight: 900, marginBottom: 16, color: C.a4, fontSize: 15, borderBottom: `2px solid ${C.a4}22`, paddingBottom: 10 }}>Dinámica Transitoria</div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                        <div style={{ gridColumn: "span 2" }}><Inp label="Inercia H (MW·s/MVA)" value={H} onChange={setH} C={C} /></div>
                        <Inp label="Pm (Mech. pu)" value={Pm} onChange={setPm} C={C} />
                        <Inp label="Pe_max (Post pu)" value={Pe} onChange={setPe} C={C} />
                        <Inp label="δ₀ (Ang. Init °)" value={d0} onChange={setD0} C={C} />
                        <Inp label="Tcl (Cierre s)" value={tcl} onChange={setTcl} C={C} />
                    </div>
                    <Btn full color={C.a4} onClick={execStab} C={C} style={{ marginTop: 10 }}>Ejecutar Swing Test</Btn>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    <KPI label="ESTADO DINÁMICO DEL SISTEMA" value={stabR ? (stabR.stable ? "SISTEMA ESTABLE ✅" : "⚠️ INESTABLE / CRÍTICO") : "—"} color={stabR?.stable ? C.ok : C.fault} C={C} />
                    <div style={{ background: C.panel, padding: 20, borderRadius: 20, border: `1px solid ${C.border}`, display: "flex", justifyContent: "center", alignItems: "center", minHeight: 200 }}>
                        <SwingChart pts={stabR?.pts || []} C={C} themeKey={themeKey} />
                    </div>
                </div>
            </div>
            {stabR && <div style={{ marginTop: 24 }}>{stabR.steps.map((s, i) => <StepCard key={i} step={s} themeKey={themeKey} C={C} />)}</div>}
        </div>
    );
};
