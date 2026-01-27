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
- [ ] **1.2 Lagrange Point Theory**
    - Calculate the location of L1, L2, and L3 based purely on $\mu$.
    - Understand the "Saddle Point" instability (stable in some directions, unstable in others).
- [ ] **1.3 RL Concepts for Control**
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
    - Continuous control: `Box(low=-1, high=1, shape=(3,))` representing Thrust vector $(T_x, T_y, T_z)$.
- [ ] **3.4 Domain Randomization (Optional but Recommended)**
    - To make it truly "Intergalactic," randomize the mass parameter $\mu$ slightly at the start of every episode.
    - This trains the AI to adapt to different gravitational environments instantly.

---

## Phase 4: Training the Autonomous Agent
**Goal:** Train the Neural Network to pilot the ship.

- [ ] **4.1 Setup Stable Baselines3 (SB3)**
    - Initialize the PPO (Proximal Policy Optimization) algorithm.
- [ ] **4.2 Reward Function Design (The "Teacher")**
    - **Survival Reward:** +1 for every second it stays near the L-point.
    - **Fuel Penalty:** -0.1 * |Thrust| (Encourage drifting/surfing over burning fuel).
    - **Distance Penalty:** -1 * Distance from Target.
- [ ] **4.3 The Training Loop**
    - Train for 1M - 5M timesteps.
    - Watch the "Mean Reward" graph. It should go up. If it stays flat, the task is too hard (reduce noise) or the reward is confusing.

---

## Phase 5: Testing & Analysis
**Goal:** Prove the satellite works without Earth.

- [ ] **5.1 Robustness Test**
    - Run the trained model in a simulation with *higher* sensor noise than it was trained on.
    - If it survives, it is truly autonomous.
- [ ] **5.2 "Alien System" Test**
    - Change the mass parameter $\mu$ to represent a different planetary system (e.g., Sun-Jupiter).
    - See if the agent can still stabilize itself.
- [ ] **5.3 Visualization (Plotly/Poliastro)**
    - 3D Plot: Show the "True Path" (smooth) vs. the "Perceived Path" (noisy) vs. the L-point.
    - Generate a video/GIF of the satellite maintaining orbit.

---

## Phase 6: Final Deliverables
- [ ] **Code:** GitHub repo with `requirements.txt` and clean structure.
- [ ] **Paper/Report:** Compare "Perfect Sensors" vs "Noisy Sensors" performance.
- [ ] **Demo:** A video showing the satellite correcting a drift automatically.