# Phase 3: Halo Orbit Training

## Objective
Train a Reinforcement Learning (PPO) agent to maintain a stable Halo Orbit around the Earth-Moon L1 Lagrange Point.

## Status: READY TO START
- **Environment:** `satellite_env.py` is verified.
- **Dynamics:** `fast_dynamics.py` (JIT) is verified and synced with Viewer.
- **Viewer:** `realtime_viewer.html` is fully operational and debugged.

## Next Steps
1.  **Hyperparameter Tuning:** The current model fails (diverges in <10s). We need to adjust PPO hyperparameters (learning rate, entropy coef, etc.).
2.  **Reward Shaping:** Review `satellite_env.py` reward function. It might be too sparse or incentivizing the wrong behavior (e.g., fuel conservation > survival).
3.  **Training Loop:** Execute `train_agent.py` for a longer duration (e.g., 5M steps).
4.  **Curriculum Learning:** Consider starting with easier "station keeping" tasks before full Halo orbit injection.

## How to Run
```bash
cd phase_3
python train_agent.py
```
