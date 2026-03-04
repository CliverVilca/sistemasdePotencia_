import React from 'react';
import { Btn, KPI } from '../UI';
import { StepCard } from '../StepCard';
import { SLD } from '../SLD';
import { SwingChart, SpectrumChart, LoadChart, RelayChart } from '../Charts';
import { THEMES } from '../../constants/themes';

export const ReportTab = ({
    buses, lines, transformers, lfR, scR, harmR, stabR, n1R, edR, profR, protR, exportPDF, themeKey, C
}) => {
    const reportC = THEMES.proSilver; // Use light theme for report readability

    const SectionHeader = ({ num, title }) => (
        <div style={{ margin: "40px 0 20px", borderLeft: `8px solid ${reportC.accent}`, paddingLeft: 15, background: "#f8f9fa", padding: "12px 15px", borderRadius: "0 8px 8px 0" }}>
            <h2 style={{ margin: 0, fontSize: 18, color: "#1a1a1a", fontWeight: 900, textTransform: "uppercase", letterSpacing: 0.5 }}>
                {num}. {title}
            </h2>
        </div>
    );

    return (
        <div style={{ width: "100%" }}>
            <div style={{ textAlign: "right", marginBottom: 20 }}>
                <Btn onClick={exportPDF} C={reportC} color={reportC.accent} style={{ padding: "12px 24px", fontSize: 13 }}>📥 Exportar Dossier Técnico (PDF)</Btn>
            </div>

            <div id="report-area" style={{
                background: "#ffffff",
                color: "#1a1a1a",
                maxWidth: 900,
                margin: "0 auto",
                boxShadow: "0 0 50px rgba(0,0,0,0.1)",
                borderRadius: 4,
                padding: "60px 80px",
                fontFamily: "'Inter', sans-serif"
            }}>
                {/* PORTADA EXECUTIVA */}
                <div style={{ textAlign: "center", borderBottom: "4px solid #1a1a1a", paddingBottom: 40, marginBottom: 50 }}>
                    <div style={{ fontSize: 12, fontWeight: 800, color: reportC.accent, letterSpacing: 4, marginBottom: 15 }}>INGENIERÍA DE SISTEMAS DE POTENCIA</div>
                    <h1 style={{ margin: 0, fontSize: 32, fontWeight: 900, color: "#000", lineHeight: 1.1 }}>REPORTE TÉCNICO DE OPERACIÓN Y ESTABILIDAD DE RED</h1>
                    <div style={{ marginTop: 25, display: "flex", justifyContent: "center", gap: 30, fontSize: 11, color: "#666", fontWeight: 700 }}>
                        <div>FECHA: {new Date().toLocaleDateString().toUpperCase()}</div>
                        <div>ID PROYECTO: {Math.random().toString(36).substring(7).toUpperCase()}</div>
                        <div>VERSIÓN: 3.2.0</div>
                    </div>
                </div>

                {/* SECCIÓN 1: VISTA DE LA RED */}
                <SectionHeader num="1" title="Arquitectura del Sistema (SLD)" />
                <p style={{ fontSize: 13, lineHeight: 1.6, color: "#444" }}>Visualización unifilar del sistema eléctrico de potencia analizado. Muestra la topología de barras y los elementos de interconexión (Líneas y Transformadores).</p>
                <div style={{ border: "1px solid #eee", borderRadius: 12, overflow: "hidden", background: "#fafafa", height: 350, margin: "20px 0", position: "relative" }}>
                    <SLD buses={buses} lines={lines} transformers={transformers} themeKey="proSilver" C={reportC} scale={0.6} />
                </div>

                {/* SECCIÓN 2: FLUJO DE POTENCIA */}
                {lfR && (
                    <>
                        <SectionHeader num="2" title="Análisis de Flujo de Potencia" />
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 15, marginBottom: 24 }}>
                            <div style={{ background: "#f1f5f9", padding: 15, borderRadius: 8 }}>
                                <div style={{ fontSize: 10, color: "#64748b", fontWeight: 800 }}>ESTADO DE RÉGIMEN</div>
                                <div style={{ fontSize: 18, fontWeight: 900, color: lfR?.converged ? "#10b981" : "#ef4444" }}>{lfR?.converged ? "SISTEMA ESTABLE (CONVERGIÓ)" : "NO CONVERGENTE"}</div>
                            </div>
                            <div style={{ background: "#f1f5f9", padding: 15, borderRadius: 8 }}>
                                <div style={{ fontSize: 10, color: "#64748b", fontWeight: 800 }}>PÉRDIDAS TOTALES</div>
                                <div style={{ fontSize: 18, fontWeight: 900 }}>{parseFloat(lfR?.totalLoss || 0).toFixed(3)} MW</div>
                            </div>
                        </div>
                        {lfR?.steps?.map((s, i) => <StepCard key={i} step={s} themeKey="proSilver" C={reportC} />)}
                    </>
                )}

                {/* SECCIÓN 3: CORTOCIRCUITO */}
                {scR && (
                    <>
                        <SectionHeader num="3" title="Análisis de Fallas (Cortocircuito)" />
                        <div style={{ background: "#fff1f2", padding: 20, borderRadius: 12, borderLeft: "5px solid #e11d48", marginBottom: 24 }}>
                            <div style={{ fontSize: 14, fontWeight: 900, marginBottom: 5 }}>CORRIENTE DE FALLA MÁXIMA</div>
                            <div style={{ fontSize: 32, fontWeight: 900, color: "#e11d48" }}>{parseFloat(scR?.Icc || 0).toFixed(2)} kA <span style={{ fontSize: 16, color: "#fb7185" }}>/ {parseFloat(scR?.Scc || 0).toFixed(2)} MVA</span></div>
                        </div>
                        {scR?.steps?.map((s, i) => <StepCard key={i} step={s} themeKey="proSilver" C={reportC} />)}
                    </>
                )}

                {/* SECCIÓN 4: ARMÓNICOS */}
                {harmR && (
                    <>
                        <SectionHeader num="4" title="Calidad de Energía y Armónicos" />
                        <div style={{ display: "flex", gap: 30, alignItems: "center", marginBottom: 30 }}>
                            <div style={{ flex: 1, background: "#f0fdf4", padding: 20, borderRadius: 12, border: "1px solid #bcf0da" }}>
                                <div style={{ fontSize: 11, fontWeight: 800, color: "#166534" }}>TOTAL HARMONIC DISTORTION (THD-V)</div>
                                <div style={{ fontSize: 36, fontWeight: 900, color: "#10b981" }}>{parseFloat(harmR?.THD || 0).toFixed(2)}%</div>
                                <div style={{ fontSize: 10, fontWeight: 700, marginTop: 5, color: parseFloat(harmR?.THD || 0) > 5 ? "#b91c1c" : "#166534" }}>
                                    {parseFloat(harmR?.THD || 0) > 5 ? "⚠️ EXCEDE LÍMITES IEEE 519" : "✅ DENTRO DE LÍMITES NORMATIVOS"}
                                </div>
                            </div>
                            <div style={{ flex: 1.5, height: 200, background: "#f8f9fa", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center" }}>
                                <SpectrumChart harmonics={harmR?.harmonics || []} C={reportC} themeKey="proSilver" />
                            </div>
                        </div>
                        {harmR?.steps?.map((s, i) => <StepCard key={i} step={s} themeKey="proSilver" C={reportC} />)}
                    </>
                )}

                {/* SECCIÓN 5: ESTABILIDAD */}
                {stabR && (
                    <>
                        <SectionHeader num="5" title="Estabilidad Dinámica Transitoria" />
                        <div style={{ background: stabR?.stable ? "#f0fdf4" : "#fef2f2", padding: 15, borderRadius: 8, marginBottom: 20, fontWeight: 800, textAlign: "center" }}>
                            ESTADO POST-FALLA: {stabR?.stable ? "✅ DINÁMICA ESTABLE" : "⚠️ COLAPSO DINÁMICO / INESTABILIDAD"}
                        </div>
                        <div style={{ height: 280, width: "100%", background: "#f8f9fa", borderRadius: 12, overflow: "hidden", marginBottom: 30, display: "flex", alignItems: "center", justifyContent: "center" }}>
                            <SwingChart pts={stabR?.pts || []} C={reportC} themeKey="proSilver" />
                        </div>
                        {stabR?.steps?.map((s, i) => <StepCard key={i} step={s} themeKey="proSilver" C={reportC} />)}
                    </>
                )}

                {/* SECCIÓN 6: PROTECCIONES */}
                {protR && (
                    <>
                        <SectionHeader num="6" title="Coordinación de Protecciones (ANSI 51/50)" />
                        <div style={{ height: 400, width: "100%", background: "#fff", border: "1px solid #eee", borderRadius: 12, marginBottom: 30, padding: 20 }}>
                            <RelayChart curves={protR?.curves || []} C={reportC} themeKey="proSilver" />
                        </div>
                        <p style={{ fontSize: 11, color: "#666", fontStyle: "italic", marginBottom: 20 }}>Gráfica Log-Log que representa la coordinación entre relés de sobrecorriente temporizada e instantánea.</p>
                        {protR?.steps?.map((s, i) => <StepCard key={i} step={s} themeKey="proSilver" C={reportC} />)}
                    </>
                )}

                {/* SECCIÓN 7: DESPACHO ECONÓMICO */}
                {edR && (
                    <>
                        <SectionHeader num="7" title="Despacho Económico y Costos" />
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 }}>
                            <div style={{ background: "#eff6ff", padding: 20, borderRadius: 12 }}>
                                <div style={{ fontSize: 10, color: "#3b82f6", fontWeight: 800 }}>COSTO OPERATIVO TOTAL</div>
                                <div style={{ fontSize: 28, fontWeight: 900 }}>{parseFloat(edR?.totalCost || 0).toFixed(2)} $/h</div>
                            </div>
                            <div style={{ background: "#f5f3ff", padding: 20, borderRadius: 12 }}>
                                <div style={{ fontSize: 10, color: "#8b5cf6", fontWeight: 800 }}>COSTO MARGINAL (λ)</div>
                                <div style={{ fontSize: 28, fontWeight: 900 }}>{parseFloat(edR?.lambda || 0).toFixed(4)} $/MWh</div>
                            </div>
                        </div>
                        {edR?.steps?.map((s, i) => <StepCard key={i} step={s} themeKey="proSilver" C={reportC} />)}
                    </>
                )}

                {/* SECCIÓN 8: PERFIL DE CARGA */}
                {profR && (
                    <>
                        <SectionHeader num="8" title="Simulación de Perfil de Carga (24h)" />
                        <div style={{ height: 250, width: "100%", background: "#f8f9fa", borderRadius: 12, marginBottom: 30, padding: 20 }}>
                            <LoadChart data={profR.results || []} C={reportC} themeKey="proSilver" />
                        </div>
                        <div style={{ border: "1px solid #eee", borderRadius: 8, overflow: "hidden" }}>
                            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 10 }}>
                                <thead style={{ background: "#f1f5f9" }}>
                                    <tr>
                                        <th style={{ padding: 10, textAlign: "left" }}>PARÁMETRO</th>
                                        <th style={{ padding: 10, textAlign: "left" }}>VALOR</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr style={{ borderBottom: "1px solid #eee" }}><td style={{ padding: 10 }}>PICO DE CARGA</td><td style={{ padding: 10, fontWeight: 800 }}>{parseFloat(profR?.peakH?.load || 0).toFixed(2)} MW</td></tr>
                                    <tr style={{ borderBottom: "1px solid #eee" }}><td style={{ padding: 10 }}>FACTOR DE CARGA (LF)</td><td style={{ padding: 10, fontWeight: 800 }}>{parseFloat(profR?.loadFactor || 0).toFixed(3)}</td></tr>
                                    <tr style={{ borderBottom: "1px solid #eee" }}><td style={{ padding: 10 }}>CARGA PROMEDIO</td><td style={{ padding: 10, fontWeight: 800 }}>{parseFloat(profR?.avgLoad || 0).toFixed(2)} MW</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </>
                )}

                {/* PIE DE PÁGINA */}
                <div style={{ marginTop: 80, borderTop: "1px solid #eee", paddingTop: 30, textAlign: "center", color: "#999", fontSize: 10 }}>
                    <p>© 2026 POWER ANALYZER PRO. DOCUMENTO CERTIFICADO PARA USO DE INGENIERÍA.</p>
                </div>
            </div>
        </div>
    );
};
