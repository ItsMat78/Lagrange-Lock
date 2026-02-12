
# Lagrange-Lock: Project Walkthrough

## 1. Project Overview
**Objective**: Maintain a satellite in a stable Halo orbit around the Earth-Moon L1 Lagrange point using Reinforcement Learning (RL).
**Challenge**: The L1 point is an unstable equilibrium in the Circular Restricted Three-Body Problem (CR3BP). Without active control, any spacecraft will drift away exponentially.
**Solution**: An AI agent (PPO) learns to apply minimal thrust to keep the satellite in a specific "Halo" orbit while minimizing fuel consumption.

---

## 2. Phase 1: Core Physics & Dynamics
**Goal**: Establish the mathematical foundation.
*   **CR3BP Model**: Implemented the Equations of Motion for the Circular Restricted Three-Body Problem.
    *   **Primary Bodies**: Earth (M1) and Moon (M2).
    *   **Frame**: Rotating reference frame where Earth and Moon appear fixed.
*   **Lagrange Points**: Calculated the 5 equilibrium points (L1-L5).
    *   **Focus**: L1 (between Earth and Moon), ideal for observation but unstable.
*   **Integration**: Used Runge-Kutta 4 (RK4) for high-precision physics propagation.

---

## 3. Phase 2: Simulation & Visualization
**Goal**: See the physics in action.
*   **Web Viewer (`realtime_viewer.html`)**:
    *   Built with **Three.js** for 3D rendering.
    *   Runs the full CR3BP physics engine in JavaScript (client-side).
    *   **Features**:
        *   Interactive camera controls (WASD/Mouse).
        *   Real-time parameter tuning (Gravity ratio $\mu$).
        *   Visualizes Lagrange points, Earth, Moon, and Trajectory trails.
        *   **New**: Ability to load and replay JSON trajectories.
*   **ONNX Inference**: Integrated `onnxruntime-web` to run Python-trained AI models directly in the browser via WebAssembly.

---

## 4. Phase 3: AI Training (Reinforcement Learning)
**Goal**: Teach the satellite to fly itself.
*   **Environment (`satellite_env.py`)**:
    *   **State**: Position $(x, y, z)$, Velocity $(v_x, v_y, v_z)$, and Fuel.
    *   **Action**: Continuous Thrust vector $(F_x, F_y, F_z)$.
    *   **Reward Function**:
        *   **+1.0**: Being in the "Sweet Spot" (Halo Orbit Shell).
        *   **-0.5**: Fuel usage (encourages efficiency).
        *   **-2.0**: Drifting away from L1 (Penalty).
        *   **-50.0**: Crashing or escaping.
*   **Algorithm**: Proximal Policy Optimization (PPO) from `stable-baselines3`.
*   **Performance**:
    *   Accelerated physics using **Numba (JIT)** to achieve >10,000 steps/second.
    *   Trained for millions of steps to learn delicate station-keeping maneuvers.
*   **Deployment**:
    *   Exported trained PyTorch model to **ONNX**.
    *   Loaded into the Web Viewer for real-time demonstration.

---

## 5. Current Status & Demo
*   **Simulation**: Accurate CR3BP physics running in real-time.
*   **AI**: The agent successfully captures into a near-Halo orbit.
*   **Tooling**: Complete pipeline from Python training -> ONNX export -> Web Visualization.
*   **Verification**: Comparison plots confirm Python and JS environments match physics behavior.

## 6. How to Run the Demo
1.  Open `phase_2/realtime_viewer.html` in a local server.
2.  **Manual Control**: Use controls to push the satellite and watch it drift.
3.  **AI Control**: Click "ENABLE AI AGENT" to watch the neural network take over and stabilize the orbit.
4.  **Replay**: Upload a `trajectory_data.json` to analyze specific past runs.
