# Phase 2 Summary: The Universal Physics Engine

## 1. Overview
In Phase 2, we built the "Digital Universe" where our AI will eventually live. The goal was to create a simulation that is **physically accurate**, **universal** (works for any 3-body system), and **extremely fast** (>10k steps/second) to support Deep Reinforcement Learning.

## 2. Component Breakdown

### A. The Core Math (`dynamics.py`)
This is the "Textbook" implementation.
- **Purpose:** Acts as the "Ground Truth" to verify accuracy.
- **Tech:** Uses Python's standard `scipy.integrate.solve_ivp`.
- **How it works:** It implements the **Circular Restricted Three-Body Problem (CR3BP)** equations.
    - It calculates forces from two massive bodies (like Earth & Moon).
    - It adds "Centrifugal Force" and "Coriolis Force" because we are in a **Rotating Reference Frame**.
    - *Note:* In this frame, Earth and Moon stay still, and the satellite moves around them. This makes the math easier for station-keeping.

### B. The Speed Demon (`fast_dynamics.py`)
This is the "Game Engine" implementation.
- **Purpose:** Performance. Standard Python is too slow for training Neural Networks (which need millions of trials).
- **Tech:** Uses **Numba (Just-In-Time Compiler)**.
- **How it works:** 
    - It takes the Python functions and compiles them into **Optimized Machine Code** (C/C++ speed) on the fly.
    - It uses a custom **Runge-Kutta 4 (RK4)** integrator manually written for speed, avoiding the overhead of `scipy`.
    - **Result:** ~1.7 Million simulation steps per second (vs ~500 in standard Python).

### C. The Verification Suite (`test_physics.py`)
- **Purpose:** Physics validation.
- **Concept:** **Jacobi Constant (Energy)**.
    - In this specific physics system, "Energy" (Kinetic + Potential - Rotational components) *must* be conserved.
    - If the satellite drifts in energy, the simulation is broken.
- **Result:** Our engine conserves energy to a precision of $10^{-11}$, which is excellent for long-term simulations.

### D. The Solver (`halo_solver.py`)
- **Purpose:** To find specific "Halo Orbits" (stable-ish paths).
- **Method:** **Shooting Method**.
    - It guesses a velocity $V_y$.
    - It simulates the path to see if it crosses the axis perpendicularly.
    - It adjusts $V_y$ (using deviations) and tries again until a loop is closed.

### E. The Viz (`interactive_system.py`)
- **Purpose:** Interactive sandbox to visualize the math.
- **Tech:** `matplotlib` (standard plotting).
- **Limitation:** Can be "janky" or slow because Matplotlib is not a real-time graphics engine.

---

## 3. Deep Dive: The Physics Engine Mechanics

### The Coordinate System (Rotating Frame)
Imagine you are standing on a merry-go-round (The Earth-Moon system).
- The center is the **Barycenter** (center of mass).
- **Earth** is fixed at $x = -\mu$.
- **Moon** is fixed at $x = 1 - \mu$.
- Because you are spinning, you feel two "fictitious" forces:
    1.  **Centrifugal Force:** Pushes you away from the center (like being thrown off the merry-go-round).
    2.  **Coriolis Force:** Pushes you sideways if you try to walk (velocity-dependent).

### The Equations of Motion
The engine calculates acceleration $\ddot{x}, \ddot{y}, \ddot{z}$ at every timestep $dt$:

$$
\ddot{x} = 2\dot{y} + x - \frac{(1-\mu)(x+\mu)}{r_1^3} - \frac{\mu(x-(1-\mu))}{r_2^3}
$$

- $2\dot{y}$ is the **Coriolis** term (stabilizes orbits!).
- $x$ is the **Centrifugal** term.
- The fractions are the **Gravity** from Earth ($r_1$) and Moon ($r_2$).

### Integration (RK4)
We don't just add `velocity * time`. We use **Runge-Kutta 4**:
1.  Look at the slope (force) at the start.
2.  Estimate the slope halfway through.
3.  Estimate it again.
4.  Estimate it at the end.
5.  Take a weighted average.
*This allows us to take larger time steps without losing accuracy.*
