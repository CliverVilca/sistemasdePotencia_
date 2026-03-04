import { cx } from "./complex";

// ── MOTOR: NEWTON-RAPHSON ────────────────────────────────────────
export function runLF(buses, lines, transformers = []) {
    try {
        const n = buses.length;
        if (n < 2) return null;
        const Y = Array.from({ length: n }, () => Array.from({ length: n }, () => ({ r: 0, i: 0 })));
        const details = [];
        [...lines, ...transformers].forEach((el, idx) => {
            const { from, to, R, X, tap = 1 } = el;
            if (from >= n || to >= n || from < 0 || to < 0) return;
            const isTx = idx >= lines.length;
            const d = R * R + X * X; if (d < 1e-12) return;
            const y = { r: R / d, i: -X / d };
            if (isTx) {
                const t = tap || 1;
                const yt2 = { r: y.r / (t * t), i: y.i / (t * t) }, ytm = { r: y.r / t, i: y.i / t };
                details.push({ from, to, R, X, tap: t, yr: cx.fix(yt2.r), yi: cx.fix(yt2.i), type: "tx" });
                Y[from][from] = cx.add(Y[from][from], yt2); Y[to][to] = cx.add(Y[to][to], y);
                Y[from][to] = cx.sub(Y[from][to], ytm); Y[to][from] = cx.sub(Y[to][from], ytm);
            } else {
                details.push({ from, to, R, X, yr: cx.fix(y.r), yi: cx.fix(y.i), type: "line" });
                Y[from][to] = cx.sub(Y[from][to], y); Y[to][from] = cx.sub(Y[to][from], y);
                Y[from][from] = cx.add(Y[from][from], y); Y[to][to] = cx.add(Y[to][to], y);
            }
        });
        const G = Y.map(r => r.map(y => y.r)), B = Y.map(r => r.map(y => y.i));
        let V = buses.map(b => +(b.Vmag || 1.0)), th = buses.map(b => +((b.Vang || 0) * Math.PI / 180));
        const iters = []; let converged = false;
        for (let it = 0; it < 60; it++) {
            let maxErr = 0;
            for (let i = 0; i < n; i++) {
                if (buses[i].type === "slack") continue;
                let Pc = 0, Qc = 0;
                for (let j = 0; j < n; j++) {
                    const ang = th[i] - th[j];
                    Pc += V[i] * V[j] * (G[i][j] * Math.cos(ang) + B[i][j] * Math.sin(ang));
                    Qc += V[i] * V[j] * (G[i][j] * Math.sin(ang) - B[i][j] * Math.cos(ang));
                }
                const Ptarget = (buses[i].Psch || 0) / 100;
                const Qtarget = (buses[i].Qsch || 0) / 100;
                const dP = Ptarget - Pc;
                const dQ = (buses[i].type === "PV") ? 0 : Qtarget - Qc;

                maxErr = Math.max(maxErr, Math.abs(dP), Math.abs(dQ));

                const bii = B[i][i] !== 0 ? B[i][i] : -10;
                // Amortiguación y actualización
                th[i] += 0.8 * (dP / (V[i] * (Math.abs(bii) + 0.1)));
                if (buses[i].type === "PQ") {
                    V[i] += 0.8 * (dQ / (V[i] * (Math.abs(bii) + 0.1)));
                }
                // Límites de seguridad
                if (isNaN(V[i])) V[i] = 1.0;
                if (isNaN(th[i])) th[i] = 0;
                V[i] = Math.max(0.6, Math.min(1.4, V[i]));
            }
            iters.push({ it: it + 1, V: V.map((v, i) => ({ mag: cx.fix(v, 4), ang: cx.fix(th[i] * 180 / Math.PI, 2) })), err: cx.fix(maxErr, 6) });
            if (maxErr < 1e-4) { converged = true; break; }
        }
        const flows = [...lines, ...transformers].map((el, idx) => {
            const { from, to, R, X } = el; if (from >= n || to >= n) return null;
            const isTx = idx >= lines.length;
            const d = R * R + X * X; if (d < 1e-12) return null;
            const y = { r: R / d, i: -X / d };
            const Vi = cx.pol(V[from], th[from] * 180 / Math.PI), Vj = cx.pol(V[to], th[to] * 180 / Math.PI);
            const dV = cx.sub(Vi, Vj), I = cx.mul(dV, y);
            const Sf = cx.mul(Vi, cx.conj(I));
            const St = cx.mul(Vj, cx.conj({ r: -I.r, i: -I.i }));
            const loading = Math.min(cx.abs(I) / 1.2, 1);
            return { id: idx, from: from + 1, to: to + 1, P: cx.fix(Sf.r * 100, 2), Q: cx.fix(Sf.i * 100, 2), I: cx.fix(cx.abs(I), 4), loss: cx.fix((Sf.r + St.r) * 100, 3), loading, type: isTx ? "tx" : "line" };
        }).filter(Boolean);
        const Vres = V.map((v, i) => ({ mag: cx.fix(v, 5), ang: cx.fix(th[i] * 180 / Math.PI, 3) }));
        let Pslack = 0, Qslack = 0;
        const si = buses.findIndex(b => b.type === "slack");
        if (si >= 0) { for (let j = 0; j < n; j++) { Pslack += V[si] * V[j] * (G[si][j] * Math.cos(th[si] - th[j]) + B[si][j] * Math.sin(th[si] - th[j])); Qslack += V[si] * V[j] * (G[si][j] * Math.sin(th[si] - th[j]) - B[si][j] * Math.cos(th[si] - th[j])); } }
        const totalLoss = flows.reduce((s, f) => s + (f ? f.loss : 0), 0);
        const steps = [
            { title: "1. YBUS — PARÁMETROS DE ELEMENTOS", formula: "Y_ij = -y_ij | Y_ii = Σy_ij", type: "lineTable", data: details },
            { title: "2. MATRIZ DE CONDUCTANCIA [G]", formula: "G = Re{Ybus}", type: "matrix", data: G.map(r => r.map(x => cx.fix(x, 6))) },
            { title: "3. MATRIZ DE SUSCEPTANCIA [B]", formula: "B = Im{Ybus}", type: "matrix", data: B.map(r => r.map(x => cx.fix(x, 6))) },
            { title: "4. ITERACIONES (CONVERGENCIA)", formula: "Δθ = ΔP/(V·(-Bii)) | ΔV = ΔQ/(-V·Bii)", type: "iters", data: iters.slice(0, 8), converged },
            { title: "5. FLUJOS EN RAMAS", formula: "S_ij = V_i·I_ij* | I_ij = y·(Vi−Vj)", type: "flows", data: flows },
            { title: "6. BALANCE DE POTENCIA", formula: "ΣPgen = ΣPcarga + Ppérdidas", calc: `P_slack=${cx.fix(Pslack * 100, 2)}MW | Q_slack=${cx.fix(Qslack * 100, 2)}MVAr\nPérdidas=${cx.fix(totalLoss, 3)}MW`, type: "plain" },
            { title: "7. PERFIL DE VOLTAJES FINAL", formula: "0.95 pu ≤ |V| ≤ 1.05 pu", type: "voltages", data: Vres.map((v, i) => ({ bus: i + 1, ...v, ok: v.mag >= 0.95 && v.mag <= 1.05 })) },
        ];
        const Gm = G.map(r => r.map(x => cx.fix(x, 6))), Bm = B.map(r => r.map(x => cx.fix(x, 6)));
        return { steps, V: Vres, flows, converged, Pslack: cx.fix(Pslack * 100, 2), Qslack: cx.fix(Qslack * 100, 2), totalLoss: cx.fix(totalLoss, 3), iters, G: Gm, B: Bm, Ydetails: details };
    } catch (e) { return { error: e.message, steps: [], V: [], flows: [], converged: false, totalLoss: 0, Pslack: 0, Qslack: 0 }; }
}

// ── MOTOR: CORTOCIRCUITO ─────────────────────────────────────────
export function runSC(buses, lines, transformers, faultBus, faultType) {
    try {
        let Zth = 0;
        [...lines, ...transformers].forEach(l => { if (l.from === faultBus || l.to === faultBus) Zth += l.X; });
        if (Zth < 0.001) Zth = 0.1;
        const Z1 = Zth, Z2 = Zth * 0.95, Z0 = Zth * 3.0, Vf = buses[faultBus]?.Vmag || 1.0;
        const Vbase = buses[faultBus]?.Vbase || 13.8, Sbase = 100;
        const Ibase = (Sbase * 1000) / (Math.sqrt(3) * Vbase);
        let Ia1 = 0, fPu = 0, label = "";
        if (faultType === "3F") { Ia1 = Vf / Z1; fPu = Ia1; label = "Trifásica"; }
        else if (faultType === "1F") { Ia1 = Vf / (Z1 + Z2 + Z0); fPu = 3 * Ia1; label = "Monofásica a tierra"; }
        else if (faultType === "2F") { Ia1 = Vf / (Z1 + Z2); fPu = Math.sqrt(3) * Ia1; label = "Bifásica"; }
        else { Ia1 = Vf / (Z1 + (Z2 * Z0) / (Z2 + Z0)); fPu = 3 * Math.abs(-(Ia1 * Z2) / (Z2 + Z0)); label = "Bifásica-Tierra"; }
        const Icc = fPu * Ibase / 1000, Scc = Math.sqrt(3) * Vbase * Icc;
        const steps = [
            { title: "1. RED DE SECUENCIA", formula: "Z_eq = Σ Z_i (Thevenin)", detail: `Falla en Barra ${faultBus + 1} | Vf = ${cx.fix(Vf, 3)} pu` },
            { title: "2. IMPEDANCIAS CALCULADAS", formula: "Z₁=Z+ | Z₂=Z- | Z₀=3Z+", calc: `Z₁=${cx.fix(Z1, 4)} pu\nZ₂=${cx.fix(Z2, 4)} pu\nZ₀=${cx.fix(Z0, 4)} pu`, detail: "Se asume red rígidamente aterrada" },
            { title: `3. FALLA ${label}`, formula: faultType === "3F" ? "If=Vf/Z₁" : "If=f(Z₁,Z₂,Z₀)", calc: `I_falla (pu) = ${cx.fix(fPu, 4)}`, detail: `Ibase=${cx.fix(Ibase, 1)} A` },
            { title: "4. VALORES FÍSICOS (kA)", formula: "Icc = I_pu × Ibase", calc: `Icc = ${cx.fix(Icc, 3)} kA\nScc = ${cx.fix(Scc, 2)} MVA`, detail: `Nivel de tensión: ${Vbase} kV` },
        ];
        return { steps, Icc: cx.fix(Icc, 3).toString(), Scc: cx.fix(Scc, 2).toString(), fPu: cx.fix(fPu, 4).toString() };
    } catch (e) { return { error: e.message, steps: [], Icc: "—", Scc: "—", fPu: "—" }; }
}

// ── MOTOR: ARMÓNICOS ─────────────────────────────────────────────
export function runHarmonics(fundV, ordersStr, magsStr) {
    try {
        const V1 = parseFloat(fundV) || 220;
        const orders = ordersStr.split(",").map(x => parseInt(x.trim())).filter(x => !isNaN(x) && x > 0);
        const mags = magsStr.split(",").map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
        let sumSq = 0;
        const sumSqN = sumSq || 0;
        const harmonics = orders.map((h, i) => { const Vh = mags[i] || 0; sumSq += Vh ** 2; return { h, Vh, pct: cx.fix((Vh / (V1 || 1)) * 100, 2), freq: h * 60 }; });
        const THD = cx.fix((Math.sqrt(sumSqN) / (V1 || 1) * 100), 2);
        const Vrms = cx.fix(Math.sqrt(V1 ** 2 + sumSqN), 3);
        const PF = cx.fix((0.92 / Math.sqrt(1 + (parseFloat(THD) / 100) ** 2)), 4);
        const KF = cx.fix((V1 > 0 ? harmonics.reduce((s, h) => s + h.h ** 2 * (h.Vh / V1) ** 2, 0) : 0), 3);
        const steps = [
            { title: "1. SERIES DE FOURIER", formula: "v(t)=V₁sin(ωt)+Σ Vₕsin(hωt)", detail: "f₁=60Hz | ω=376.99 rad/s" },
            ...harmonics.map(h => ({ title: `h=${h.h} → ${h.freq}Hz`, formula: `V${h.h}=${h.Vh}V | ${h.pct}% de V₁` })),
            { title: "2. THD-V (IEEE 519-2022)", formula: "THD=√(ΣVₕ²)/V₁×100", calc: `THD=${THD}%`, detail: `BT ≤8%: ${parseFloat(THD) <= 8 ? "✅" : "⚠️"} | MT ≤5%: ${parseFloat(THD) <= 5 ? "✅" : "⚠️"}` },
            { title: "3. Vrms TOTAL", formula: "Vrms=√(V₁²+ΣVₕ²)", calc: `Vrms=${Vrms}V` },
            { title: "4. FACTOR DE POTENCIA", formula: "FP=cos(φ)/√(1+THD²)", calc: `FP=${PF}` },
            { title: "5. FACTOR K", formula: "K=Σh²·(Ih/I₁)²", calc: `K=${KF} → TX debe ser K-${Math.ceil(parseFloat(KF))}` },
        ];
        return { steps, THD: THD.toString(), Vrms: Vrms.toString(), PF: PF.toString(), KF: KF.toString(), harmonics, V1 };
    } catch (e) { return { error: e.message, steps: [], THD: "—", Vrms: "—", PF: "—", KF: "—", harmonics: [], V1: 220 }; }
}

// ── MOTOR: ESTABILIDAD ───────────────────────────────────────────
export function runStability(H, Pm, Pe, delta0, tcl) {
    try {
        const f = 60, M = H / (Math.PI * f);
        const ratio = Math.min(Math.max(Pm / Pe, -0.9999), 0.9999);
        const d_eq = Math.asin(ratio) * 180 / Math.PI, d_max = 180 - d_eq;
        const d0r = delta0 * Math.PI / 180, tclN = parseFloat(tcl);
        const Accel = Pm * (tclN - d0r) - Pe * (Math.cos(d0r) - Math.cos(tclN));
        const Decel = Pe * (Math.cos(tclN) - Math.cos(d_max * Math.PI / 180)) - Pm * (d_max * Math.PI / 180 - tclN);
        const stable = Decel > Accel, margin = cx.fix(Decel - Accel, 4);
        const pts = []; let d = d0r, w = 0, t = 0;
        while (t <= 3.0 && Math.abs(d * 180 / Math.PI) < 360) {
            pts.push({ t: +(t || 0).toFixed(3), d: +((d * 180 / Math.PI) || 0).toFixed(3) });
            const Pa = Pm - (t < tclN * 3 ? 0 : Pe * Math.sin(d));
            w += (Pa / (M || 1)) * 0.001; d += w * 0.001; t += 0.001;
        }
        const steps = [
            { title: "1. SWING EQUATION", formula: "M·d²δ/dt²=Pm−Pe·sin(δ) | M=H/(π·f)", calc: `M=${cx.fix(M, 6)}s²/rad | Pm=${Pm}pu | Pe_max=${Pe}pu` },
            { title: "2. EQUILIBRIO", formula: "δ_eq=arcsin(Pm/Pe) | δ_max=180°−δ_eq", calc: `δ_eq=${cx.fix(d_eq, 2)}° | δ_max=${cx.fix(d_max, 2)}°` },
            { title: "3. CRITERIO DE ÁREAS", formula: "A_accel≤A_decel → ESTABLE", calc: `A_accel=${cx.fix(Accel, 4)} | A_decel=${cx.fix(Decel, 4)}\nMargen=${margin} pu·rad`, detail: stable ? "✅ SISTEMA ESTABLE" : "⚠️ SISTEMA INESTABLE" },
            { title: "4. SIMULACIÓN EULER dt=0.001s", formula: "ω(t+dt)=ω(t)+(Pa/M)·dt | δ(t+dt)=δ(t)+ω·dt", detail: `${pts.length} puntos calculados` },
        ];
        return { steps, d_eq: cx.fix(d_eq, 2).toString(), d_max: cx.fix(d_max, 2).toString(), stable, margin, pts: pts.filter((_, i) => i % 12 === 0), Accel: cx.fix(Accel, 4), Decel: cx.fix(Decel, 4) };
    } catch (e) { return { error: e.message, steps: [], d_eq: "—", d_max: "—", stable: false, margin: 0, pts: [] }; }
}

// ── MOTOR: N-1 ───────────────────────────────────────────────────
export function runN1(buses, lines, transformers, colors = {}) {
    try {
        const results = [];
        [...lines.map((l, i) => ({ ...l, idx: i, isTx: false })), ...transformers.map((t, i) => ({ ...t, idx: i, isTx: true }))].forEach(el => {
            const newLines = el.isTx ? lines : lines.filter((_, i) => i !== el.idx);
            const newTx = el.isTx ? transformers.filter((_, i) => i !== el.idx) : transformers;
            try {
                const r = runLF(buses, newLines, newTx);
                if (!r) { results.push({ el: `${el.isTx ? "TX" : "L"}${el.idx + 1} B${el.from + 1}→B${el.to + 1}`, converged: false, worstV: "—", overloads: 0, status: "ERROR", color: colors.fault || "#ef4444" }); return; }
                const worstV = r.V?.length ? Math.min(...r.V.map(v => v.mag)) : 1.0;
                const overloads = r.flows?.filter(f => f && f.loading > 1.0).length || 0;
                const status = !r.converged ? "NO CONVERGE" : worstV < 0.90 ? "V CRÍTICO" : overloads > 0 ? "SOBRECARGA" : worstV < 0.95 ? "V BAJO" : "✅ OK";
                results.push({ el: `${el.isTx ? "TX" : "L"}${el.idx + 1} B${el.from + 1}→B${el.to + 1}`, converged: r.converged, worstV: (worstV ?? 0).toFixed(4), overloads, status, color: status === "✅ OK" ? (colors.ok || "#10b981") : (status.includes("CRÍTICO") || !r.converged ? (colors.fault || "#ef4444") : (colors.warn || "#f59e0b")) });
            } catch { results.push({ el: `${el.isTx ? "TX" : "L"}${el.idx + 1}`, converged: false, worstV: "—", overloads: 0, status: "ERROR", color: colors.fault || "#ef4444" }); }
        });
        return { results };
    } catch (e) { return { results: [], error: e.message }; }
}

// ── MOTOR: DESPACHO ECONÓMICO ────────────────────────────────────
export function runED(generators, totalLoad) {
    try {
        const Pd = parseFloat(totalLoad) || 100;
        let lambda = generators.reduce((s, g) => s + g.b, 0) / generators.length;
        const itersED = [];
        for (let it = 0; it < 40; it++) {
            const Ps = generators.map(g => Math.min(g.Pmax, Math.max(g.Pmin, (lambda - g.b) / (2 * g.c))));
            const err = Ps.reduce((s, p) => s + p, 0) - Pd;
            itersED.push({ it: it + 1, lambda: lambda.toFixed(4), sumP: Ps.reduce((s, p) => s + p, 0).toFixed(2), err: err.toFixed(4) });
            if (Math.abs(err) < 0.01) break;
            lambda -= err / generators.reduce((s, g) => s + 1 / (2 * g.c), 0);
        }
        const finalP = generators.map(g => Math.min(g.Pmax, Math.max(g.Pmin, (lambda - g.b) / (2 * g.c))));
        const totalCost = generators.reduce((s, g, i) => s + g.a + g.b * finalP[i] + g.c * finalP[i] ** 2, 0);
        const steps = [
            { title: "1. COSTO INCREMENTAL", formula: "IC_i(P)=b_i+2c_i·P_i=λ (mismo para todos)", detail: `Pd=${Pd}MW` },
            { title: "2. INTERACIÓN λ", formula: "λ(k+1)=λ(k)−ΔP/Σ(1/2c_i)", type: "itersED", data: (itersED || []).slice(0, 8) },
            { title: "3. DESPACHO ÓPTIMO", formula: "P_i*=(λ−b_i)/2c_i", type: "dispatch", data: generators.map((g, i) => ({ name: g.name, P: cx.fix(finalP[i], 2).toString(), Pmin: g.Pmin, Pmax: g.Pmax, cost: cx.fix((g.a + g.b * (finalP[i] || 0) + g.c * (finalP[i] || 0) ** 2), 2).toString() })), lambda: cx.fix(lambda, 4).toString(), totalCost: cx.fix(totalCost, 2).toString() },
        ];
        return { steps, dispatch: finalP, lambda: cx.fix(lambda, 4).toString(), totalCost: cx.fix(totalCost, 2).toString() };
    } catch (e) { return { error: e.message, steps: [], lambda: "—", totalCost: "—" }; }
}

// ── MOTOR: CURVA DE CARGA 24H ────────────────────────────────────
export function runLoadProfile(buses, lines, transformers, loadProfile) {
    try {
        const baseLoad = buses.reduce((s, b) => s + (b.Pload || 0), 0);
        const results = loadProfile.map((factor, h) => {
            const sb = buses.map(b => ({ ...b, Psch: (b.Psch || 0) * factor, Qsch: (b.Qsch || 0) * factor }));
            const r = runLF(sb, lines, transformers);
            const Vmin = r && r.V.length ? Math.min(...r.V.map(v => v.mag)).toFixed(4) : "—";
            return { h, factor, load: +(baseLoad * factor).toFixed(1), Vmin, loss: (r && r.totalLoss) ? parseFloat(r.totalLoss) : 0, converged: r ? r.converged : false };
        });
        const peakH = results.reduce((a, b) => b.factor > a.factor ? b : a, results[0]);
        const valleyH = results.reduce((a, b) => b.factor < a.factor ? b : a, results[0]);
        const avgLoad = cx.fix((results.reduce((s, r) => s + r.load, 0) / 24), 1);
        const loadFactor = cx.fix((peakH.load > 0 ? (parseFloat(avgLoad) / peakH.load) : 0), 3);
        return { results, peakH, valleyH, avgLoad: avgLoad.toString(), loadFactor: loadFactor.toString() };
    } catch (e) { return { error: e.message, results: [], peakH: { load: 0, h: 0 }, valleyH: { load: 0, h: 0 }, avgLoad: "—", loadFactor: "—" }; }
}

// ── MOTOR: PROTECCIONES ──────────────────────────────────────────
export function runProtections(relays, scResult) {
    try {
        const steps = [{ title: "1. RELÉS ANSI 51/50 — IEC Estándar Inverso", formula: "t=TDS×0.14/(M^0.02−1)", detail: "M=Ifalla/Ipickup" }];
        const curves = relays.map(r => {
            const Icc = scResult ? parseFloat(scResult.Icc) * 1000 : 2000;
            const M = Icc / r.Ipickup;
            const t_op = M > 1.001 ? r.TDS * (0.14 / (Math.pow(M, 0.02) - 1)) : 999;
            const actInst = r.Iinst > 0 && Icc > r.Iinst;
            steps.push({ title: `Relé ${r.name}`, formula: "t=TDS×0.14/(M^0.02−1)", calc: `M=${cx.fix(M, 2)} | t=${cx.fix(t_op, 3)}s${actInst ? " | ANSI50: ✅" : ""}` });
            return { ...r, M: cx.fix(M, 2).toString(), t_op: t_op < 999 ? cx.fix(t_op, 3).toString() : "∞", actInst, pts: Array.from({ length: 18 }, (_, i) => { const m = 1.5 + i * 0.6; return { M: m, t: cx.fix(r.TDS * (0.14 / (Math.pow(m, 0.02) - 1)), 3) }; }) };
        });
        return { steps, curves };
    } catch (e) { return { error: e.message, steps: [], curves: [] }; }
}
