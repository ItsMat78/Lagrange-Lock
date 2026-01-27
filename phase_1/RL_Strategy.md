# Reinforcement Learning Strategy: The "Blind" Pilot

## 1. The Core Concept (MDP vs POMDP)
In standard RL (like playing Chess), you see the entire board perfectly. This is a **Markov Decision Process (MDP)**.
In our satellite problem, sensors are noisy. We don't know exactly where we are. This is a **Partially Observable MDP (POMDP)**.

**The Challenge:** The Agent effectively needs to learn two skills at once:
1.  **Estimator:** "Where am I regarding the noise?" (Internal Kalman Filter).
2.  **Controller:** "Given where I think I am, how do I thrust to stay at L1?"

## 2. The "Brain" Components

### A. The State (Observation)
This is what the Neural Network "sees" every 0.1 seconds.
**Vector Shape:** `(6,)`
1.  $x + noise$
2.  $y + noise$
3.  $z + noise$
4.  $\dot{x} + noise$
5.  $\dot{y} + noise$
6.  $\dot{z} + noise$

*Note: We normalize these inputs to be roughly between -1 and 1 so the network learns faster.*

### B. The Action
This is what the Neural Network "does" every step.
**Vector Shape:** `(3,)` (Continuous values between -1.0 and 1.0)
1.  $T_x$: Thrust in X direction.
2.  $T_y$: Thrust in Y direction.
3.  $T_z$: Thrust in Z direction.

*Realism Note:* The engine has a maximum thrust ($F_{max}$).
$$ \text{Actual Force} = \text{Action} \times F_{max} $$

### C. The Reward Function (The Teacher)
This is how we tell the AI if it's doing a good job. It is a score calculated every step.

$$ R = R_{survival} - R_{fuel} - R_{distance} $$

1.  **Survival Bonus (+1.0):** You didn't crash this second? Good job.
2.  **Fuel Penalty (-0.1 * |Action|):** Don't fire the engines if you don't have to. Drift if possible.
3.  **Distance Penalty (-1.0 * Dist):** The further you are from L1, the lower your score.

## 3. The Algorithm: PPO (Proximal Policy Optimization)
We will use **PPO** from Stable Baselines3.
*   **Why?** It is the industry standard for continuous control (robotics).
*   **How it works:** It collects a batch of experiences, tries to improve the policy slightly, but ensures it doesn't change *too much* at once (preventing "catastrophic forgetting").

## 4. Episode Structure
- **Start:** Satellite is placed near L1 with a small random velocity.
- **Step:** Simulation runs for 0.1 seconds.
- **End (Game Over):**
    - Satellite crashes into Earth/Moon.
    - Time limit reached (Success!).

## 5. Realism Upgrade: The Thruster Problem
You asked: *Can we teach the AI to use specific thrusters instead of just "Force X/Y/Z"?*

### The "Control Allocation" Dilemma
Real satellites use a **Reaction Control System (RCS)**, typically 6 to 12 small nozzles.
*   **Idealized (Easy):** Agent outputs `[Tx, Ty, Tz]`. We magically apply that force.
*   **Realistic (Hard):** Agent outputs `[Thruster_1, Thruster_2, ..., Thruster_N]`.

### Option A: The "GNC" Approach (Recommended for Phase 1-4)
In professional aerospace, we split the brain:
1.  **Guidance (AI):** Decides *where* to push. Output: `Force_Vector`.
2.  **Control Allocator (Math Script):** Decides *which thrusters* to fire to achieve that vector.
    *   *Why?* The AI shouldn't waste time relearning that "Thruster 1" points Left. That is a known mechanical fact.

### Option B: The "End-to-End" Approach (Advanced)
We give the AI direct control over the valves.
*   **Action Space:** `MultiBinary(6)` (Fire +X, -X, +Y, -Y, +Z, -Z).
*   **Pros:** Can handle **Thruster Failure**. If Thruster +X breaks, the AI might learn to rotate and use +Y to move sideways!
*   **Cons:** Takes 10x longer to train.

**Decision:** We will start with **Option A (Force Vector)** to get the physics working. In Phase 5, we can swap the Action Space to **Option B** to test "Thruster Failure Scenarios".


## Key Takeaway for Phase 2
We are building the "Gymnasium" (The Video Game) where this Agent lives. It needs to provide:
1.  `reset()`: Randomize starting position.
2.  `step(action)`: Calculate physics, add noise, return new state and reward.
