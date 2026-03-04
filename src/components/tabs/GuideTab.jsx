import React from 'react';

export const GuideTab = ({ C }) => {
    return (
        <div style={{ padding: 40, maxWidth: 1000, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 35 }}>
            <div style={{ background: C.panel, padding: 35, borderRadius: 28, border: `1px solid ${C.border}` }}>
                <h3 style={{ color: C.accent, fontWeight: 900, fontSize: 20, marginBottom: 25, display: "flex", alignItems: "center", gap: 10 }}>
                    <span>📖</span> MANUAL DEL INGENIERO
                </h3>
                <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                    {[
                        ["DISEÑO DE RED", "Use las herramientas superiores para editar la topología. 'Barra' crea nudos con voltajes base configurables. 'Línea' y 'Trafo' definen las conexiones y parámetros serie."],
                        ["NEWTON-RAPHSON", "El motor resuelve ecuaciones de balance de potencia. Asegúrese de tener al menos una barra tipo 'Slack' para referencia de fase."],
                        ["ANÁLISIS DE FALLA", "Calcula corrientes según IEC 60909. Útil para verificar la capacidad de ruptura de interruptores y ajuste de relés de sobrecorriente."],
                        ["ESTABILIDAD", "Evalúa la respuesta dinámica ante fallas mediante el criterio de áreas iguales y la ecuación de oscilación."],
                        ["POST-PROCESAMIENTO", "Utilice la pestaña de 'Reporte' para consolidar todos los resultados en un documento exportable a PDF."]
                    ].map(([t, d], i) => (
                        <div key={i}>
                            <div style={{ fontSize: 11, fontWeight: 900, color: C.accent, marginBottom: 6, textTransform: "uppercase", letterSpacing: 0.5 }}>{t}</div>
                            <div style={{ fontSize: 13, lineHeight: 1.6, color: C.muted }}>{d}</div>
                        </div>
                    ))}
                </div>
            </div>
            <div style={{ background: C.panel, padding: 35, borderRadius: 28, border: `1px solid ${C.border}` }}>
                <h3 style={{ color: C.a2, fontWeight: 900, fontSize: 20, marginBottom: 25, display: "flex", alignItems: "center", gap: 10 }}>
                    <span>⚖️</span> ESTÁNDARES & TOLERANCIAS
                </h3>
                <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
                    <div style={{ background: `${C.ok}08`, padding: 20, borderRadius: 16, border: `1.5px solid ${C.ok}22` }}>
                        <div style={{ fontWeight: 900, fontSize: 14, marginBottom: 8, color: C.ok }}>LÍMITES DE TENSIÓN (ANSI C84.1)</div>
                        <div style={{ fontSize: 12, color: C.muted, lineHeight: 1.5 }}>Las barras deben mantenerse entre <b>0.95 pu</b> y <b>1.05 pu</b>. Caídas superiores al 5% requieren compensación reactiva.</div>
                    </div>
                    <div style={{ background: `${C.warn}08`, padding: 20, borderRadius: 16, border: `1.5px solid ${C.warn}22` }}>
                        <div style={{ fontWeight: 900, fontSize: 14, marginBottom: 8, color: C.warn }}>CALIDAD DE ENERGÍA (IEEE 519)</div>
                        <div style={{ fontSize: 12, color: C.muted, lineHeight: 1.5 }}>El THD-V total no debe exceder el <b>5%</b> en el Punto de Acoplamiento Común para tensiones menores a 69kV.</div>
                    </div>
                    <div style={{ background: `${C.fault}08`, padding: 20, borderRadius: 16, border: `1.5px solid ${C.fault}22` }}>
                        <div style={{ fontWeight: 900, fontSize: 14, marginBottom: 8, color: C.fault }}>SEGURIDAD N-1</div>
                        <div style={{ fontSize: 12, color: C.muted, lineHeight: 1.5 }}>Ante la salida de cualquier elemento (línea o trafo), el sistema debe mantener voltajes estables y evitar sobrecargas críticas.</div>
                    </div>
                </div>
            </div>
        </div>
    );
};
