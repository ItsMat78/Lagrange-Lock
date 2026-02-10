import sys
import os
# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import gymnasium as gym
from stable_baselines3 import PPO
from phase_3.satellite_env import SatelliteEnv
from imitation.data import serialize
import numpy as np

def train_rsi():
    """
    Trains an agent using Reference State Initialization (RSI).
    It loads expert trajectories and sets them in the environment so the agent
    starts 80% of episodes from a valid valid state.
    """
    
    # 1. Load Data
    data_path = "phase_3/data/expert_trajectories.npz"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run 'record_expert.py' first.")
        return

    print("Loading expert trajectories for RSI...")
    transitions = serialize.load(data_path)
    print(f"Loaded {len(transitions)} trajectories.")
    
    # Extract all observations (states) from flattened trajectories
    # transitions is a list of TrajectoryWithRew
    all_states = []
    for traj in transitions:
        # traj.obs is (N+1, 6)
        all_states.append(traj.obs[:-1]) # exclude terminal? keep all valid points
    
    # Flatten
    expert_states = np.vstack(all_states)
    print(f"Extracted {len(expert_states)} valid state frames for initialization.")

    # 2. Setup Environment with RSI
    env = SatelliteEnv(use_rsi=True)
    env.set_expert_states(expert_states)
    
    # 3. Train PPO
    print("Training PPO with RSI (Curriculum)...")
    
    models_dir = "phase_3/models/PPO"
    os.makedirs(models_dir, exist_ok=True)
    
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        tensorboard_log=None,
        learning_rate=0.0003,
        n_steps=2048,
    )
    
    # Train for 1M steps - should be consistently stable now
    model.learn(total_timesteps=1000000)
    
    save_path = f"{models_dir}/ppo_rsi_v1"
    model.save(save_path)
    print(f"RSI Model saved to {save_path}")

if __name__ == "__main__":
    train_rsi()
