import React from 'react';
import { Inp, Btn, KPI } from '../UI';
import { SpectrumChart } from '../Charts';
import { StepCard } from '../StepCard';

export const HarmonicTab = ({
    fundV, setFundV, harmOrds, setHarmOrds, harmMags, setHarmMags,
    execHarm, harmR, themeKey, C
}) => {
    return (
        <div style={{ width: "100%" }}>
            <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 20 }}>
                <div style={{ background: C.panel, padding: 20, borderRadius: 20, border: `1px solid ${C.border}`, boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)", alignSelf: "start" }}>
                    <div style={{ fontWeight: 900, marginBottom: 16, color: C.accent, fontSize: 15, borderBottom: `2px solid ${C.accent}22`, paddingBottom: 10 }}>Configuración de Armónicos</div>
                    <div style={{ display: "grid", gap: 4 }}>
                        <Inp label="V-Fundamental (V1)" value={fundV} onChange={setFundV} C={C} />
                        <Inp label="Órdenes (h3, h5...)" value={harmOrds} onChange={setHarmOrds} raw={true} C={C} />
                        <Inp label="Magnitudes (Volts)" value={harmMags} onChange={setHarmMags} raw={true} C={C} />
                    </div>
                    <Btn full color={C.accent} onClick={execHarm} C={C} style={{ marginTop: 10 }}>Calcular Distorsión</Btn>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 16 }}>
                        <KPI label="TOTAL HARMONIC DISTORTION (THD-V %)" value={harmR ? harmR.THD : "—"} color={harmR && parseFloat(harmR.THD) > 8 ? C.fault : C.ok} C={C} />
                    </div>
                    <div style={{ background: C.panel, padding: 20, borderRadius: 20, border: `1px solid ${C.border}`, display: "flex", justifyContent: "center", alignItems: "center", minHeight: 180 }}>
                        <SpectrumChart harmonics={harmR?.harmonics || []} V1={fundV} C={C} themeKey={themeKey} />
                    </div>
                </div>
            </div>
            {harmR && <div style={{ marginTop: 24 }}>{harmR.steps.map((s, i) => <StepCard key={i} step={s} themeKey={themeKey} C={C} />)}</div>}
        </div>
    );
};
