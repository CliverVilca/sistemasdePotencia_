export const TOPOS = {
    s3: {
        name: "3 Barras", buses: [
            { id: 0, name: "B1", type: "slack", x: 500, y: 150, Vmag: 1.05, Vang: 0, Vbase: 13.8, Psch: 0, Qsch: 0, Pload: 0, Pgen: 150 },
            { id: 1, name: "B2", type: "PV", x: 300, y: 450, Vmag: 1.02, Vang: 0, Vbase: 13.8, Psch: 100, Qsch: 0, Pload: 0, Pgen: 100 },
            { id: 2, name: "B3", type: "PQ", x: 700, y: 450, Vmag: 1.0, Vang: 0, Vbase: 13.8, Psch: -80, Qsch: -30, Pload: 80 },
        ], lines: [{ id: 0, from: 0, to: 1, R: 0.02, X: 0.08 }, { id: 1, from: 0, to: 2, R: 0.025, X: 0.10 }, { id: 2, from: 1, to: 2, R: 0.03, X: 0.12 }], transformers: []
    },
    s5: {
        name: "IEEE 5 Barras", buses: [
            { id: 0, name: "B1", type: "slack", x: 500, y: 100, Vmag: 1.06, Vang: 0, Vbase: 230, Psch: 0, Qsch: 0, Pload: 0 },
            { id: 1, name: "B2", type: "PV", x: 250, y: 300, Vmag: 1.00, Vang: 0, Vbase: 230, Psch: 40, Qsch: 0, Pload: 0, Pgen: 40 },
            { id: 2, name: "B3", type: "PQ", x: 750, y: 300, Vmag: 1.0, Vang: 0, Vbase: 230, Psch: -25, Qsch: -15, Pload: 25 },
            { id: 3, name: "B4", type: "PQ", x: 300, y: 550, Vmag: 1.0, Vang: 0, Vbase: 230, Psch: -40, Qsch: -5, Pload: 40 },
            { id: 4, name: "B5", type: "PQ", x: 700, y: 550, Vmag: 1.0, Vang: 0, Vbase: 230, Psch: -50, Qsch: -15, Pload: 50 },
        ], lines: [
            { id: 0, from: 0, to: 1, R: 0.02, X: 0.06 }, { id: 1, from: 0, to: 2, R: 0.08, X: 0.24 },
            { id: 2, from: 1, to: 2, R: 0.06, X: 0.18 }, { id: 3, from: 1, to: 3, R: 0.06, X: 0.18 },
            { id: 4, from: 2, to: 4, R: 0.04, X: 0.12 }, { id: 5, from: 3, to: 4, R: 0.01, X: 0.03 },
        ], transformers: []
    },
};

export const LOAD_PROFILE = [0.55, 0.50, 0.48, 0.46, 0.47, 0.52, 0.65, 0.80, 0.90, 0.95, 0.97, 0.98, 0.95, 0.93, 0.95, 0.97, 1.00, 0.99, 0.95, 0.88, 0.82, 0.75, 0.68, 0.60];
