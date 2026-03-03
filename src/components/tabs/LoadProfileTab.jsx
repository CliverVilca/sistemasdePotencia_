import React from 'react';
import { Btn, KPI } from '../UI';
import { LoadChart } from '../Charts';

export const LoadProfileTab = ({
    execProf, profR, themeKey, C
}) => {
    return (
        <div style={{ width: "100%" }}>
            <div style={{ background: C.panel, padding: 24, borderRadius: 24, border: `1px solid ${C.border}`, marginBottom: 20, boxShadow: "0 4px 20px rgba(0,0,0,0.05)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
                    <div>
                        <div style={{ fontWeight: 900, fontSize: 20 }}>Perfil de Carga Diaria (24h)</div>
                        <div style={{ fontSize: 13, color: C.muted, marginTop: 4 }}>Simulación dinámica de demanda y variabilidad de red</div>
                    </div>
                    <Btn color={C.accent} onClick={execProf} C={C}>▶ Iniciar Simulación 24h</Btn>
                </div>
                <div style={{ display: "flex", justifyContent: "center", marginBottom: 30, background: C.dim, padding: 20, borderRadius: 20, border: `1px solid ${C.border}22` }}>
                    <LoadChart data={profR?.results || []} C={C} themeKey={themeKey} />
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
                    <KPI sm label="Pico de Carga" value={profR ? `${profR.peakH.load} MW` : "—"} C={C} />
                    <KPI sm label="Carga Media" value={profR ? `${profR.avgLoad} MW` : "—"} C={C} />
                    <KPI sm label="Factor Carga" value={profR ? profR.loadFactor : "—"} C={C} />
                    <KPI sm label="Pérdidas Máx" value={profR ? `${profR.maxLoss} MW` : "—"} color={C.warn} C={C} />
                </div>
            </div>

            {profR && (
                <div style={{ background: C.panel, padding: 20, borderRadius: 20, border: `1px solid ${C.border}`, boxShadow: "0 2px 10px rgba(0,0,0,0.02)" }}>
                    <div style={{ fontWeight: 800, fontSize: 13, marginBottom: 16, color: C.accent, textTransform: "uppercase", letterSpacing: 0.5 }}>Bitácora de Simulación Temporal (24h)</div>
                    <div style={{ overflowX: "auto", borderRadius: 12, border: `1px solid ${C.border}44` }}>
                        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11 }}>
                            <thead style={{ background: C.dim }}>
                                <tr>
                                    {["HORA", "DEMANDA (MW)", "GENERACIÓN (MW)", "PÉRDIDAS (MW)", "ESTADO"].map(h => (
                                        <th key={h} style={{ padding: "10px 14px", textAlign: "left", color: C.muted, fontWeight: 900, fontSize: 9 }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {profR.results.map((r, i) => (
                                    <tr key={i} style={{ borderBottom: `1px solid ${C.border}22` }}>
                                        <td style={{ padding: "10px 14px", fontWeight: 800, color: C.text }}>{r.h}:00 h</td>
                                        <td style={{ padding: "10px 14px", color: C.a2, fontFamily: "'JetBrains Mono'" }}>{r.load} MW</td>
                                        <td style={{ padding: "10px 14px", color: C.pq, fontFamily: "'JetBrains Mono'" }}>{r.gen} MW</td>
                                        <td style={{ padding: "10px 14px", color: C.warn, fontWeight: 700 }}>{r.loss} MW</td>
                                        <td style={{ padding: "10px 14px" }}>
                                            <span style={{ background: `${C.ok}15`, color: C.ok, padding: "3px 8px", borderRadius: 6, fontSize: 9, fontWeight: 900 }}>CONVERGIÓ</span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};
