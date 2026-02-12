import gymnasium as gym
from stable_baselines3 import PPO
import numpy as np
import os
import sys

# Ensure imports work
sys.path.append('phase_3')
sys.path.append(os.path.abspath('phase_3'))
from satellite_env import SatelliteEnv

model_path = "phase_3/ppo_satellite_14000000_steps.zip"
env = SatelliteEnv()
model = PPO.load(model_path, env=env, device='cpu')

# Base State (Python L1)
base_obs = np.array([0.836915, 0, 0, 0, 0, 0, 1.0], dtype=np.float32)
act_base, _ = model.predict(base_obs, deterministic=True)

# JS State (Calculated L1)
js_x = 0.8369180073
js_obs = np.array([js_x, 0, 0, 0, 0, 0, 1.0], dtype=np.float32)
act_js, _ = model.predict(js_obs, deterministic=True)

with open('sensitivity_output.txt', 'w') as f:
    f.write(f"Base Action: {act_base}\n")
    f.write(f"JS Action:   {act_js}\n")
    f.write(f"Diff:        {np.linalg.norm(act_base - act_js)}\n")
    f.write(f"Tanh(Base):  {np.tanh(act_base)}\n")
    f.write(f"Tanh(JS):    {np.tanh(act_js)}\n")
