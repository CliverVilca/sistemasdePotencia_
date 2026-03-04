# ⚡ POWER ANALYZER PRO v10.0 | Arquitecura Enterprise

Este sistema ha sido reconstruido bajo una arquitectura de **Framework Profesional** modular.

## 🏗️ Estructura del Framework

```text
/
├── main.py              # Punto de entrada (Bootloader)
└── app/
    ├── core/            # Motores de Cálculo (Engine)
    │   └── engine.py    # Algoritmos NR e IEC
    ├── graphics/        # Motor Gráfico (Canvas CAD)
    │   ├── items.py     # Equipos Inteligentes
    │   └── scene.py     # Escena de Ingeniería
    └── ui/              # Interfaz de Usuario (HMI)
        ├── main_window.py
        └── widgets.py   # Componentes Atómicos
```

## 🚀 Características Avanzadas
- **Escalabilidad**: Es fácil añadir nuevos módulos de cálculo o tipos de equipos.
- **Desacoplamiento**: La interfaz no depende del motor de cálculo, permitiendo cálculos pesados en segundo plano.
- **Gráficos Vectoriales**: Dibujo de alta precisión con rejilla de ingeniería automática.
```
