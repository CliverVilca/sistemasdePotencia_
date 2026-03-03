# ⚡ Power Analyzer PRO v3.2

**Power Analyzer PRO** is a professional-grade power systems simulation and analysis suite built with React. It provides engineers with a comprehensive toolset for analyzing electrical networks based on international standards (IEEE, IEC, ANSI).

![Architecture](https://img.shields.io/badge/Architecture-Modular-blue)
![React](https://img.shields.io/badge/React-18-blue)
![Vite](https://img.shields.io/badge/Vite-Fast-blue)

## 🚀 Key Features

*   **Newton-Raphson Solver**: High-precision power flow analysis with detailed iteration logs.
*   **Short Circuit Engine**: Fault calculation according to IEC 60909 (3-phase, 1-phase-to-ground, etc.).
*   **Harmonic Analysis**: THD-V calculation and spectrum visualization (IEEE 519-2022).
*   **Transient Stability**: Swing equation simulation with dynamic charts.
*   **Economic Dispatch**: Optimization of generation costs using incremental cost theory.
*   **Protection Coordination**: ANSI 51/50 relay curves and TCC plotting.
*   **Automatic Pipeline**: "One-Click Engineering" to execute multiple analysis sequences in parallel.
*   **Blueprint SLD**: Interactive Single Line Diagram with real-time animations and drag-and-drop.

## 📁 Project Structure

The project follows a modern, decoupled architecture:

```text
src/
├── components/      # UI Components (SLD, Inspector, UI Primitives)
│   └── tabs/        # Module-specific Tabs (Harmonics, Stability, etc.)
├── engine/          # Electrical Engineering Engines (Solvers, Math/Complex)
├── constants/       # Global Config (Themes, Topologies, Libraries)
├── App.jsx          # Main App Orchestrator
└── main.jsx         # Entry Point
```

## 🛠️ Tech Stack

*   **Frontend**: React (Hooks, functional components)
*   **Math**: Custom Complex Number arithmetic library.
*   **Viz**: High-performance SVG-based charts and SLD.
*   **Export**: jsPDF & html2canvas for technical report generation.
*   **Styles**: Theme-driven dynamic CSS (Pro Silver & Pro Midnight).

## 📥 Getting Started

1.  Clone the repository.
2.  Install dependencies: `npm install`
3.  Run in development mode: `npm run dev`
4.  Build for production: `npm run build`

## 📖 Standards Supported

*   **ANSI C84.1**: Voltage tolerance limits.
*   **IEEE 519-2022**: Harmonic distortion levels.
*   **IEC 60909**: Short circuit calculation methodology.

---
*Developed for professional power systems analysis.*
