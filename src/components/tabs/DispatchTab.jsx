import React from 'react';
import { Inp, Btn, KPI } from '../UI';
import { StepCard } from '../StepCard';

export const DispatchTab = ({
    totLoad, setTotLoad, gens, execED, applyED, edR, themeKey, C
}) => {
    return (
        <div style={{ width: "100%" }}>
            <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 20 }}>
                <div style={{ background: C.panel, padding: 20, borderRadius: 20, border: `1px solid ${C.border}`, boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)", alignSelf: "start" }}>
                    <div style={{ fontWeight: 900, marginBottom: 16, color: C.pv, fontSize: 15, borderBottom: `2px solid ${C.pv}22`, paddingBottom: 10 }}>Despacho Económico</div>
                    <Inp label="Demanda Total (MW)" value={totLoad} onChange={setTotLoad} C={C} />
                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                        <Btn full color={C.pv} onClick={execED} C={C}>Optimizar Costos</Btn>
                        {edR && <Btn full outline color={C.ok} onClick={applyED} C={C}>✅ Aplicar al Sistema</Btn>}
                    </div>
                    <div style={{ marginTop: 20 }}>
                        <div style={{ fontSize: 9, color: C.muted, marginBottom: 10, fontWeight: 800, textTransform: "uppercase", letterSpacing: 0.5 }}>UNIDADES GENERADORAS</div>
                        {gens.map((g, i) => (
                            <div key={i} style={{ display: "flex", gap: 8, marginBottom: 8, background: C.dim, padding: "10px 14px", borderRadius: 12, border: `1px solid ${C.border}44`, alignItems: "center" }}>
                                <div style={{ width: 10, height: 10, borderRadius: "50%", background: C.pv, boxShadow: `0 0 8px ${C.pv}` }} />
                                <div style={{ fontSize: 11, fontWeight: 800, color: C.text }}>{g.name}</div>
                                <div style={{ marginLeft: "auto", fontSize: 9, color: C.muted, fontWeight: 600 }}>{g.Pmin} - {g.Pmax} MW</div>
                            </div>
                        ))}
                    </div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                        <KPI label="COSTO TOTAL ($/h)" value={edR ? edR.totalCost : "—"} color={C.pv} C={C} />
                        <KPI label="λ ÓPTIMO ($/MWh)" value={edR ? edR.lambda : "—"} color={C.a3} C={C} />
                    </div>
                </div>
            </div>
            {edR && <div style={{ marginTop: 24 }}>{edR.steps.map((s, i) => <StepCard key={i} step={s} themeKey={themeKey} C={C} />)}</div>}
        </div>
    );
};
