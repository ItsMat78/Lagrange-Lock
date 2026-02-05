import os
import sys
# Add project root to path so 'phase_3' module can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import CheckpointCallback
from phase_3.satellite_env import SatelliteEnv

def train():
    # Create directories
    models_dir = "phase_3/models/PPO"
    log_dir = "phase_3/logs"
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # Initialize environment
    # We use make_vec_env for parallel training if needed, but start simple
    env = SatelliteEnv()
    
    # Initialize Agent
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        # tensorboard_log=log_dir, # Commented out to fix error if persistent
        tensorboard_log=None,
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64,
        gae_lambda=0.95,
        gamma=0.99,
    )
    
    print("Starting training...")
    # Train
    # Phase 3 Update: Longer training for stable station keeping
    TIMESTEPS = 2000000 
    
    checkpoint_callback = CheckpointCallback(
        save_freq=50000,
        save_path=models_dir,
        name_prefix="ppo_sat_v4"
    )

    model.learn(total_timesteps=TIMESTEPS, callback=checkpoint_callback)
    
    # Save final model
    model.save(f"{models_dir}/ppo_sat_v4_final")
    print("Training finished. Model saved.")
    
    # Post-training cleanup: Delete intermediate checkpoints
    print("Cleaning up intermediate checkpoints...")
    import glob
    checkpoints = glob.glob(f"{models_dir}/ppo_sat_v4_*_steps.zip")
    for cp in checkpoints:
        try:
            os.remove(cp)
            print(f"Deleted {cp}")
        except Exception as e:
            print(f"Failed to delete {cp}: {e}")
    print("Cleanup complete. Only final model preserved.")

if __name__ == "__main__":
    train()
