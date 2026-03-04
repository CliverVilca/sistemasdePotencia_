import React from 'react';

export const StepCard = ({ step, themeKey, C }) => (
    <div style={{
        background: C.panel,
        border: `1px solid ${C.border}`,
        borderLeft: `6px solid ${C.accent}`,
        borderRadius: 16,
        padding: "20px 24px",
        marginBottom: 18,
        boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    }}>
        <div style={{ color: C.accent, fontWeight: 900, fontSize: 13, marginBottom: 12, letterSpacing: 0.8, textTransform: "uppercase" }}>
            {step.title}
        </div>

        {step.formula && (
            <div style={{
                background: themeKey === "proMidnight" ? "#0f172a" : "#f8fafc",
                border: `1.5px solid ${C.border}`,
                borderRadius: 12,
                padding: "14px 20px",
                marginBottom: 14,
                fontFamily: "'Cambria', 'Georgia', serif",
                color: C.accent,
                fontSize: 15,
                fontWeight: 600,
                textAlign: "center",
                fontStyle: "italic",
                boxShadow: "inset 0 2px 4px rgba(0,0,0,0.05)"
            }}>
                {step.formula}
            </div>
        )}

        {step.calc && (
            <div style={{
                background: themeKey === "proMidnight" ? "#00000033" : "#00000005",
                borderRadius: 10,
                padding: "12px 16px",
                marginBottom: 12,
                fontFamily: "'JetBrains Mono', monospace",
                color: C.a2,
                fontSize: 10.5,
                whiteSpace: "pre-line",
                border: `1px dotted ${C.border}`,
                lineHeight: 1.6
            }}>
                {step.calc}
            </div>
        )}

        {step.detail && (
            <div style={{ color: C.muted, fontSize: 11, fontWeight: 600, marginBottom: 12, opacity: 0.9, display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ fontSize: 14 }}>ℹ️</span> {step.detail}
            </div>
        )}

        {step.type === "lineTable" && step.data && (
            <div style={{ overflowX: "auto", borderRadius: 8, border: `1px solid ${C.border}` }}>
                <table style={{ borderCollapse: "collapse", fontSize: 10.5, width: "100%", background: themeKey === "proMidnight" ? "#ffffff03" : "#00000002" }}>
                    <thead>
                        <tr style={{ background: C.dim }}>
                            {["TIPO", "RAMA (DE→A)", "R (pu)", "X (pu)", "TAP", "Yr", "Yi"].map(h => (
                                <th key={h} style={{ padding: "10px 12px", color: C.muted, textAlign: "left", borderBottom: `2px solid ${C.border}`, fontWeight: 900, fontSize: 9 }}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {step.data.map((r, i) => (
                            <tr key={i} style={{ borderBottom: `1px solid ${C.border}33` }}>
                                <td style={{ padding: "10px 12px", color: r.type === "tx" ? C.tx : C.lineHot, fontWeight: 800 }}>{r.type === "tx" ? "TRANSF" : "LÍNEA"}</td>
                                <td style={{ padding: "10px 12px", color: C.text, fontWeight: 800 }}>BARR.{r.from + 1} → BARR.{r.to + 1}</td>
                                <td style={{ padding: "10px 12px", color: C.pq, fontFamily: "'JetBrains Mono'" }}>{parseFloat(r.R ?? 0).toFixed(4)}</td>
                                <td style={{ padding: "10px 12px", color: C.pq, fontFamily: "'JetBrains Mono'" }}>{parseFloat(r.X ?? 0).toFixed(4)}</td>
                                <td style={{ padding: "10px 12px", color: C.tx, fontWeight: 800 }}>{r.tap || "1.00"}</td>
                                <td style={{ padding: "10px 12px", color: C.a2 }}>{r.yr}</td>
                                <td style={{ padding: "10px 12px", color: C.a2 }}>{r.yi}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        )}

        {step.type === "iters" && step.data && (
            <div style={{ overflowX: "auto", borderRadius: 8, border: `1px solid ${C.border}` }}>
                <table style={{ borderCollapse: "collapse", fontSize: 10.5, width: "100%" }}>
                    <thead style={{ background: C.dim }}>
                        <tr>
                            <th style={{ padding: "10px 12px", color: C.text, textAlign: "left", borderBottom: `2px solid ${C.border}`, fontWeight: 900, fontSize: 9 }}>ITERACIÓN</th>
                            {(step.data[0]?.V || []).map((_, i) => (
                                <th key={i} style={{ padding: "10px 12px", color: C.muted, textAlign: "left", borderBottom: `2px solid ${C.border}`, fontWeight: 900, fontSize: 9 }}>V{i + 1} [pu] ∠°</th>
                            ))}
                            <th style={{ padding: "10px 12px", color: C.muted, textAlign: "left", borderBottom: `2px solid ${C.border}`, fontWeight: 900, fontSize: 9 }}>ERROR MAX</th>
                        </tr>
                    </thead>
                    <tbody>
                        {step.data.map((r, i) => (
                            <tr key={i} style={{ borderBottom: `1px solid ${C.border}33`, background: r.converged ? `${C.ok}15` : "transparent" }}>
                                <td style={{ padding: "10px 12px", color: C.text, fontWeight: 900 }}>№ {r.it}{r.converged ? " ✨" : ""}</td>
                                {(r.V || []).map((v, j) => (
                                    <td key={j} style={{ padding: "10px 12px", color: C.a2, fontFamily: "'JetBrains Mono'", fontWeight: 600 }}>{v.mag} ∠ {v.ang}°</td>
                                ))}
                                <td style={{ padding: "10px 12px", color: r.err < 0.001 ? C.ok : C.warn, fontWeight: 900 }}>{r.err}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        )}

        {step.type === "flows" && step.data && (
            <div style={{ overflowX: "auto", borderRadius: 8, border: `1px solid ${C.border}` }}>
                <table style={{ borderCollapse: "collapse", fontSize: 11, width: "100%" }}>
                    <thead style={{ background: C.dim }}>
                        <tr>
                            {["CONEXIÓN", "P (MW)", "Q (MVAr)", "|I| (pu)", "PÉRIDAS (MW)", "CARGA %"].map(h => (
                                <th key={h} style={{ padding: "10px 12px", color: C.muted, textAlign: "left", borderBottom: `2px solid ${C.border}`, fontWeight: 900, fontSize: 9 }}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {step.data.map((r, i) => {
                            const lc = parseFloat(r.loading || 0) > 0.9 ? C.fault : parseFloat(r.loading || 0) > 0.6 ? C.warn : C.ok;
                            return (
                                <tr key={i} style={{ borderBottom: `1px solid ${C.border}33` }}>
                                    <td style={{ padding: "10px 12px", color: r.type === "tx" ? C.tx : C.lineHot, fontWeight: 900 }}>BARR.{r.from} → BARR.{r.to}</td>
                                    <td style={{ padding: "10px 12px", color: C.a3, fontWeight: 900 }}>{r.P}</td>
                                    <td style={{ padding: "10px 12px", color: C.pq, fontFamily: "'JetBrains Mono'" }}>{r.Q}</td>
                                    <td style={{ padding: "10px 12px", color: C.a2, fontWeight: 700 }}>{r.I}</td>
                                    <td style={{ padding: "10px 12px", color: C.muted, fontWeight: 700 }}>{r.loss}</td>
                                    <td style={{ padding: "10px 12px" }}>
                                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                                            <div style={{ background: C.tag, borderRadius: 10, height: 10, width: 60, overflow: "hidden", border: `1px solid ${C.border}` }}>
                                                <div style={{ width: `${Math.min(parseFloat(r.loading || 0) * 100, 100)}%`, height: "100%", background: lc, opacity: 0.8 }} />
                                            </div>
                                            <span style={{ color: lc, fontSize: 11, fontWeight: 800 }}>{(parseFloat(r.loading || 0) * 100).toFixed(0)}%</span>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        )}

        {step.type === "voltages" && step.data && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 12, marginTop: 12 }}>
                {step.data.map(v => (
                    <div key={v.bus} style={{
                        background: `${v.ok ? C.ok : C.warn}0a`,
                        border: `2px solid ${v.ok ? C.ok : C.warn}22`,
                        borderRadius: 14,
                        padding: "12px 18px",
                        fontSize: 12.5,
                        boxShadow: "0 2px 4px rgba(0,0,0,0.02)",
                        display: "flex",
                        flexDirection: "column",
                        gap: 2
                    }}>
                        <div style={{ color: C.muted, fontSize: 10, fontWeight: 800, textTransform: "uppercase" }}>NODO {v.bus}</div>
                        <div style={{ color: v.ok ? v.ok : v.warn, fontWeight: 900, fontSize: 13.5 }}>{v.mag} ∠ {v.ang}° <small>pu</small></div>
                        <div style={{ fontSize: 9.5, color: v.ok ? C.ok : C.warn, fontWeight: 700 }}>{v.ok ? "ESTADO ÓPTIMO" : "FUERA DE RANGO"}</div>
                    </div>
                ))}
            </div>
        )}

        {step.type === "matrix" && step.data && (
            <div style={{ overflowX: "auto", marginTop: 14, padding: 2 }}>
                <div style={{ border: `1.5px solid ${C.border}`, borderRadius: 14, padding: "16px", background: themeKey === "proMidnight" ? "#0a0f1d" : "#fbfcfd", boxShadow: "inset 0 2px 8px rgba(0,0,0,0.1)" }}>
                    <table style={{ borderCollapse: "collapse", fontSize: 9.5, width: "100%" }}>
                        <tbody>
                            {step.data.map((row, i) => (
                                <tr key={i} style={{ borderBottom: i < step.data.length - 1 ? `1px solid ${C.border}22` : "none" }}>
                                    <td style={{ padding: "6px 12px", color: C.accent, fontWeight: 900, borderRight: `2px solid ${C.border}`, background: C.dim, width: 35 }}>N{i + 1}</td>
                                    {row.map((val, j) => (
                                        <td key={j} style={{ padding: "6px 10px", color: val === 0 ? C.muted : C.a2, fontFamily: "'JetBrains Mono', monospace", textAlign: "right", opacity: val === 0 ? 0.3 : 1 }}>
                                            {typeof val === 'number' ? val.toFixed(5) : val}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        )}
    </div>
);
