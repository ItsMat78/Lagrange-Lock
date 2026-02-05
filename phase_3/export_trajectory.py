import gymnasium as gym
from stable_baselines3 import PPO
import numpy as np
import json
from phase_3.satellite_env import SatelliteEnv
import os

def export_trajectory():
    model_path = "phase_3/models/PPO/ppo_sat_final"
    env = SatelliteEnv()
    
    print(f"Loading model from {model_path}...")
    try:
        model = PPO.load(model_path, env=env)
    except FileNotFoundError:
        print("Model not found.")
        return

    obs, _ = env.reset()
    trajectory = []
    
    # Run for a longer duration for visualization
    steps = 5000
    print(f"Simulating {steps} steps...")
    
    for _ in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, _ = env.step(action)
        
        # Store full frame: Position [x,y,z], Action [fx,fy,fz], Reward
        step_data = {
            "pos": obs[:3].tolist(),
            "vel": obs[3:].tolist(),
            "action": action.tolist(),
            "reward": float(reward)
        }
        trajectory.append(step_data)
        
        if done or truncated:
            obs, _ = env.reset()
            # For visualization continuity, we might want to just restart the log 
            # or keep logging multiple episodes. Let's just break for one clean run.
            break

    # Save to JS file
    output_path = "phase_3/trajectory_data.js"
    # Structure: window.RL_DATA = [...]
    js_content = f"window.RL_DATA = {json.dumps(trajectory)};"
    
    with open(output_path, "w") as f:
        f.write(js_content)
    
    print(f"Trajectory exported to {output_path} ({len(trajectory)} frames)")

if __name__ == "__main__":
    export_trajectory()
