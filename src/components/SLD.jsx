import React, { useRef, useState, useCallback, useEffect } from 'react';

export const SLD = ({
    buses, lines, transformers, lfResult, scResult, faultBusId, animFault,
    onSelBus, onSelLine, selId, selType, onDrag, edMode, onAddLine, onAddTx, onAddSVC, onAddShunt, onDelBus, addTemplate,
    themeKey, C
}) => {
    const svgRef = useRef(null);
    const [dragging, setDragging] = useState(null);
    const [off, setOff] = useState({ x: 0, y: 0 });
    const [connFrom, setConnFrom] = useState(null);
    const [hoverId, setHoverId] = useState(null);

    const bc = (t) => ({ slack: C.slack, PV: C.pv, PQ: C.pq, TX: C.tx }[t] || C.text);
    const [dim, setDim] = useState({ w: 1000, h: 750 });
    const containerRef = useRef(null);

    useEffect(() => {
        if (!containerRef.current) return;
        const obs = new ResizeObserver(ent => {
            const { width, height } = ent[0].contentRect;
            if (width > 0 && height > 0) setDim({ w: width, h: height });
        });
        obs.observe(containerRef.current);
        return () => obs.disconnect();
    }, []);

    const onMD = useCallback((e, id) => {
        e.stopPropagation();
        if (edMode === "connect") {
            if (connFrom === null) { setConnFrom(id); }
            else if (connFrom !== id) { onAddLine(connFrom, id); setConnFrom(null); }
            return;
        }
        if (edMode === "addTx") {
            if (connFrom === null) { setConnFrom(id); }
            else if (connFrom !== id) { onAddTx(connFrom, id); setConnFrom(null); }
            return;
        }
        if (edMode === "delete") { onDelBus(id); return; }

        const svg = svgRef.current;
        if (!svg) return;
        const pt = svg.createSVGPoint();
        pt.x = e.clientX; pt.y = e.clientY;
        const sp = pt.matrixTransform(svg.getScreenCTM().inverse());
        const bus = buses.find(b => b.id === id);
        if (!bus) return;

        setDragging(id);
        setOff({ x: sp.x - bus.x, y: sp.y - bus.y });
        onSelBus(id);
    }, [edMode, connFrom, onAddLine, onAddTx, onDelBus, buses, onSelBus]);

    const onMM = useCallback(e => {
        if (dragging === null) return;
        const svg = svgRef.current;
        if (!svg) return;
        const pt = svg.createSVGPoint();
        pt.x = e.clientX; pt.y = e.clientY;
        const sp = pt.matrixTransform(svg.getScreenCTM().inverse());
        onDrag(dragging, sp.x - off.x, sp.y - off.y);
    }, [dragging, off, onDrag]);

    const onMU = useCallback(() => setDragging(null), []);

    const Vres = lfResult?.V, flows = lfResult?.flows || [];
    const allEls = [...lines.map((l, i) => ({ ...l, idx: i, isTx: false })), ...(transformers || []).map((t, i) => ({ ...t, idx: lines.length + i, isTx: true }))];

    const bestViewBox = React.useMemo(() => {
        if (buses.length === 0) return "0 0 1200 800";
        const xs = buses.map(b => b.x), ys = buses.map(b => b.y);
        const minX = Math.min(...xs), maxX = Math.max(...xs), midX = (minX + maxX) / 2;
        const minY = Math.min(...ys), maxY = Math.max(...ys), midY = (minY + maxY) / 2;
        const cW = maxX - minX, cH = maxY - minY;

        // Vista Panorámica: Padding generoso para evitar recortes de etiquetas/iconos
        const pad = 1.8;
        const margin = 300;

        let vW = Math.max(1200, (cW + margin) * pad);
        let vH = Math.max(900, (cH + margin) * pad);

        const vAR = vW / vH, dAR = dim.w / dim.h;
        if (dAR > vAR) { vW = vH * dAR; } else { vH = vW / dAR; }

        // Elevación Superior: Ajuste de horizonte para centrado focal optimizado
        const lift = vH * 0.22;
        return `${midX - vW / 2} ${midY - vH / 2 + lift} ${vW} ${vH}`;
    }, [buses, dim]);

    const vbArr = bestViewBox.split(" ");

    return (
        <div ref={containerRef} style={{ position: "relative", flex: 1, overflow: "hidden", background: themeKey === "proMidnight" ? "#0b1220" : "#f1f5f9" }}>
            {/* LIBRERÍA DE TOPOLOGÍAS (Frotante glass) */}
            {!lfResult && !scResult && (
                <div style={{ position: "absolute", top: 20, right: 20, zIndex: 50, display: "flex", gap: 8 }}>
                    <button onClick={() => addTemplate?.("star")} style={{ padding: "8px 16px", background: `${C.panel}ee`, border: `1px solid ${C.border}`, borderRadius: 10, color: C.text, fontSize: 10, fontWeight: 900, cursor: "pointer", backdropFilter: "blur(10px)", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }}>💠 ESTRELLA</button>
                    <button onClick={() => addTemplate?.("parallel")} style={{ padding: "8px 16px", background: `${C.panel}ee`, border: `1px solid ${C.border}`, borderRadius: 10, color: C.text, fontSize: 10, fontWeight: 900, cursor: "pointer", backdropFilter: "blur(10px)", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }}>⚡ PARALELO</button>
                </div>
            )}

            <svg id="sld-svg" ref={svgRef} width="100%" height="100%"
                viewBox={bestViewBox}
                preserveAspectRatio="xMidYMid meet"
                style={{ cursor: dragging !== null ? "grabbing" : "default", display: "block" }}
                onMouseMove={onMM} onMouseUp={onMU} onMouseLeave={onMU}>

                <defs>
                    <pattern id="gridSmall" width="15" height="15" patternUnits="userSpaceOnUse"><path d="M 15 0 L 0 0 0 15" fill="none" stroke={C.border} strokeWidth="0.2" opacity="0.3" /></pattern>
                    <pattern id="gridLarge" width="75" height="75" patternUnits="userSpaceOnUse"><rect width="75" height="75" fill="url(#gridSmall)" /><path d="M 75 0 L 0 0 0 75" fill="none" stroke={C.border} strokeWidth="0.5" opacity="0.5" /></pattern>

                    <filter id="busGlow"><feGaussianBlur stdDeviation="3" result="blur" /><feComposite in="SourceGraphic" in2="blur" operator="over" /></filter>
                    <linearGradient id="busGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#fff" stopOpacity="0.4" /><stop offset="50%" stopColor="#fff" stopOpacity="0.1" /><stop offset="100%" stopColor="#000" stopOpacity="0.2" /></linearGradient>

                    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill={C.line} opacity="0.5" /></marker>
                </defs>

                {/* Fondo Técnico */}
                <rect x={vbArr[0]} y={vbArr[1]} width={vbArr[2]} height={vbArr[3]} fill="url(#gridLarge)" />

                {/* Líneas y Conexiones */}
                {allEls.map(el => {
                    const b1 = buses.find(b => b.id === el.from), b2 = buses.find(b => b.id === el.to);
                    if (!b1 || !b2) return null;
                    const flow = flows.find(f => f && f.id === el.idx);
                    const isSel = selId === el.id && selType === "line";
                    const loading = flow ? Math.min(Math.abs(flow.P) / 100, 1.2) : 0;
                    const color = loading > 1 ? C.fault : loading > 0.8 ? C.warn : el.isTx ? C.tx : C.line;

                    return (
                        <g key={el.id} onClick={() => onSelLine(el.id)} style={{ cursor: "pointer" }}>
                            {/* Glow Path */}
                            <line x1={b1.x} y1={b1.y} x2={b2.x} y2={b2.y} stroke={color} strokeWidth={isSel ? 8 : 4.5} opacity={isSel ? 0.3 : 0.12} filter="url(#busGlow)" />
                            {/* Main Path */}
                            <line x1={b1.x} y1={b1.y} x2={b2.x} y2={b2.y} stroke={color} strokeWidth={isSel ? 4 : 3.5} markerMid="url(#arrow)" />

                            {/* Flow Animation Particles */}
                            {flow && (
                                <line x1={b1.x} y1={b1.y} x2={b2.x} y2={b2.y} stroke={color} strokeWidth={2} strokeDasharray="4,24" opacity={0.6}>
                                    <animate attributeName="stroke-dashoffset" from="100" to="0" dur={`${3 - loading * 2}s`} repeatCount="indefinite" />
                                </line>
                            )}

                            {/* Transformer Symbol */}
                            {el.isTx && (
                                <g transform={`translate(${(b1.x + b2.x) / 2}, ${(b1.y + b2.y) / 2})`}>
                                    <circle cx="-6" cy="0" r="8" fill={C.panel} stroke={color} strokeWidth="2" />
                                    <circle cx="6" cy="0" r="8" fill={C.panel} stroke={color} strokeWidth="2" />
                                </g>
                            )}

                            {/* Branch Info Badge (Floating) */}
                            {flow && (
                                <g transform={`translate(${(b1.x + b2.x) / 2}, ${(b1.y + b2.y) / 2 - 20})`}>
                                    <rect x="-22" y="-9" width="44" height="18" rx="5" fill={C.panel} stroke={color} strokeWidth="1" opacity="0.9" />
                                    <text textAnchor="middle" y="3" fill={C.text} fontSize="8" fontWeight="900" fontFamily="JetBrains Mono">{(parseFloat(flow.P || 0)).toFixed(1)} MW</text>
                                </g>
                            )}
                        </g>
                    );
                })}

                {/* Barras de Barra (Buses) */}
                {buses.map((bus, busIdx) => {
                    const col = bc(bus.type);
                    const Vr = Vres?.[busIdx];
                    const isSel = selId === bus.id && selType === "bus";
                    const isFault = animFault && faultBusId === bus.id;
                    const Vok = Vr ? (Vr.mag >= 0.95 && Vr.mag <= 1.05) : true;

                    return (
                        <g key={bus.id} onMouseDown={e => onMD(e, bus.id)}
                            onMouseEnter={() => setHoverId(bus.id)} onMouseLeave={() => setHoverId(null)}
                            style={{ cursor: dragging === bus.id ? "grabbing" : "grab" }}>

                            {/* Selection Effect */}
                            {(isSel || hoverId === bus.id) && <rect x={bus.x - 48} y={bus.y - 15} width={96} height={30} rx={15} fill={col} opacity={0.05} />}

                            {/* Bus Bar Body (Cyber style) scaled up */}
                            <rect x={bus.x - 40} y={bus.y - 4} width={80} height={8} rx={4} fill={col} filter="url(#busGlow)" />
                            <rect x={bus.x - 40} y={bus.y - 4} width={80} height={8} rx={4} fill="url(#busGrad)" />

                            {/* Status Indicator (LED) */}
                            <circle cx={bus.x - 45} cy={bus.y} r={3} fill={Vok ? C.ok : C.warn} />

                            {/* Label & Details scaled up */}
                            <g transform={`translate(${bus.x}, ${bus.y - 15})`}>
                                <text textAnchor="middle" fill={C.text} fontSize="11" fontWeight="900" style={{ letterSpacing: -0.2 }}>{bus.name}</text>
                                <text textAnchor="middle" y="42" fill={C.muted} fontSize="7" fontWeight="800" textTransform="uppercase">{bus.vBase}kV | {bus.type}</text>
                            </g>

                            {/* Diagnostic Badge (Voltage) scaled up */}
                            {Vr && (
                                <g transform={`translate(${bus.x + 48}, ${bus.y})`}>
                                    <rect x="0" y="-10" width="54" height="20" rx="10" fill={C.panel} stroke={Vok ? C.ok : C.warn} strokeWidth="1.5" opacity="0.95" />
                                    <text x="27" y="3" textAnchor="middle" fill={Vok ? C.ok : C.warn} fontSize="10" fontWeight="900" fontFamily="JetBrains Mono">{Vr.mag} pu</text>
                                </g>
                            )}

                            {/* Symbology Icons scaled up */}
                            {bus.type === "slack" && (
                                <g transform={`translate(${bus.x - 15}, ${bus.y - 55})`}>
                                    <path d="M15 0 L30 25 L0 25 Z" fill={C.panel} stroke={C.slack} strokeWidth="2.5" />
                                    <path d="M8 18 Q15 8 22 18" fill="none" stroke={C.slack} strokeWidth="2" />
                                    <line x1="15" y1="25" x2="15" y2="52" stroke={C.slack} strokeWidth="2.5" />
                                    <text x="15" y="-6" textAnchor="middle" fill={C.slack} fontSize="8" fontWeight="900">GRID</text>
                                </g>
                            )}

                            {bus.type === "PV" && (
                                <g transform={`translate(${bus.x - 15}, ${bus.y - 55})`}>
                                    <circle cx="15" cy="15" r="12" fill={C.panel} stroke={C.pv} strokeWidth="2.5" />
                                    <text x="15" y="21" textAnchor="middle" fill={C.pv} fontSize="18" fontWeight="900">~</text>
                                    <line x1="15" y1="27" x2="15" y2="52" stroke={C.pv} strokeWidth="2.5" />
                                    <text x="15" y="-6" textAnchor="middle" fill={C.pv} fontSize="8" fontWeight="900">GEN</text>
                                </g>
                            )}

                            {bus.type === "PQ" && (bus.Pload || 0) > 0 && (
                                <g transform={`translate(${bus.x}, ${bus.y + 8})`}>
                                    <path d="M-8 0 L8 0 L0 15 Z" fill={C.pq} opacity="0.8" />
                                    <text y="26" textAnchor="middle" fill={C.pq} fontSize="8" fontWeight="900">LOAD</text>
                                </g>
                            )}

                            {/* Fault Visual */}
                            {isFault && (
                                <g>
                                    <circle cx={bus.x} cy={bus.y} r="25" fill={C.fault} opacity="0.1">
                                        <animate attributeName="r" values="20;35;20" dur="0.5s" repeatCount="indefinite" />
                                    </circle>
                                    <text x={bus.x} y={bus.y + 35} textAnchor="middle" fill={C.fault} fontSize="10" fontWeight="900" style={{ letterSpacing: 1 }}>FAULT!</text>
                                </g>
                            )}
                        </g>
                    );
                })}

                {/* Connection Overlay */}
                {connFrom !== null && (
                    <g opacity="0.8">
                        <rect x={vbArr[0]} y={vbArr[1]} width={vbArr[2]} height="30" fill={C.accent} />
                        <text x="50%" y="20" textAnchor="middle" fill="#fff" fontSize="12" fontWeight="900">SELECT TARGET BUS TO FINALIZE CONNECTION</text>
                    </g>
                )}
            </svg>

            {/* Diagram Legend (Minimalist Glass) */}
            <div style={{ position: "absolute", bottom: 20, right: 20, zIndex: 10, display: "flex", flexDirection: "column", gap: 6, background: `${C.panel}cc`, padding: 10, borderRadius: 12, border: `1px solid ${C.border}`, backdropFilter: "blur(6px)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}><div style={{ width: 8, height: 2, background: C.line }} /> <span style={{ fontSize: 9, fontWeight: 700, opacity: 0.8 }}>Transmission</span></div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}><div style={{ width: 8, height: 2, background: C.tx }} /> <span style={{ fontSize: 9, fontWeight: 700, opacity: 0.8 }}>Transformer</span></div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}><div style={{ width: 8, height: 8, borderRadius: 2, background: C.slack }} /> <span style={{ fontSize: 9, fontWeight: 700, opacity: 0.8 }}>Slack Node</span></div>
            </div>
        </div>
    );
};
