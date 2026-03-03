import React from 'react';

export const Inp = ({ label, value, onChange, type = "number", raw = false, step = "0.01", C }) => (
    <div style={{ marginBottom: 12 }}>
        <label style={{ display: "block", color: C.muted, fontSize: 10, fontWeight: 800, marginBottom: 5, textTransform: "uppercase", letterSpacing: 0.5 }}>{label}</label>
        <input type={raw ? "text" : type} step={step} value={value} onChange={e => onChange(e.target.value)}
            style={{ width: "100%", background: C.dim, border: `1.5px solid ${C.border}`, borderRadius: 10, padding: "10px 12px", color: C.text, fontSize: 13, fontWeight: 600, outline: "none", transition: "all 0.2s" }}
            onFocus={e => { e.target.style.borderColor = C.accent; e.target.style.boxShadow = `0 0 0 3px ${C.accent}15`; }}
            onBlur={e => { e.target.style.borderColor = C.border; e.target.style.boxShadow = "none"; }} />
    </div>
);

export const Sel = ({ label, value, onChange, options, C }) => (
    <div style={{ marginBottom: 12 }}>
        <label style={{ display: "block", color: C.muted, fontSize: 10, fontWeight: 800, marginBottom: 5, textTransform: "uppercase", letterSpacing: 0.5 }}>{label}</label>
        <select value={value} onChange={e => onChange(e.target.value)}
            style={{ width: "100%", background: C.dim, border: `1.5px solid ${C.border}`, borderRadius: 10, padding: "10px 12px", color: C.text, fontSize: 13, fontWeight: 600, outline: "none", cursor: "pointer", appearance: "none" }}>
            {options.map(o => <option key={o.v} value={o.v}>{o.l}</option>)}
        </select>
    </div>
);

export const Btn = ({ children, onClick, active, color, sm, style, title, C }) => (
    <button title={title} onClick={onClick} style={{
        padding: sm ? "6px 12px" : "12px 24px",
        background: active ? color : C.panel,
        color: active ? "#fff" : color,
        border: `1.5px solid ${color}`,
        borderRadius: sm ? 8 : 12,
        fontSize: sm ? 10 : 13,
        fontWeight: 800,
        cursor: "pointer",
        transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
        ...style,
        boxShadow: active ? `0 4px 12px ${color}33` : "none",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 6
    }}>{children}</button>
);

export const KPI = ({ label, value, color, sm, C }) => (
    <div style={{ background: C.panel, border: `1px solid ${C.border}`, borderRadius: 14, padding: sm ? "10px 14px" : "18px 22px", textAlign: "center", minWidth: 0, boxShadow: "0 4px 6px -1px rgba(0,0,0,0.05)" }}>
        <div style={{ color: C.muted, fontSize: sm ? 9 : 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>{label}</div>
        <div style={{ color: color || C.accent, fontSize: sm ? 14 : 26, fontWeight: 900, lineHeight: 1.1 }}>{value}</div>
    </div>
);
