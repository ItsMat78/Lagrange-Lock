
# Phase 2 Presentation Guide: The Environment

## 1. The Concept: "Visual Verification"
Start by explaining *why* you built this environment before building the AI.
*   **The Narrative:** "Before training an AI to control a satellite, I needed a 'Digital Twin' of the physics. If the environment isn't realistic, the AI learns nothing useful."
*   **The Solution:** "I built a custom Realtime Physics Engine in the browser using the Normalized CR3BP (Circular Restricted Three-Body Problem) equations."

## 2. The Demo: `realtime_viewer.html`
Open `phase_2/realtime_viewer.html`.

### A. The Physics (Stability)
1.  **Select "Earth-Moon":** Show the default view.
2.  **Point out L1:** Explain how the satellite starts near the Lagrange Point (L1).
3.  **Let it Run:** Don't touch anything. Watch the satellite drift.
    *   *Say:* "This drift isn't an animation error; it's the natural chaos of three-body physics. The satellite falls off the 'gravitational hill'."

### B. The Modularity (Configuration)
1.  **Open Config Panel:** (Top Right).
2.  **Change Scale:** Increase `Size 1` (Primary Body) to `2.0`. Click `RESPAWN`.
    *   *Show:* The blue sphere instantly grows.
3.  **Change Mass Parameter ($\mu$):** Change `Mass Param` to `0.5` (Binary Star System). Click `RESPAWN`.
    *   *Show:* The two bodies are now equal size (if you reset scale). The gravity field has fundamentally changed.
    *   *Say:* "This proves the engine is general-purpose. I can simulate Earth-Moon, Sun-Jupiter, or binary stars just by changing one variable."

### C. The Crash System (Safety)
1.  **Force a Crash:**
    *   In the Config Panel, set `Sat Initial X` to `-0.01` (Inside the Primary Body effectively).
    *   Click `RESPAWN`.
2.  **Result:** The screen flashes **"IMPACT DETECTED"**.
    *   *Say:* "I implemented real-time collision detection. This is critical for the AI Phase—if the agent crashes, it receives a massive penalty."

## 3. Technical Highlights
*   **Integration:** "The simulation solves the Runge-Kutta (RK4) differential equations 60 times per second in JavaScript."
*   **Independence:** "The Simulation Loop is decoupled from the Rendering Loop, ensuring physical accuracy even if the frame rate drops."

## 4. Closing
"This environment is now the perfect 'Gym' for our AI. It is accurate, modular, and has clear success/failure states."
