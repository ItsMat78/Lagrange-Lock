import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import os

# Add current directory to path to allow import of cr3bp_env
sys.path.append(os.getcwd())

# Import the environment directly to register it if not installed as a package
import cr3bp_env  # This triggers the code in __init__.py if it were a package, but here we just need the file.
# Wait, __init__.py is only run if we import the folder as a package.
# Since we are running this script in the same folder, we should manually register it for the test
# OR use the __init__.py if we import the folder. 
# Let's manually register for safety in this script if gym.make fails, 
# BUT we want to test if the __init__.py works.
# To test __init__.py, we should `import Lagrange-Lock` or similar, but the dash is an issue.
# Instead, we will rely on the fact that `gym` uses `entry_point`.
# IF we register it here manually, we are not testing the __init__.py file strictly.
# However, the user's requirement was that `__init__.py` *exists* so they can use it later.
# For this test, I will explicitely register it to ensure the test runs, confirming the Env class is good.
# Actually, let's try to simulate the user usage.
from gymnasium.envs.registration import register
register(
    id='CR3BP-v0',
    entry_point='cr3bp_env:CR3BPEnv',
    max_episode_steps=1000,
)

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
