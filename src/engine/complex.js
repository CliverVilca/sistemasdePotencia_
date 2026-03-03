export const cx = {
    add: (a, b) => ({ r: a.r + b.r, i: a.i + b.i }),
    sub: (a, b) => ({ r: a.r - b.r, i: a.i - b.i }),
    mul: (a, b) => ({
        r: a.r * b.r - a.i * b.i,
        i: a.r * b.i + a.i * b.r
    }),
    div: (a, b) => {
        const d = b.r * b.r + b.i * b.i;
        return {
            r: (a.r * b.r + a.i * b.i) / d,
            i: (a.i * b.r - a.r * b.i) / d
        };
    },
    abs: (a) => Math.sqrt(a.r * a.r + a.i * a.i),
    ang: (a) => (Math.atan2(a.i, a.r) * 180) / Math.PI,
    pol: (m, d) => {
        const r = (d * Math.PI) / 180;
        return { r: m * Math.cos(r), i: m * Math.sin(r) };
    },
    conj: (a) => ({ r: a.r, i: -a.i }),
    fix: (n, d = 4) => parseFloat((n ?? 0).toFixed(d)),
    toFixedSafe: (n, d = 2) => {
        const val = parseFloat(n);
        return isNaN(val) ? (0).toFixed(d) : val.toFixed(d);
    }
};
