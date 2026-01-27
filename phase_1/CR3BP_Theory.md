# The Normalized Circular Restricted Three-Body Problem (CR3BP)

## 1. The Setup
Imagine two massive celestial bodies (like the Earth and the Moon) orbiting each other in a circle. We call these the **Primary ($m_1$)** and the **Secondary ($m_2$)**, where $m_1 > m_2$.

A third, much smaller body (the **Satellite**) moves in their gravitational field. It is "Restricted" because its mass is so small it doesn't affect the motion of the two large bodies.

## 2. Why Normalize?
In physics, using real units (kilograms, kilometers, seconds) can be messy because the numbers vary wildly.
- Earth-Moon distance: 384,400 km
- Sun-Earth distance: 149,600,000 km

If we write code using strict kilometers, we need different parameters for every system.
**Normalization** solves this by defining "Universal Units":

1. **Unit of Length ($L^*$):** The distance between the two main bodies is always **1.0**.
2. **Unit of Mass ($M^*$):** The total mass of the system ($m_1 + m_2$) is always **1.0**.
3. **Unit of Time:** Chosen such that the orbital angular velocity ($\omega$) is **1.0** (or orbital period is $2\pi$).

## 3. The Magic Parameter: Mu ($\mu$)
Once we normalize, the entire "Universe" is defined by a single number: **$\mu$** (mass ratio).

$$ \mu = \frac{m_2}{m_1 + m_2} $$

- The mass of the smaller body becomes $\mu$.
- The mass of the larger body becomes $1 - \mu$.

### Examples:
- **Earth-Moon:** $m_2$ is much smaller. $\mu \approx 0.01215$.
- **Sun-Earth:** Earth is tiny compared to Sun. $\mu \approx 3.0 \times 10^{-6}$.
- **Binary Stars (Equal Mass):** $\mu = 0.5$.

## 4. The Coordinate System
We use a **Rotating Reference Frame**. The coordinate system rotates *with* the two bodies, so they appear fixed in space.
- Primary ($1-\mu$) is at $(- \mu, 0, 0)$.
- Secondary ($\mu$) is at $(1 - \mu, 0, 0)$.
*(Note: The origin is the Center of Mass (Barycenter)).*

This simplifies the math drastically because the bodies don't move in our view!

## 5. The Equations of Motion
In this rotating frame, the motion of the satellite is governed by these equations (which we will implement in Phase 2):

$$ \ddot{x} - 2\dot{y} = \frac{\partial \Omega}{\partial x} $$
$$ \ddot{y} + 2\dot{x} = \frac{\partial \Omega}{\partial y} $$
$$ \ddot{z} = \frac{\partial \Omega}{\partial z} $$

Where $\Omega$ (Omega) is the **Pseudo-Potential Function**:
$$ \Omega(x, y, z) = \frac{1}{2}(x^2 + y^2) + \frac{1-\mu}{r_1} + \frac{\mu}{r_2} $$

- $r_1$: Distance from satellite to Primary.
- $r_2$: Distance from satellite to Secondary.
- $\ddot{x}, \ddot{y}, \ddot{z}$: Acceleration.
- $2\dot{y}, 2\dot{x}$: Coriolis acceleration terms (due to rotation).

### Key Takeaway for Phase 1.1:
We don't need to code these *yet* (that's Phase 2), but you must understand that **everything** depends on $x, y, z, \dot{x}, \dot{y}, \dot{z}$ and the single parameter $\mu$.

## 6. FAQ: Why not use Real Units in the Inertial Frame?

It is a common question: *Why do we do all this "Normalization" and "Rotating Frame" math? Why not just use $F=ma$ with kilograms and meters in standard space?*

### A. The Reference Frame Issue
**Station Keeping** is defined relative to the two bodies.
- **In the Rotating Frame:** The Lagrange Point L1 is a fixed coordinate, e.g., $(0.84, 0, 0)$. The target is a single static point.
- **In the Inertial (Non-Rotating) Frame:** The Earth and Moon are orbiting. L1 is whipping around the center at thousands of km/h. Your "Target" is a constantly moving high-speed trajectory. To an AI, this is incredibly confusing to learn.

**Verdict:** We use the Rotating Frame because it makes the *Reference Point* static.

### B. The Normalization (Units) Issue
Neural Networks hate huge numbers.
- **Real Units:**
    - Earth Distance: `149,600,000.0` km
    - Spacecraft Drift: `0.001` km
    - *Problem:* Computers lose precision when adding tiny numbers to huge numbers (Floating Point Error). Neural networks struggle to learn weights that handle both $10^8$ and $10^{-3}$.
- **Normalized Units:**
    - Distance: `1.0`
    - Drift: `1e-5`
    - *Result:* The math is numerically stable, and the AI learns faster.

### C. Does this "mess up" the Static (Inertial) Simulation?
No, because the transformation is **exact**, not an approximation.

You can convert any point from the Rotating Frame $(x_r, y_r)$ to the Inertial Frame $(X_i, Y_i)$ at any time $t$ using a simple **Rotation Matrix**:

$$ X_i = x_r \cos(t) - y_r \sin(t) $$
$$ Y_i = x_r \sin(t) + y_r \cos(t) $$

*(Since we normalized angular velocity $\omega=1$, the angle is just $t$)*.

Think of it like a camera on a merry-go-round:
- The **Rotating Frame** is the camera attached to the merry-go-round. To this camera, the horse looks "stationary".
- The **Inertial Frame** is a camera on the ground. To this camera, the horse is spinning.
- The physics is true for both; it's just a change of coordinate systems. We choose the rotating one because it's easier to calculate "Am I standing still next to the horse?"

## 7. The Core Challenge: The "Saddle Point" Instability
If L1 is a static point, you might ask: *Why can't we just place the satellite there and leave it? Why do we need an AI?*

### The "Balancing a Pencil" Problem
L1 is an **Unstable Equilibrium** (Saddle Point).
- **Stable Directions:** If you push it "sideways" (along the orbit), it might drift back.
- **Unstable Directions:** If you nudge it "towards" Earth or the Moon *even by a millimeter*, it will fall.

Because of gravity, that tiny millimeter error will grow exponentially.
1. $t=0$: Error 1mm
2. $t=10$: Error 10cm
3. $t=50$: Error 100km -> **Crash.**

### The "Blind" Pilot
The problem gets harder: **Your satellite is blind.**
In Phase 3, we add noise. The satellite doesn't define its position as "Exactly at L1". It sees:
*"I think I am at L1... give or take 50km."*

**The AI's Job:**
1.  **Estimate:** "Based on my noisy sensors, where am I actually?" (Implicit Kalman Filter).
2.  **Act:** "Fire thrusters just enough to stop falling, but not so much that I waste fuel."
3.  **Survive:** Keep balancing that pencil forever.

## 8. Why Lagrange Points? (Real World Applications)
You might ask: *If they are unstable and hard to stay at, why bother? Why not just orbit Earth like the ISS?*

### A. The "Parking Spots" of Space
Lagrange points are unique because they stay **fixed** relative to the Earth and Sun/Moon. This is a superpower for specific missions:

1.  **L1 (The Sun Watcher):**
    *   **Location:** Between Sun and Earth.
    *   **Benefit:** Uninterrupted view of the Sun. never blocked by Earth.
    *   **Real Mission:** *SOHO* and *DSCOVR* (detects solar storms before they hit Earth).
2.  **L2 (The Deep Space Eye):**
    *   **Location:** Behind Earth (away from Sun).
    *   **Benefit:** Earth blocks the brilliance of the Sun. It is the darkest, coldest place near us.
    *   **Real Mission:** *James Webb Space Telescope (JWST)*. It needs extreme cold to see infrared light.
3.  **Halo Orbits:**
    *   We don't actually sit *exactly* on the point (that amplifies communication noise with the Sun behind you). We orbit *around* the L-point. This is called a **Halo Orbit**.
    *   Your AI will likely learn to fly a Halo Orbit naturally!

### B. Fuel Efficiency
Even though L1/L2 are unstable, the forces trying to push you away are **tiny**.
- **Low Earth Orbit (ISS):** Requires huge energy to stay up (drag) or change orbit.
- **Lagrange Point:** A "gentle" environment. Station-keeping requires mere meters per second of delta-v (fuel) per year.

### C. The Halo Orbit Advantage (Why not sit still?)
You noticed I mentioned **Halo Orbits** (orbiting the empty space of the L-point). Why do we do this instead of sitting exactly at the coordinate?

1.  **Communication (The "Eclipse" Problem):**
    *   **L2 Example:** If you sit exactly at L2, the Earth is directly between you and the Sun.
    *   *Result:* Earth blocks your Solar Panels (No Power!).
    *   *Result:* Radio signals from Earth pass through the messy atmosphere or are blocked.
    *   **Halo Solution:** By orbiting *around* the L-point (roughly 500,000 km wide), you are always visible to Earth and always in sunlight.

2.  **Scientific Stability:**
    *   Sitting on a razor's edge requires constant, jittery correction.
    *   Falling into a smooth "limit cycle" (Halo Orbit) is often more fuel-efficient and provides a smoother ride for sensitive instruments.






