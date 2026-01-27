# 🛰️ Lagrange-Lock
### Autonomous Station-Keeping in Chaotic 3-Body Systems

**Universal. Blind. Robust.**

Lagrange-Lock is a Deep Reinforcement Learning (RL) agent capable of maintaining a satellite's position at unstable Lagrange Points (L1, L2, L3) using only noisy, local sensor data. Unlike traditional controllers that rely on perfect Earth-tracking, this agent is designed to be **truly autonomous**.

---

## 🌌 The Mission
Maintaining a Halo Orbit around a Lagrange point is like balancing a pencil on its tip—forever.
- **The Challenge:** Gravity at these points is unstable. A 1mm error grows into a 100km drift exponentially.
- **The Solution:** An RL "Brain" trained to survive in a chaotic environment, fighting gravitational perturbations and sensor noise simultaneously.
- **The Twist:** We use **Normalized Physics**, meaning the same neural network can pilot a ship in the Earth-Moon system ($\mu \approx 0.012$) OR a Binary Star system ($\mu = 0.5$) without retraining.

## 🛠️ Tech Stack
- **Simulation:** Python, SciPy (RK45 Integrator)
- **Acceleration:** JAX / Numba (For >10,000 steps/sec)
- **AI Core:** Gymnasium, Stable Baselines3 (PPO Algorithm)
- **Math:** Normalized Circular Restricted 3-Body Problem (CR3BP)

## 🗺️ Roadmap
- [x] **Phase 1: Foundations** - Universal Physics & Lagrange Point Theory.
- [ ] **Phase 2: Physics Engine** - High-speed orbital propagator.
- [ ] **Phase 3: The Environment** - "Blind Pilot" Gymnasium wrapper.
- [ ] **Phase 4: Training** - PPO Agent vs. Chaos.
- [ ] **Phase 5: Realism** - N-Body Gravity, Thruster Failures, & Inertial verification.

## 🚀 Quick Start
*(Coming Soon)*

```bash
# Clone the repo
git clone https://github.com/YourUsername/Lagrange-Lock.git

# Install dependencies
pip install -r requirements.txt

# Calculate L-Points for Earth-Moon
python phase_1/find_lagrange_points.py
```

---
*Built for the future of deep-space autonomy.*
