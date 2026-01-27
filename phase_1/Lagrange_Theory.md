# Lagrange Points: The Math of Equilibrium

## 1. Defining "Equilibrium"
In our Rotating Frame, a satellite is "stationary" (equilibrium) if:
1.  Velocity is zero ($\dot{x} = \dot{y} = \dot{z} = 0$).
2.  Acceleration is zero ($\ddot{x} = \ddot{y} = \ddot{z} = 0$).

Looking at our Equations of Motion, if velocity is zero, the Coriolis terms vanish. We are left with:
$$ 0 = \frac{\partial \Omega}{\partial x}, \quad 0 = \frac{\partial \Omega}{\partial y}, \quad 0 = \frac{\partial \Omega}{\partial z} $$

The Lagrange points are simply the places where the **gradient of the potential is zero**. It's physically where the centrifugal force exactly cancels out the gravity of the two bodies.

## 2. The Collinear Points (L1, L2, L3)
These three points lie along the x-axis ($y=0, z=0$).
To find them, we just need to solve for $x$ where $\frac{\partial \Omega}{\partial x} = 0$.

Derivative of Collinear Potential:
$$ x - \frac{1-\mu}{|x+\mu|^3}(x+\mu) - \frac{\mu}{|x-1+\mu|^3}(x-1+\mu) = 0 $$

Since absolute values are annoying, we split this into three regions:
- **L1 Region:** Between the bodies.
- **L2 Region:** Right of the secondary.
- **L3 Region:** Left of the primary.

## 3. The Triangular Points (L4, L5)
These are not on the x-axis. They form equilateral triangles with the two masses.
- Location: $x = 0.5 - \mu$, $y = \pm \frac{\sqrt{3}}{2}$
- **Calculated instantly**, no solver needed!

## 4. Stability
- **L1, L2, L3:** Unstable (Saddle points). Like balancing a ball on a hill.
- **L4, L5:** Stable (if $\mu$ is small enough). Like a ball in a bowl. Dust and asteroids accumulate here (Trojan asteroids).

## 5. Beyond 3 Bodies: Can we do 4+?
You asked: *Is it possible to forward this to 3+ body systems (N-Body Problem)?*

### A. The "Moving Target" Reality
In the real solar system, the Sun, Earth, and Moon all pull on the satellite (4-Body Problem).
- **CR3BP (Our Model):** Calculates "Sun-Earth L1" assuming the Moon doesn't exist.
- **Reality:** The Moon *does* exist. It pulls on that L1 point.
- **Result:** The "Point" is no longer a fixed coordinate. It becomes a **Quasi-Periodic Trajectory** (a Lissajous curve) that wobbles around the theoretical point.

### B. The AI Advantage
This is exactly why we use Reinforcement Learning!
- **Classical Controller:** Needs complex 4-body equations (Bi-Circular Restricted 4-Body Problem) to calculate the wobble exactly.
- **Our AI:** We train it on CR3BP with **Random Noise** (Phase 3).
    - If the Moon pulls it effectively "adds noise" to the gravity vector.
    - Since the AI is trained to fight noise, it often **naturally cancels out the Moon's gravity** without ever being told the Moon exists!
    
**Conclusion:** Yes! We start with 3-Body because it's the "Base Foundation". The AI treats the 4th body (Moon/Jupiter) as just "Wind" that it has to fight against.

