
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy

# Ensure phase_3 module can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from phase_3.satellite_env import SatelliteEnv

class DistanceLoggingCallback(BaseCallback):
    """
    Callback for logging the average distance to L1 per episode.
    """
    def __init__(self, verbose=0):
        super(DistanceLoggingCallback, self).__init__(verbose)
        self.episode_distances = []
        self.current_episode_distances = []
        # Store (accumulated_steps, avg_distance) tuples for plotting
        self.logged_distances = [] 

    def _on_step(self) -> bool:
        # Access the underlying environment instance
        # stable_baselines3 wraps the env, so we need to dig into it
        # training_env is a VecEnv (DummyVecEnv usually)
        # envs[0] is the Monitor wrapper
        # .env is the SatelliteEnv
        
        try:
            # Depending on how many wrappers there are, we might need to unwrap
            base_env = self.training_env.envs[0].unwrapped
            
            # Check if we can access state
            if hasattr(base_env, 'state') and base_env.state is not None:
                # State is [x, y, z, vx, vy, vz]
                # L1 is at base_env.target_pos
                pos = base_env.state[:3]
                target = base_env.target_pos
                dist = np.linalg.norm(pos - target)
                self.current_episode_distances.append(dist)
        except Exception:
            # Fallback if unwrapping fails for some reason
            pass
        
        # Check if episode ended
        # 'dones' is a boolean array for the vectorized environments
        if self.locals.get("dones", [False])[0]:
            if self.current_episode_distances:
                avg_dist = np.mean(self.current_episode_distances)
                self.episode_distances.append(avg_dist)
                
                # Log with total timesteps so we can plot against time
                self.logged_distances.append((self.num_timesteps, avg_dist))
                self.current_episode_distances = []
                
        return True

def plot_results(log_dir, distance_data):
    """
    Plot Reward vs Episodes and Distance vs Time
    """
    # 1. Plot Reward vs Episodes (using Monitor data)
    try:
        # load_results returns a pandas DataFrame with 'r' (reward) and 'l' (length) and 't' (time elapsed)
        # We can also get 'index' which effectively corresponds to episodes if using Monitor
        df = load_results(log_dir)
        
        if not df.empty and 'r' in df:
            rewards = df['r'].values
            episodes = np.arange(len(rewards))
            
            plt.figure(figsize=(10, 5))
            plt.plot(episodes, rewards, label='Reward per Episode')
            plt.xlabel('Episodes')
            plt.ylabel('Reward')
            plt.title('Training Reward over Episodes')
            plt.legend()
            plt.grid(True)
            output_path = os.path.join(log_dir, 'training_rewards.png')
            plt.savefig(output_path)
            plt.close()
            print(f"Saved reward plot to {output_path}")
        else:
            print("No reward data found in monitor logs.")
        
    except Exception as e:
        print(f"Could not plot rewards: {e}")

    # 2. Plot Distance to L1 vs Time (using Callback data)
    try:
        if distance_data:
            steps, dists = zip(*distance_data)
            
            plt.figure(figsize=(10, 5))
            plt.plot(steps, dists, label='Avg Distance to L1', color='orange')
            plt.xlabel('Total Timesteps')
            plt.ylabel('Average Distance (L1 Units)')
            plt.title('Distance to L1 vs. Time')
            plt.legend()
            plt.grid(True)
            output_path = os.path.join(log_dir, 'training_distance.png')
            plt.savefig(output_path)
            plt.close()
            print(f"Saved distance plot to {output_path}")
        else:
            print("No distance data collected to plot.")
            
    except Exception as e:
        print(f"Could not plot distances: {e}")


def train():
    # Directories
    # Using 'phase_3' relative paths since we run from project root ideally
    # But to be safe, let's use absolute paths derived from this file's location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # We want models and logs inside phase_3
    # If this script is in phase_3/, then current_dir IS phase_3
    models_dir = os.path.join(current_dir, "models", "PPO_5M")
    log_dir = os.path.join(current_dir, "logs_5M")
    
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    print(f"Saving models to: {models_dir}")
    print(f"Saving logs to: {log_dir}")

    # Environment Setup
    # Create the environment 
    env = SatelliteEnv()
    # Wrap it with Monitor for SB3 logging (CSVs) which enables results_plotter
    env = Monitor(env, log_dir)
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=100000, # Save every 100k steps
        save_path=models_dir,
        name_prefix="ppo_sat_5M"
    )
    
    dist_callback = DistanceLoggingCallback(verbose=1)

    # Initialize Agent
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        tensorboard_log=log_dir, # Optional: explicit tensorboard log
        learning_rate=3e-4,      # 0.0003
        n_steps=2048,
        batch_size=64,
        gae_lambda=0.95,
        gamma=0.99,
    )
    
    # Training
    TOTAL_TIMESTEPS = 5000000
    print(f"Starting training for {TOTAL_TIMESTEPS} steps...")
    
    try:
        model.learn(
            total_timesteps=TOTAL_TIMESTEPS, 
            callback=[checkpoint_callback, dist_callback]
        )
    except KeyboardInterrupt:
        print("Training interrupted by user. Saving current model...")
    except Exception as e:
        print(f"Training failed with error: {e}")
    
    # Save Final Model
    final_model_path = os.path.join(models_dir, "ppo_sat_5M_final")
    model.save(final_model_path)
    print(f"Training finished. Final model saved to {final_model_path}")
    
    # Plotting
    # We pass the collected data from the callback manually
    plot_results(log_dir, dist_callback.logged_distances)
    
    print("Done.")

if __name__ == "__main__":
    train()
