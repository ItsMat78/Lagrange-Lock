# Daily Progress Report: Lagrange-Lock Phase 3 (AI Training)

**Date**: February 6, 2026

## Executive Summary
Today's session focused on moving beyond "Standard PPO" to advanced **Imitation Learning** and **Curriculum Learning** techniques. We successfully built a pipeline to record "expert" behavior (successful orbit segments) and use that data to pre-train agents. This addresses the core difficulty of the CR3BP environment: the agent randomly crashing before it can learn stable behavior.

## Key Technical Achievements

### 1. Imitation Learning Setup (Behavior Cloning)
We implemented a complete Behavior Cloning (BC) pipeline to "clone" successful strategies:
- **Data Recording**: Created `record_expert.py` to extract high-reward trajectories from existing models, filtering out crashes.
- **Hybrid Training**: Created `train_bc.py` which performs a two-stage training process:
    1.  **Behavior Cloning**: Supervised learning to mimic the expert data (50 epochs).
    2.  **PPO Fine-Tuning**: Reinforcement learning to perfect the strategy (500k steps).
- **Architecture**: Engineered the script to share the exact `policy` network between BC and PPO, ensuring seamless transfer of knowledge.

### 2. Curriculum Learning (Reference State Initialization)
We modified the physics environment to support "Reference State Initialization" (RSI), a powerful curriculum technique:
- **Environment Update**: Modified `satellite_env.py` to accept a database of `expert_states`.
- **Logic**: Instead of always spawning at a difficult random point, the environment now spawns the agent **inside a valid Halo Orbit** 80% of the time. This allows the agent to practice "station keeping" immediately.
- **Training Script**: Created `train_rsi.py` to leverage this new capability.

### 3. Infrastructure & Debugging
We resolved significant compatibility and environment challenges:
- **Dependency Hell**: Fixed conflicts between `numpy 2.x`, `numba`, and `imitation`.
- **Pathing**: Fixed `ModuleNotFoundError` issues by patching system paths in scripts.
- **API Updates**: Updated code to match the latest `imitation` library standards (`TrajectoryWithRew`).
- **ONNX Export**: Updated `export_onnx.py` to support exporting these advanced models to the web viewer.

## Models Status

| Model Name | Type | Status | path |
| :--- | :--- | :--- | :--- |
| `ppo_sat_final` | Standard PPO | **Baseline** | `phase_3/models/PPO/` |
| `bc_policy_only` | Behavior Cloning | **Saved** | `phase_3/models/BC/` |
| `ppo_finetuned_from_bc` | BC + PPO | **Exported** | `phase_2/models/ppo_finetuned_from_bc.onnx` |
| `ppo_rsi_v1` | Curriculum PPO | **Training...** | *(Currently running)* |

## Next Steps
1.  **Validate RSI Model**: Once the current training finishes (<10 mins), export `ppo_rsi_v1` and test it in the viewer.
2.  **Symmetry Augmentation**: Implement X-axis symmetry flipping to double the effective training data.
3.  **Physics Inputs**: Feed `r1` (Earth dist) and `r2` (Moon dist) explicitly to the neural network.
