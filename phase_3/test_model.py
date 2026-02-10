import gymnasium as gym
from stable_baselines3 import PPO
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from phase_3.satellite_env import SatelliteEnv

def pack_model_if_needed(model_dir):
    """
    If the model is an unzipped directory, zip it so SB3 can load it.
    """
    if os.path.isdir(model_dir):
        print(f"Model path {model_dir} is a directory. Zipping for SB3...")
        shutil.make_archive(model_dir, 'zip', model_dir)
        return model_dir + ".zip"
    return model_dir

import shutil

def test_model():
    model_path = "ppo_sat_v4_final" # The folder user provided
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return

    # Check if we need to zip it
    # SB3 load usually requires a .zip file or a path without extension that resolves to a .zip
    # But if it's a raw directory, we might need to repack it.
    # Let's try to zip it to a temp file.
    zipped_path = pack_model_if_needed(model_path)
    
    print(f"Loading model from {zipped_path}...")
    
    # Initialize Environment
    # Ensure it matches the training env (7 observations including fuel)
    env = SatelliteEnv()
    
    try:
        model = PPO.load(zipped_path, env=env)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    print("Model loaded. Starting simulation...")
    
    obs, _ = env.reset()
    states = []
    rewards = []
    fuels = []
    
    steps = 2000
    for i in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, _ = env.step(action)
        
        states.append(obs[:6]) # x,y,z,vx,vy,vz
        fuels.append(obs[6])
        rewards.append(reward)
        
        if done or truncated:
            print(f"Episode finished at step {i+1}")
            break
            
    states = np.array(states)
    
    # Analysis
    final_fuel = fuels[-1]
    print(f"Final Fuel: {final_fuel*100:.2f}%")
    print(f"Average Reward: {np.mean(rewards):.4f}")
    
    # 3D Plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot L1 (Target)
    ax.scatter([0.836915], [0], [0], color='red', s=100, label='L1 Point')
    
    # Plot Trajectory
    ax.plot(states[:, 0], states[:, 1], states[:, 2], label='Satellite Path', alpha=0.7)
    
    # Plot Start/End
    ax.scatter([states[0,0]], [states[0,1]], [states[0,2]], color='green', label='Start')
    ax.scatter([states[-1,0]], [states[-1,1]], [states[-1,2]], color='black', label='End')
    
    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_zlabel('Z (AU)')
    ax.legend()
    ax.set_title(f'Station Keeping Test (Fuel Rem: {final_fuel*100:.1f}%)')
    
    output_img = "phase_3/test_trajectory.png"
    plt.savefig(output_img)
    print(f"Trajectory plot saved to {output_img}")

if __name__ == "__main__":
    test_model()
