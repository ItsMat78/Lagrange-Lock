# Phase 3: AI Training & Export

This folder contains the Reinforcement Learning (RL) pipeline for the satellite station-keeping agent.

## Key Files

- **`satellite_env.py`**: The Gymnasium environment simulating the CR3BP physics.
    - *Goal*: Keep satellite in a "Halo Orbit" shell (0.02 - 0.1 dist) around L1.
    - *Reward*: Promotes fuel efficiency (quadratic penalty) and stability.
- **`fast_dynamics.py`**: JIT-compiled physics engine (Numba) for high-speed training.
- **`train.py`**: Main script to train the PPO agent from scratch.
    - *Usage*: `python phase_3/train.py`
- **`export_onnx.py`**: Converts trained PyTorch models to ONNX for the web viewer.
    - *Usage*: `python phase_3/export_onnx.py`

## Imitation Learning (New!)

If you have a partial model or want to clone behavior:

1.  **Record Data**: Run your best model to collect "expert" trajectories.
    ```bash
    python phase_3/record_expert.py
    ```
    *Note*: This filters for high-reward episodes only.

2.  **Train from Data**: Train a new agent using Behavior Cloning (BC) + PPO fine-tuning.
    ```bash
    python phase_3/train_bc.py
    ```

## Advanced Improvements

To further improve the model beyond standard PPO:

1.  **Curriculum Learning**:
    - Modify `satellite_env.py` to start the agent *perfectly* on the L1 point with 0 velocity.
    - Once it masters that, slowly increase the random noise in `reset()`.
    
2.  **Symmetry Augmentation**:
    - The CR3BP system is symmetric across the X-axis (`y -> -y`, `vy -> -vy`).
    - You can double your training data (or Replay Buffer) by flipping every observed transition.

3.  **Physics-Informed Inputs**:
    - Currently, the agent sees `[x, y, z, vx, vy, vz]`.
    - It might help to explicitly give it **Distance to Earth** and **Distance to Moon** as extra inputs so it doesn't have to "calculate" gravity fields internally.

4.  **Reward Engineering**:
    - **Manifold Alignment**: Penalize velocity components that are perpendicular to the stable manifold (requires complex math).
    - **Energy Conservation**: Penalize changes in Jacobi Constant (energy) that aren't explained by the thrust used.

## Troubleshooting

- **ImportError / ModuleNotFound**: Run scripts from the project root (e.g., `python phase_3/train.py`, NOT `cd phase_3` then `python train.py`).
- **Drift**: If the agent drifts, it likely hasn't trained long enough or the action scaling is mismatched. The current viewer applies `0.5x` scaling to match the environment.
