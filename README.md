
# Lagrange-Lock: Autonomous Station-Keeping AI

Lagrange-Lock is a project to train a Reinforcement Learning (RL) agent to control a satellite in the chaotic environment of the Circular Restricted Three-Body Problem (CR3BP), specifically around the Lagrange Point (L1).

## Project Structure

The project is divided into distinct execution phases:

### Phase 1: Mathematical Foundation (Complete)
*   Implemented the CR3BP Equations of Motion in Python.
*   Verified the existence of Lagrange Points (L1, L2, etc.).
*   Developed a "Shooting Method" solver to find specific Halo Orbits.

### Phase 2: Visual Verification (Complete)
*   **Goal:** Create a "Digital Twin" to verify physics before AI training.
*   **Outcome:** A standalone **Realtime WebGL Viewer**.
*   **Key File:** `phase_2/realtime_viewer.html`
*   **Capabilities:**
    *   Runs full RK4 physics integration in the browser at 60 FPS.
    *   Visualizes Earth-Moon, Sun-Jupiter, and Binary Star systems.
    *   Interactive controls to fly the satellite and test stability.
    *   Realtime crash detection.

### Phase 3: The AI Brain (In Progress)
*   **Goal:** Train a PPO Agent using Gymnasium and Stable-Baselines3.
*   **Current Task:** Wrapping the Python physics core into a custom `Gymnasium` environment.

---

## How to Run Phase 2 (Viewer)

1.  Navigate to `phase_2/`.
2.  Open **`realtime_viewer.html`** in any modern web browser.
3.  No Python server required.

## How to Run Phase 3 (Training)
*(Coming Soon)*
