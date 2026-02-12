# Lagrange-Lock: Taming the Three-Body Problem with AI

**Lagrange-Lock** is a research project dedicated to solving the station-keeping problem for satellites at Lagrange Points (specifically Earth-Moon L1) using Deep Reinforcement Learning. Unlike traditional control theory which requires precise mathematical linearization, our "Blind Pilot" AI (PPO) learns to surf the chaotic gravitational manifolds of the Circular Restricted Three-Body Problem (CR3BP).

---

## 📅 Project Roadmap & Progress

The project is structured into evolutionary phases, moving from mathematical theory to a full-stack AI simulation.

### ✅ Phase 1: Mathematical Foundations (Completed)
*   **Goal**: Validate the physics of the Three-Body Problem.
*   **Achievements**:
    *   Implemented the **CR3BP Equations of Motion** in Python.
    *   Derived the location of L1 through numerical root-finding (Newton-Raphson).
    *   Validated "Jacobi Constant" (Energy) conservation to ensure physics accuracy.

### ✅ Phase 2: The 3D Physics Engine (Completed)
*   **Goal**: Build a fast, visualized simulation environment.
*   **Achievements**:
    *   Expanded math to **3D space** ($z$-axis dynamics).
    *   Built a **Custom RK4 Integrator** in Python for trajectory propagation.
    *   Developed the first **Three.js Web Viewer** to visualize ballistic (non-controlled) particle paths in the browser.

### 🌟 Phase 3: The AI Pilot (Current Status: ~90% Complete)
*   **Goal**: Train an AI to autonomously maintain a Halo Orbit.
*   **Achievements**:
    *   **High-Performance Backend**: Ported physics to `Numba` JIT (~10,000 steps/sec).
    *   **Gymnasium Environment**: Created `SatelliteEnv` with a complex Reward Function (Stability + Fuel Efficiency).
    *   **PPO Integration**: Successfully integrated **Stable-Baselines3** to train the agent.
    *   **Interactive Control**: Upgraded the Web Viewer to communicate with the Python backend (`server.py`), allowing users to "Request AI Trajectories" on demand.
    *   **Result**: The AI successfully discovers and maintains Halo orbits for 5000+ timesteps.

### 🔮 Phase 4: Robustness & Realism (Future Work)
*   **Goal**: Prepare the Orbit-Keeping Agent for real-world uncertainties.
*   **Pending**:
    *   **Noisy Sensors**: Introduce Gaussian noise to position/velocity inputs to test the "Blind Pilot" theory.
    *   **Thruster Failures**: Disable 1-2 thrusters during simulation to force the AI to compensate.
    *   **Transfer Orbits**: Train a separate agent to *travel* to L1 from Earth GTO, rather than just spawning there.

---

## 🚀 Quick Start (Phase 3)

### Prerequisites
*   Python 3.8+
*   `pip install -r requirements.txt`

### Running the Simulation
1.  **Start the Server**:
    ```bash
    python phase_3/server.py
    ```
2.  **Access the Interface**:
    *   Open **[http://localhost:8081/realtime_viewer.html](http://localhost:8081/realtime_viewer.html)** in your browser.
3.  **Deploy AI**:
    *   Go to the **AI Control** panel on the left.
    *   Select a model (e.g., `ppo_sat_v4_final.zip`).
    *   Click **RUN AI**.

---

## 📂 Repository Structure

```
Lagrange-Lock/
│
├── phase_3/                  # 🌟 MAIN ACTIVE DIRECTORY
│   ├── server.py             # API Host & AI Inference Engine
│   ├── satellite_env.py      # Physics & Reward Logic (GymEnv)
│   ├── fast_dynamics.py      # Numba-Accelerated Math Core
│   ├── train_phase_3.py      # Training Script (PPO)
│   ├── realtime_viewer.html  # WebGL Frontend
│   └── models/               # Trained Agent Weights
│
├── phase_2/                  # Legacy 3D particles (No AI)
├── phase_1/                  # Legacy 2D Math Scripts
└── README.md                 # This file
```

---

## 👨‍💻 Credits
**Project Team**: Shreyash Rai, Sameer Choudhary
**Supervisor**: Dr. Avantika Singh (IIIT Naya Raipur)
**Date**: February 2026
