# Phase 3 FAQ: AI & Physics Mechanics

## 🧠 Why PPO? (Critical Design Decisions)

### **Q: Why Proximal Policy Optimization (PPO) and not DQN?**
**A:** The choice of PPO is fundamental to the project's success for three reasons:
1.  **Continuous Action Space**: Satellite thrusters require smooth, continuous values (e.g., 23.5% thrust). **DQN** only handles discrete actions (On/Off), which leads to jerky "bang-bang" control that wastes fuel and destabilizes orbits. PPO outputs a continuous probability distribution for thrust.
2.  **Trust Region / Clipping**: The Three-Body Problem is chaotic. A slightly wrong update to the neural network can cause the agent to forget everything and crash. PPO’s **Clipping** mechanism (limiting updates to usually 20%) ensures the AI learns conservatively and doesn't destroy its own knowledge base.
3.  **Sample Efficiency**: We need millions of timesteps. PPO is robust and requires less hyperparameter tuning than **SAC** (Soft Actor-Critic) while being safer for physical control tasks.

### **Q: Explain the Actor-Critic Architecture used here.**
**A:** We use two separate neural networks working in tandem:
*   **The Pilot (Actor)**: Views the state (`[x, y, z, vx, vy, vz, fuel]`) and outputs the **Action** (`[Fx, Fy, Fz]`). It learns "What to do."
*   **The Instructor (Critic)**: Views the state and outputs a single **Value** number. It predicts "How good is this situation?" (Expected future reward).
*   **Learning**: If the Pilot makes a move and gets a higher reward than the Instructor predicted, the Pilot is rewarded (Advantage > 0). The Instructor then updates its prediction to be more accurate next time.

### **Q: What is the "Clipping" function in PPO?**
**A:** The core mathematical innovation of PPO is the **Clipped Surrogate Objective**.
$$ L(\theta) = \hat{\mathbb{E}}_t \left[ \min(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t) \right] $$

*   **Ideally**: We want to improve the policy as much as possible ($r_t(\theta)\hat{A}_t$).
*   **Problem**: If we change the policy too much based on a single batch of data, we might overshoot and destroy the delicate stability the agent has learned.
*   **Solution**: PPO "clips" the update. If the new policy is too different from the old one (ratio $r_t(\theta)$ is far from 1.0, e.g., > 1.2 or < 0.8), the update is capped.
    *   **Interpretation**: "Improve the policy by pushing it towards good actions, but if the new policy starts drifting more than 20% away from the old one, stop pushing so we don't accidentally wreck stable behaviors."
    *   This ensures **incremental, safe learning**.

---

## 🏆 The Reward Function (Teaching the AI)

The reward function communicates our goals to the AI. It is calculated at **every single timestep**.

$$ R_t = R_{base} + R_{halo} - P_{vel} - P_{fuel} - P_{dist} - P_{crash} $$

### **1. 🟢 Bonuses (Good Behavior)**
*   **Survival Baseline ($R_{base} = +0.1$)**:
    *   Awarded simply for not crashing. This prevents the "suicide" bug where an agent crashes immediately to avoid negative penalties.
*   **Halo Shell Bonus ($R_{halo} = +1.0$)**:
    *   **The most critical component.** Awarded **only** if distance to L1 is between `0.01` and `0.08`.
    *   This forces the agent to orbit *around* L1 rather than stopping directly *at* L1 (which is impossible/unstable). It defines the "shape" of the solution we want.

### **2. 🔴 Penalties (Bad Behavior)**
*   **Fuel Penalty ($P_{fuel} = -0.5 \times ||Thrust||^2$)**:
    *   **Why Quadratic?** Punishing $Thrust^2$ means high thrust is **exponentially** more expensive than low thrust.
    *   **Effect**: The agent learns that "Drifting (0 thrust) is free." It will fight gravity only when absolutely necessary, mimicking real-world fuel optimization.
*   **Stability / Velocity Penalty ($P_{vel} = -0.1 \times ||Velocity||$)**:
    *   Discourages the agent from zooming past the target at high speeds. It acts as a "damper" on the system.
*   **Distance Gradient ($P_{dist} = -2.0 \times Distance$)**:
    *   A constant, gentle gravity well pulling the agent toward L1 even if it's far away.
*   **Crash Penalty ($P_{crash} = -50.0$)**:
    *   If the agent drifts too far (> 0.1 units), it is "dead." The huge penalty ensures avoiding this is the #1 priority.

---

## 📚 Technical Implementation Details

### **Q: What is Reference State Initialization (RSI)?**
**A:**
*   **Problem**: Stabilizing a Halo orbit from a random starting point is like balancing a pencil on its tip during an earthquake. Most random starts crash instantly.
*   **Solution**: Occasionally (20% of episodes), we "cheat" and start the agent in a known valid state (calculated by math).
*   **Result**: This gives the AI valid training data immediately ("Oh, *this* is what a good orbit looks like!"), allowing it to learn how to *maintain* the orbit before it learns how to *find* it.

### **Q: Why normalize the physics ($\mu$)?**
**A:**
*   Neural networks fail when inputs vary wildly (e.g., Distance = 150,000,000 km, Mass = $10^{24}$ kg).
*   We normalize the Earth-Moon system so Distance = 1.0 and Mass = 1.0. The only variable remaining is the mass ratio $\mu \approx 0.012$.
*   This makes the AI **Universally Applicable** to any two-body system (Sun-Earth, Jupiter-Europa) just by changing $\mu$.
