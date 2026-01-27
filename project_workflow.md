# Project Roadmap: Autonomous Station-Keeping in Chaotic 3-Body Systems

**Objective:** Develop a Deep Reinforcement Learning (RL) agent capable of autonomous station-keeping at Lagrange points. The system must be "universal" (applicable to any 3-body system) and "blind" (relying on onboard noisy sensors rather than external Earth tracking).

**Tech Stack:** Python, SciPy, JAX/Numba, Gymnasium, Stable Baselines3, Poliastro, Plotly.

---

## Phase 1: Theoretical Foundations (Universal Physics)
**Goal:** Understand the math that makes this applicable to "intergalactic" systems and the basics of RL.

- [x] **1.1 Master the Normalized CR3BP**
    - Study the *Circular Restricted Three-Body Problem*.
    - **Crucial for Intergalactic Scope:** Learn how to write equations using the mass parameter $\mu$ (mu) and non-dimensional units.
    - *Why?* If you solve for $\mu$, your code works for the Earth-Moon system ($\mu \approx 0.012$) AND a binary star system ($\mu = 0.5$) without changing the code.
- [x] **1.2 Lagrange Point Theory**
    - Calculate the location of L1, L2, and L3 based purely on $\mu$.
    - Understand the "Saddle Point" instability (stable in some directions, unstable in others).
- [x] **1.3 RL Concepts for Control**
    - Learn: Agent, Environment, State, Action, Reward.
    - Concept: **Partially Observable Markov Decision Process (POMDP)**. This is the formal term for "the satellite doesn't know exactly where it is."

---

## Phase 2: The Universal Physics Engine
**Goal:** Build a high-speed simulator that calculates "True Physics" but is generic enough for any star system.

- [ ] **2.1 The Core Integrator (SciPy)**
    - Implement the CR3BP Equations of Motion in Python.
    - Use `scipy.integrate.solve_ivp` with **RK45** for high precision.
- [ ] **2.2 JIT Acceleration (JAX / Numba)**
    - Wrap the differential equations with JAX or Numba decorators.
    - **Goal:** Achieve >10,000 steps per second. RL requires millions of trials; standard Python is too slow.
- [ ] **2.3 Verification**
    - Simulate a "Halo Orbit" (a specific periodic orbit).
    - Ensure energy (Jacobi Constant) remains conserved in the simulation (a physics check).

---

## Phase 3: The "Blind Pilot" Environment (Gymnasium)
**Goal:** Create the interface where the AI lives. This is where we implement the "Autonomous/Noisy" constraint.

- [ ] **3.1 Custom Gymnasium Class**
    - Create `class SatelliteEnv(gym.Env):`
- [ ] **3.2 The "Intergalactic" Observation Space**
    - **The Twist:** Do *not* feed the agent the exact $(x, y, z)$ coordinates from the simulator.
    - **The Solution:** Create a "Sensor Model" function.
        - `observation = true_state + random_gaussian_noise(sigma)`
    - The agent receives this noisy data. This forces it to learn an internal Kalman Filter (estimation logic) implicitly.
- [ ] **3.3 The Action Space**
    - **Initial Strategy:** Continuous control `Box(low=-1, high=1, shape=(3,))` representing Thrust vector $(F_x, F_y, F_z)$.
    - **Note:** This mimics a "Guidance" system. The "Control Allocation" to specific thrusters is assumed perfect for now.
- [ ] **3.4 Domain Randomization (The "Universal" Key)**
    - Randomize mass parameter $\mu$ slightly.
    - Randomize "Gravity Noise" (simulating 4th body pull).

---

## Phase 4: Training the Autonomous Agent
**Goal:** Train the Neural Network to pilot the ship.

- [ ] **4.1 Setup Stable Baselines3 (SB3)**
    - Initialize PPO (Proximal Policy Optimization).
- [ ] **4.2 Reward Function Design**
    - **Survival:** +1 per step.
    - **Efficiency:** -0.1 * |Action| (Minimize Fuel).
    - **Station Keeping:** -1 * Distance from Target.
- [ ] **4.3 The Training Loop**
    - Train for 1M - 5M timesteps.
    - Monitor "Mean Episode Length" (Survival Time).

---

## Phase 5: Advanced Testing & "Realism" Upgrades
**Goal:** Prove the satellite works in the "Real World" (Inertial Frame, Broken Thrusters, Extra Planets).

- [ ] **5.1 The "Inertial Frame" Verification**
    - Convert the trajectory back to the Inertial Frame (Non-Rotating).
    - Prove that the satellite is actually orbiting Earth/Moon (and not just chasing a ghost).
- [ ] **5.2 The "N-Body" Perturbation Test**
    - Introduce a "Phantom Force" representing the Sun or Jupiter.
    - Verify that the AI (trained on noise) naturally fights this drift.
- [ ] **5.3 The "Thruster Failure" Scenario (The "Engineer" Update)**
    - **Upgrade:** Change Action Space to `MultiBinary(6)` (Individual Thrusters).
    - **Test:** Disable one thruster during the simulation.
    - **Goal:** See if the AI learns to "spin and thrust" to compensate for the dead engine.
- [ ] **5.4 Visualization**
    - 3D Plotly graph showing the "Halo Orbit" limit cycle.
    - Generate a video/GIF of the satellite maintaining orbit.

---

## Phase 6: Final Deliverables
- [ ] **Code:** GitHub repo with `requirements.txt` and clean structure.
- [ ] **Paper/Report:** Compare "Perfect Sensors" vs "Noisy Sensors" performance.
- [ ] **Demo:** A video showing the satellite correcting a drift automatically.