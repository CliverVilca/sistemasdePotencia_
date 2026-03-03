import React from 'react';

const f = (n, d = 1) => {
    const v = parseFloat(n);
    return isNaN(v) ? (0).toFixed(d) : v.toFixed(d);
};

const R_STYLE = {
    bg: "#f3f4f6", // ggplot2 gray background
    grid: "#ffffff",
    axis: "#4b5563"
};

const Grid = ({ w, h, p, xTicks, yTicks, C, themeKey }) => {
    const isDark = themeKey === "proMidnight";
    const bg = isDark ? "#111827" : "#f3f4f6";
    const grid = isDark ? "#ffffff08" : "#ffffff";
    return (
        <g>
            <rect x={p} y={p} width={w - p * 2} height={h - p * 2} fill={bg} rx={4} />
            {xTicks.map(x => <line key={x} x1={x} y1={p} x2={x} y2={h - p} stroke={grid} strokeWidth={1} />)}
            {yTicks.map(y => <line key={y} x1={p} y1={y} x2={w - p} y2={y} stroke={grid} strokeWidth={1} />)}
        </g>
    );
};

export const SwingChart = ({ pts, C, themeKey }) => {
    if (!pts || !pts.length) return null;
    const W = 380, H = 140, p = 30;
    const ds = pts.map(d => d.d), ts = pts.map(d => d.t);
    const tM = Math.max(...ts) || 2, dMin = Math.min(...ds), dMax = Math.max(...ds);
    const tx = t => p + (t / tM) * (W - p * 2), ty = d => H - p - ((d - dMin) / ((dMax - dMin) || 1)) * (H - p * 2);

    const xT = [tx(0), tx(tM / 2), tx(tM)];
    const yT = [ty(dMin), ty((dMin + dMax) / 2), ty(dMax)];

    return (
        <svg width={W} height={H} style={{ borderRadius: 12, border: `1px solid ${C.border}`, boxShadow: "0 4px 10px rgba(0,0,0,0.1)" }}>
            <Grid w={W} h={H} p={p} xTicks={xT} yTicks={yT} C={C} themeKey={themeKey} />
            <text x={8} y={H / 2} fill={C.muted} fontSize={8} fontWeight="800" transform={`rotate(-90, 8, ${H / 2})`} textAnchor="middle">δ Angle (°)</text>
            <text x={W / 2} y={H - 8} fill={C.muted} fontSize={8} fontWeight="800" textAnchor="middle">Time (seconds)</text>
            <path d={pts.map((d, i) => `${i ? "L" : "M"}${f(tx(d.t), 1)} ${f(ty(d.d), 1)}`).join(" ")} fill="none" stroke={C.accent} strokeWidth={2.5} strokeLinejoin="round" filter="url(#glow)" />
            <defs><filter id="glow"><feGaussianBlur stdDeviation="1.5" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter></defs>
        </svg>
    );
};

export const SpectrumChart = ({ harmonics, V1, C, themeKey }) => {
    if (!harmonics || !harmonics.length) return null;
    const W = 380, H = 140, p = 30;
    const bars = [{ h: 1, Vh: parseFloat(V1 || 220) }, ...harmonics];
    const maxV = Math.max(...bars.map(b => b.Vh)) || 1;
    const bw = (W - p * 2) / (bars.length + 1);

    const xT = bars.map((_, i) => p + (i + 0.5) * bw);
    const yT = [H - p, H - p - 40, H - p - 80];

    return (
        <svg width={W} height={H} style={{ borderRadius: 12, border: `1px solid ${C.border}`, boxShadow: "0 4px 10px rgba(0,0,0,0.1)" }}>
            <Grid w={W} h={H} p={p} xTicks={[]} yTicks={yT} C={C} themeKey={themeKey} />
            <text x={10} y={H / 2} fill={C.muted} fontSize={8} fontWeight="800" transform={`rotate(-90, 10, ${H / 2})`} textAnchor="middle">Magnitude (V)</text>
            {bars.map((b, i) => {
                const bh = (b.Vh / maxV) * (H - p * 2);
                const x = p + (i + 0.5) * bw;
                return (
                    <g key={i}>
                        <rect x={x - bw * 0.3} y={H - p - bh} width={bw * 0.6} height={bh} fill={i === 0 ? C.accent : C.a2} rx={3} opacity={0.9} />
                        <text x={x} y={H - p + 12} fill={C.muted} fontSize={7} fontWeight="900" textAnchor="middle">h{b.h}</text>
                    </g>
                );
            })}
        </svg>
    );
};

export const LoadChart = ({ data, C, themeKey }) => {
    if (!data || !data.length) return null;
    const W = 480, H = 160, p = 35;
    const maxL = Math.max(...data.map(d => d.load)) || 100;
    const tx = h => p + (h / 23) * (W - p * 2), ty = l => H - p - (l / (maxL * 1.1)) * (H - p * 2);
    const path = data.map((d, i) => `${i ? "L" : "M"}${f(tx(d.h), 1)} ${f(ty(d.load), 1)}`).join(" ");

    const xT = [0, 6, 12, 18, 23].map(h => tx(h));
    const yT = [0, 0.5, 1.0].map(v => ty(v * maxL));

    return (
        <svg width={W} height={H} style={{ borderRadius: 16, border: `1px solid ${C.border}`, display: "block", boxShadow: "0 6px 15px rgba(0,0,0,0.12)" }}>
            <Grid w={W} h={H} p={p} xTicks={xT} yTicks={yT} C={C} themeKey={themeKey} />
            <text x={12} y={H / 2} fill={C.muted} fontSize={8} fontWeight="900" transform={`rotate(-90, 12, ${H / 2})`} textAnchor="middle">Power (MW)</text>
            <text x={W / 2} y={H - 8} fill={C.muted} fontSize={8} fontWeight="900" textAnchor="middle">Time of Day (Hours)</text>
            <path d={`${path} L${tx(23)} ${H - p} L${tx(0)} ${H - p} Z`} fill={C.accent} opacity={0.15} />
            <path d={path} fill="none" stroke={C.accent} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" />
            {xT.map((x, i) => <text key={i} x={x} y={H - p + 14} fill={C.muted} fontSize={7} fontWeight="900" textAnchor="middle">{[0, 6, 12, 18, 23][i]}:00</text>)}
        </svg>
    );
};

export const RelayChart = ({ curves, C, themeKey }) => {
    if (!curves || !curves.length) return null;
    const W = 380, H = 200, p = 35;
    const logM = v => Math.log10(Math.max(v, 1.1));
    const tx = m => p + (logM(m) - logM(1.1)) / (logM(50) - logM(1.1)) * (W - p * 2);
    const ty = t => H - p - ((Math.log10(Math.max(t, 0.01)) - Math.log10(0.01)) / (Math.log10(100) - Math.log10(0.01))) * (H - p * 2);

    const xT = [2, 5, 10, 20, 50].map(m => tx(m));
    const yT = [0.01, 0.1, 1, 10, 100].map(t => ty(t));
    const colors = [C.accent, C.pv, C.pq, C.a4];

    return (
        <svg width={W} height={H} style={{ borderRadius: 16, border: `1px solid ${C.border}`, boxShadow: "0 6px 15px rgba(0,0,0,0.12)" }}>
            <Grid w={W} h={H} p={p} xTicks={xT} yTicks={yT} C={C} themeKey={themeKey} />
            <text x={W / 2} y={H - 8} fill={C.muted} fontSize={8} fontWeight="900" textAnchor="middle">Multiplier M (I/Ip)</text>
            <text x={12} y={H / 2} fill={C.muted} fontSize={8} fontWeight="900" transform={`rotate(-90, 12, ${H / 2})`} textAnchor="middle">Operating Time t (s)</text>
            {curves.map((c, ci) => {
                const path = c.pts.filter(pt => pt.t > 0 && pt.t < 200).map((pt, i) => `${i ? "L" : "M"}${f(tx(pt.M), 1)} ${f(ty(pt.t), 1)}`).join(" ");
                return (
                    <g key={ci}>
                        <path d={path} fill="none" stroke={colors[ci % 4]} strokeWidth={2.5} strokeLinejoin="round" opacity={0.8} />
                        <text x={tx(20)} y={ty(parseFloat(c.t_op) || 1)} fill={colors[ci % 4]} fontSize={7} fontWeight="900" textAnchor="start">{c.name}</text>
                    </g>
                );
            })}
        </svg>
    );
};
