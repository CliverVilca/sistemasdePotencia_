import React from 'react';
import { Inp, Btn } from '../UI';
import { RelayChart } from '../Charts';
import { StepCard } from '../StepCard';

export const ProtectionsTab = ({
    relays, setRelays, execProt, protR, scR, themeKey, C
}) => {
    return (
        <div style={{ width: "100%" }}>
            <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 20 }}>
                <div style={{ background: C.panel, padding: 20, borderRadius: 20, border: `1px solid ${C.border}`, boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)", alignSelf: "start" }}>
                    <div style={{ fontWeight: 900, marginBottom: 16, color: C.slack, fontSize: 15, borderBottom: `2px solid ${C.slack}22`, paddingBottom: 10 }}>Coordinación de Protecciones</div>
                    <div style={{ fontSize: 10, color: C.muted, background: C.dim, padding: 12, borderRadius: 12, border: `1px solid ${C.border}`, marginBottom: 16, textAlign: "center" }}>
                        ⚡ CORRIENTE DE FALLA: <span style={{ color: C.fault, fontWeight: 900, fontSize: 16, marginLeft: 5 }}>{scR ? scR.Icc : "N/A"} kA</span>
                    </div>
                    {relays.map((r, i) => (
                        <div key={i} style={{ marginBottom: 12, padding: 14, background: C.dim, borderRadius: 14, border: `1.5px solid ${C.border}66` }}>
                            <div style={{ fontWeight: 900, fontSize: 11, marginBottom: 10, display: "flex", alignItems: "center", gap: 8, textTransform: "uppercase" }}>
                                <div style={{ width: 8, height: 8, borderRadius: "50%", background: [C.accent, C.pv, C.pq, C.a4][i % 4], boxShadow: `0 0 8px ${[C.accent, C.pv, C.pq, C.a4][i % 4]}` }} />
                                Relé {r.name}
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                                <Inp label="Ip (A)" value={r.Ipickup} onChange={v => { const nr = [...relays]; nr[i].Ipickup = parseFloat(v); setRelays(nr); }} C={C} />
                                <Inp label="TDS" value={r.TDS} onChange={v => { const nr = [...relays]; nr[i].TDS = parseFloat(v); setRelays(nr); }} C={C} />
                            </div>
                        </div>
                    ))}
                    <Btn full color={C.slack} onClick={execProt} C={C} style={{ marginTop: 4 }}>Graficar Curvas TCC</Btn>
                </div>
                <div style={{ background: C.panel, padding: 24, borderRadius: 20, border: `1px solid ${C.border}`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)", minHeight: 450 }}>
                    <RelayChart curves={protR?.curves || []} C={C} themeKey={themeKey} />
                </div>
            </div>
            {protR && <div style={{ marginTop: 24 }}>{protR.steps.map((s, i) => <StepCard key={i} step={s} themeKey={themeKey} C={C} />)}</div>}
        </div>
    );
};
