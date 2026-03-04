# 🏛️ Architecture Overview - Power Analyzer PRO

This document outlines the professional modular architecture of the project.

## 🧱 The Decomposition Strategy

The original monolithic application (`power_pro_v2.jsx`) was decomposed into functional silos to improve maintainability and scalability. 

### ⚙️ 1. The Engineering Engine (`src/engine/`)

The core mathematical logic is now completely separated from the UI.
*   **`complex.js`**: A custom library for complex number arithmetic (`add`, `sub`, `mul`, `conj`, `pol`, `abs`). 
*   **`solvers.js`**: Stateless technical engines (`runLF`, `runSC`, `runStability`, etc.). They take raw state (buses, lines) and return analysis results.

### 🎨 2. The Design System (`src/constants/`)

Styling, data, and libraries are centralized for easier global updates.
*   **`themes.js`**: Defines `proSilver` and `proMidnight` tokens. 
*   **`topologies.js`**: Preconfigured network models (IEEE 5-Bus, 3-Bus Demo).
*   **`libraries.js`**: Equipment databases (Cables, Transformers).

### 🧩 3. The Component Hierarchy (`src/components/`)

Visual elements are broken down into granular, reusable pieces.
*   **`UI.jsx`**: Core primitives (`Btn`, `Inp`, `Sel`, `KPI`).
*   **`Charts.jsx`**: Data visualization (TCC, Swing, Spectrum, Load Curves).
*   **`SLD.jsx`**: The Single Line Diagram (blueprint-style logic).
*   **`Inspector.jsx`**: Variable parameter explorer and results viewer.

#### 🗂️ 4. The Tab Fragments (`src/components/tabs/`)

Each technical module (Harmonics, Stability, ED, etc.) has its own file. This keeps `App.jsx` ultra-light.

## 🔀 5. The Orchestrator (`src/App.jsx`)

The main App component now only handles:
1.  **Global Simulation State**.
2.  **Tab Routing**.
3.  **Cross-tab shared logic** (like updating the network topology).
4.  **PDF Generation**.

## 📊 Benefits of the New Structure

1.  **Readability**: No more 1500-line files.
2.  **Scalability**: Adding a new analysis (e.g. Monte Carlo) only requires a new solver and a new tab component.
3.  **Testability**: Engines can be unit-tested without rendering any React components.
4.  **Performance**: Smaller files lead to faster HMR (Hot Module Replacement) during development.

---
*Architected for engineering excellence.*
