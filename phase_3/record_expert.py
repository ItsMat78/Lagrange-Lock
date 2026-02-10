import sys
import os
# Add project root to path so 'phase_3' module can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import gymnasium as gym
from stable_baselines3 import PPO
from phase_3.satellite_env import SatelliteEnv
from imitation.data import serialize
from imitation.data.types import TrajectoryWithRew
import numpy as np
import os

def record_expert(model_path, output_path, n_episodes=50, min_reward_threshold=0):
    """
    Loads a PPO model, runs episodes, and saves the trajectories of satisfying episodes.
    """
    print(f"Loading model from {model_path}...")
    env = SatelliteEnv()
    
    try:
        model = PPO.load(model_path, env=env)
    except FileNotFoundError:
        print(f"Error: Model not found at {model_path}")
        return

    trajectories = []
    
    print(f"Collecting {n_episodes} episodes...")
    
    accepted_episodes = 0
    
    for i in range(n_episodes):
        obs, _ = env.reset()
        done = False
        truncated = False
        
        # Lists to store episode data
        obs_list = [obs]
        act_list = []
        rew_list = []
        # We don't strictly need infos for BC, but good to have
        infos_list = [] 
        
        episode_reward = 0
        
        while not (done or truncated):
            action, _ = model.predict(obs, deterministic=True)
            next_obs, reward, done, truncated, info = env.step(action)
            
            obs_list.append(next_obs)
            act_list.append(action)
            rew_list.append(reward)
            # infos_list.append(info) # info might be empty
            
            episode_reward += reward
            obs = next_obs
            
        # Filter: Only save if it was a "good" episode
        # You can adjust this threshold based on what you consider "expert" behavior
        if episode_reward >= min_reward_threshold:
            # imitations expects numpy arrays
            traj = TrajectoryWithRew(
                obs=np.array(obs_list),
                acts=np.array(act_list),
                infos=None, # Optional
                terminal=True,
                rews=np.array(rew_list)
            )
            trajectories.append(traj)
            accepted_episodes += 1
            print(f"Episode {i+1}: Reward {episode_reward:.2f} [ACCEPTED]")
        else:
            print(f"Episode {i+1}: Reward {episode_reward:.2f} [REJECTED - Threshold {min_reward_threshold}]")

    if trajectories:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        serialize.save(output_path, trajectories)
        print(f"\nSaved {len(trajectories)} trajectories to {output_path}")
    else:
        print("\nNo trajectories passed the threshold. Nothing saved.")

if __name__ == "__main__":
    # Example usage:
    # 1. Train your PPO model normally first
    # 2. Run this to filter the BEST runs from that model
    
    MODEL_PATH = "phase_3/models/PPO/ppo_sat_final"
    OUTPUT_PATH = "phase_3/data/expert_trajectories.npz"
    
    # Set threshold high enough that only stable orbits are kept
    # Note: Adjust strictly based on your reward function scale!
    # If a survival run gets ~200 reward, set this to 150.
    record_expert(MODEL_PATH, OUTPUT_PATH, n_episodes=20, min_reward_threshold=50)
