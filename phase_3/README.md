# Phase 3: AI Training & Export

This folder contains the Reinforcement Learning (RL) pipeline for the satellite station-keeping agent.

## Key Files

- **`satellite_env.py`**: The Gymnasium environment simulating the CR3BP physics.
    - *Goal*: Keep satellite in a "Halo Orbit" shell (0.02 - 0.1 dist) around L1.
    - *Reward*: Promotes fuel efficiency (quadratic penalty) and stability.
- **`fast_dynamics.py`**: JIT-compiled physics engine (Numba) for high-speed training.
- **`train.py`**: Main script to train the PPO agent.
    - *Usage*: `python phase_3/train.py`
    - *Output*: Saves models to `phase_3/models/PPO/`.
    - *Cleanup*: Automatically deletes intermediate checkpoints, keeping only the final model.
- **`export_onnx.py`**: Converts trained PyTorch models to ONNX for the web viewer.
    - *Usage*: `python phase_3/export_onnx.py`
    - *Output*: `phase_2/models/*.onnx` and `models.json`.
    - *Cleanup*: Automatically removes old `_steps.onnx` files from the viewer.

## How to Train a New Agent

1.  **Configure**: Edit `satellite_env.py` if you want to change physics or rewards.
2.  **Train**:
    ```bash
    python phase_3/train.py
    ```
    (This will run for 2M steps. Takes 15-30 mins depending on CPU).
3.  **Export**:
    ```bash
    python phase_3/export_onnx.py
    ```
4.  **View**: Open `phase_2/realtime_viewer.html` and select the new model.

## Troubleshooting

- **ImportError / ModuleNotFound**: Run scripts from the project root (e.g., `python phase_3/train.py`, NOT `cd phase_3` then `python train.py`).
- **Drift**: If the agent drifts, it likely hasn't trained long enough or the action scaling is mismatched. The current viewer applies `0.5x` scaling to match the environment.
