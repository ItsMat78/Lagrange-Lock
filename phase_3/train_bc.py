import sys
import os
# Add project root to path so 'phase_3' module can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from phase_3.satellite_env import SatelliteEnv
from imitation.algorithms import bc
from imitation.data import serialize
import os
import numpy as np
import torch

def train_bc_then_ppo():
    """
    1. Loads expert trajectories.
    2. Trains a PPO policy using Behavior Cloning (BC) to mimic them.
    3. Saves the BC-pretrained policy.
    4. (Optional) Continue training with RL (PPO) to improve further.
    """
    
    # 1. Load Data
    data_path = "phase_3/data/expert_trajectories.npz"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run 'record_expert.py' first.")
        return

    print("Loading expert trajectories...")
    transitions = serialize.load(data_path)
    print(f"Loaded {len(transitions)} trajectories.")

    # 2. Setup Environment
    env = SatelliteEnv()
    os.makedirs("phase_3/models/BC", exist_ok=True)

    # 3. Initialize PPO First (to share policy)
    print("Initializing PPO Model...")
    ppo_model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1, 
        tensorboard_log=None,
        learning_rate=3e-4,
    )

    # 4. Behavior Cloning (Pre-training)
    print("Setting up Behavior Cloning trainer...")
    
    rng = np.random.default_rng(0)
    
    # We pass the PPO model's policy directly to BC
    # This ensures they share the exact same network architecture and weights
    bc_trainer = bc.BC(
        observation_space=env.observation_space,
        action_space=env.action_space,
        demonstrations=transitions,
        rng=rng,
        policy=ppo_model.policy, 
        device="auto" 
    )

    print("Training with Behavior Cloning (Mimicking)...")
    bc_trainer.train(n_epochs=50) 
    
    # Save the BC-pretrained policy
    bc_model_path = "phase_3/models/BC/bc_policy_only"
    ppo_model.save(bc_model_path) # saving the PPO model effectively saves the updated policy
    print(f"BC Policy saved to {bc_model_path}")
    
    # 5. Continue with PPO (RL Fine-tuning)
    print("Transitioning to pure PPO training...")
    # The ppo_model.policy has already been updated by bc_trainer!
    # So we just run learn() now.
    
    ppo_model.learn(total_timesteps=500000)
    
    final_path = "phase_3/models/PPO/ppo_finetuned_from_bc"
    ppo_model.save(final_path)
    print(f"Final Fine-tuned Model saved to {final_path}")

if __name__ == "__main__":
    train_bc_then_ppo()
