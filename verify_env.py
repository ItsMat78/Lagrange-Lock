import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import os

# Add current directory to path to allow import of cr3bp_env
sys.path.append(os.getcwd())

# Import the environment directly which now handles registration
import cr3bp_env

def test_env():
    print("Creating environment...")
    env = gym.make('CR3BP-v0', render_mode='rgb_array')
    
    print("Resetting environment...")
    obs, info = env.reset(seed=42)
    print(f"Initial Observation: {obs}")
    assert obs.shape == (6,), "Observation shape mismatch"
    
    print("Stepping environment...")
    action = env.action_space.sample()
    print(f"Sample Action: {action}")
    
    start_time = time.time()
    obs, reward, terminated, truncated, info = env.step(action)
    end_time = time.time()
    
    print(f"Step took {end_time - start_time:.4f} seconds")
    print(f"Observation after step: {obs}")
    print(f"Reward: {reward}")
    print(f"Terminated: {terminated}")
    
    # Check for NaNs
    assert not np.any(np.isnan(obs)), "Observation contains NaNs"
    
    # Test Render
    print("Testing Render...")
    frame = env.render()
    if frame is not None:
        print(f"Render returned frame with shape: {frame.shape}")
        assert frame.shape[2] == 3, "Render should be RGB"
    else:
        print("Render returned None")

    env.close()
    print("Test passed!")

if __name__ == "__main__":
    test_env()
