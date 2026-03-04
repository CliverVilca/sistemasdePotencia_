import React from 'react';
import { Btn, KPI } from '../UI';

export const AutoFlowTab = ({
    execAuto, autoR, C
}) => {
    return (
        <div style={{ width: "100%" }}>
            <div style={{ background: C.panel, padding: 40, borderRadius: 32, border: `1.5px solid ${C.border}`, boxShadow: "0 25px 50px -12px rgba(0,0,0,0.2)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 35 }}>
                    <div>
                        <h1 style={{ margin: 0, fontSize: 26, fontWeight: 900, letterSpacing: -1 }}>Engineering One-Click Pipeline 🤖</h1>
                        <p style={{ color: C.muted, fontSize: 14, fontWeight: 600, marginTop: 4 }}>Ejecución masiva de normativas IEEE/IEC para validación de red</p>
                    </div>
                    <Btn color={C.accent} style={{ padding: "20px 40px", fontSize: 16, borderRadius: 20 }} onClick={execAuto} C={C}>🚀 INICIAR PIPELINE</Btn>
                </div>
                {autoR ? (
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20 }}>
                        <KPI label="ESTADO FLUJO" value={autoR.lf?.converged ? "CONVERGE" : "FALLO"} color={autoR.lf?.converged ? C.ok : C.fault} C={C} />
                        <KPI label="PÉRDIDAS T." value={`${autoR.lf?.totalLoss} MW`} color={C.warn} C={C} />
                        <KPI label="CAPACIDAD CC" value={autoR.scOverall ? `${(parseFloat(autoR.scOverall.bestIcc) * 100).toFixed(0)} MVA` : "—"} color={C.fault} C={C} />
                        <KPI label="MÁRGEN N-1" value={`${autoR.n1?.results.filter(r => r.status === "✅ OK").length}/${autoR.n1?.results.length} OK`} color={C.a4} C={C} />
                    </div>
                ) : (
                    <div style={{ width: "100%", textAlign: "center", background: `${C.accent}05`, borderRadius: 24, border: `2px dashed ${C.border}` }}>
                        <div style={{ fontSize: 48, marginBottom: 20 }}>🛸</div>
                        <div style={{ fontWeight: 800, color: C.muted, fontSize: 16 }}>El sistema está listo para procesar todos los escenarios de contingencia y estabilidad.</div>
                    </div>
                )}
            </div>
        </div>
    );
};
