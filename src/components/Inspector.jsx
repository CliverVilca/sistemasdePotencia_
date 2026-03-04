import React from 'react';
import { Inp, Sel, Btn } from './UI';

export const Inspector = ({
    selBus, selLineEl, lfR, scR, faultBus,
    setFaultBus, execSC, transformers, flows, C,
    updBus, updLine, updTx, onDelBus, onDelLineEl
}) => {
    const bc = (t) => ({ slack: C.slack, PV: C.pv, PQ: C.pq, TX: C.tx }[t] || C.text);
    const selFlow = selLineEl ? flows.find(f => f && (f.id === selLineEl.id || (f.from === selLineEl.from + 1 && f.to === selLineEl.to + 1))) : null;

    return (
        <div style={{ width: 240, background: C.panel, borderLeft: `1px solid ${C.border}`, padding: 16, overflowY: "auto", flexShrink: 0, boxShadow: "-2px 0 10px rgba(0,0,0,0.02)" }}>
            <div style={{ color: C.accent, fontWeight: 800, fontSize: 11, marginBottom: 16, textTransform: "uppercase", letterSpacing: 1.5, display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 14 }}>🔍</span> INSPECTOR
            </div>

            {!selBus && !selLineEl && (
                <div style={{ color: C.muted, fontSize: 11, lineHeight: 1.6 }}>
                    <div style={{ background: C.dim, padding: 12, borderRadius: 12, border: `1px solid ${C.border}`, marginBottom: 16 }}>
                        <div style={{ fontWeight: 800, marginBottom: 8, color: C.text }}>Pasos rápidos</div>
                        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                            <div>1️⃣ Usa <b>Mover</b> para situar</div>
                            <div>2️⃣ <b>Barra</b> añade nudos</div>
                            <div>3️⃣ <b>Línea</b> conecta barras</div>
                            <div>4️⃣ <b>TX</b> añade trafos</div>
                            <div>5️⃣ <b>Flujo P</b> simula</div>
                        </div>
                    </div>
                </div>
            )}

            {selBus && (() => {
                const col = bc(selBus.type), Vr = lfR?.V[selBus.id];
                return (
                    <div>
                        <div style={{ background: `${col}15`, border: `1px solid ${col}33`, borderRadius: 12, padding: 14, marginBottom: 16 }}>
                            <div style={{ color: col, fontWeight: 900, fontSize: 16, marginBottom: 2 }}>{selBus.name}</div>
                            <Sel label="Tipo de Barra" value={selBus.type} onChange={v => updBus(selBus.id, "type", v)} options={[{ v: "slack", l: "Slack (Ref)" }, { v: "PV", l: "PV (Gen)" }, { v: "PQ", l: "PQ (Carga)" }]} C={C} />
                        </div>

                        <div style={{ marginBottom: 16 }}>
                            <Inp label="Vbase (kV)" value={selBus.Vbase} onChange={v => updBus(selBus.id, "Vbase", v)} C={C} />
                            <Inp label="V objetivo (pu)" value={selBus.Vmag} onChange={v => updBus(selBus.id, "Vmag", v)} C={C} />
                            <Inp label="P Deseada (MW)" value={selBus.Psch} onChange={v => updBus(selBus.id, "Psch", v)} C={C} />
                            <Inp label="Q Deseada (MVAr)" value={selBus.Qsch} onChange={v => updBus(selBus.id, "Qsch", v)} C={C} />
                        </div>

                        {Vr && (
                            <div style={{ background: `${Vr.mag >= 0.95 && Vr.mag <= 1.05 ? C.ok : C.warn}0e`, border: `1px solid ${Vr.mag >= 0.95 && Vr.mag <= 1.05 ? C.ok : C.warn}35`, borderRadius: 12, padding: 12, marginBottom: 12 }}>
                                <div style={{ color: C.muted, fontSize: 8, fontWeight: 800, marginBottom: 4, textTransform: "uppercase" }}>Resultado Flujo</div>
                                <div style={{ color: Vr.mag >= 0.95 && Vr.mag <= 1.05 ? C.ok : C.warn, fontWeight: 900, fontSize: 18, fontFamily: "'JetBrains Mono'" }}>{Vr.mag} pu</div>
                                <div style={{ color: C.text, fontSize: 10, fontWeight: 600 }}>∠{Vr.ang}°</div>
                            </div>
                        )}

                        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                            <Btn sm full color={C.fault} onClick={() => { setFaultBus(String(selBus.id)); execSC(); }} C={C}>⚡ Simular falla aquí</Btn>
                            <Btn sm full color={C.fault} style={{ opacity: 0.6 }} onClick={() => onDelBus(selBus.id)} C={C}>✕ Eliminar Barra</Btn>
                        </div>
                    </div>
                );
            })()}

            {selLineEl && (() => {
                const isTx = transformers.some(t => t.id === selLineEl.id);
                const loading = selFlow ? Math.min(Math.abs(selFlow.P || 0) / 120, 1) : 0.2;
                const lc = loading > 0.85 ? C.fault : loading > 0.55 ? C.warn : C.ok;

                return (
                    <div>
                        <div style={{ background: `${isTx ? C.tx : C.lineHot}15`, border: `1px solid ${isTx ? C.tx : C.lineHot}33`, borderRadius: 12, padding: 14, marginBottom: 16 }}>
                            <div style={{ color: isTx ? C.tx : C.lineHot, fontWeight: 900, fontSize: 14 }}>{isTx ? "⊛ Transformador" : "⟶ Línea Transmisión"}</div>
                            <div style={{ color: C.muted, fontSize: 10, fontWeight: 800 }}>ID: {selLineEl.id} | B{selLineEl.from + 1} → B{selLineEl.to + 1}</div>
                        </div>

                        <div style={{ marginBottom: 16 }}>
                            <Inp label="R (pu)" value={selLineEl.R} onChange={v => isTx ? updTx(selLineEl.id, "R", v) : updLine(selLineEl.id, "R", v)} C={C} />
                            <Inp label="X (pu)" value={selLineEl.X} onChange={v => isTx ? updTx(selLineEl.id, "X", v) : updLine(selLineEl.id, "X", v)} C={C} />
                            {isTx && <Inp label="Tap / Relación" value={selLineEl.tap || 1} onChange={v => updTx(selLineEl.id, "tap", v)} C={C} />}
                        </div>

                        {selFlow && (
                            <div style={{ background: `${lc}0e`, border: `1px solid ${lc}35`, borderRadius: 12, padding: 12, marginBottom: 16 }}>
                                <div style={{ color: C.muted, fontSize: 8, fontWeight: 800, marginBottom: 6, textTransform: "uppercase" }}>Flujo Activo & Carga</div>
                                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                                    <span style={{ color: C.text, fontWeight: 900, fontSize: 16 }}>{selFlow.P} MW</span>
                                    <span style={{ color: lc, fontWeight: 900, fontSize: 16 }}>{(parseFloat(loading || 0) * 100).toFixed(0)}%</span>
                                </div>
                                <div style={{ background: C.tag, borderRadius: 10, height: 6, overflow: "hidden" }}>
                                    <div style={{ width: `${loading * 100}%`, height: "100%", background: lc, borderRadius: 10 }} />
                                </div>
                            </div>
                        )}
                        <Btn sm full color={C.fault} style={{ opacity: 0.6 }} onClick={() => onDelLineEl(selLineEl.id, isTx)} C={C}>✕ Eliminar Elemento</Btn>
                    </div>
                );
            })()}
        </div>
    );
};
