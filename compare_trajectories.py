
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from phase_3.satellite_env import SatelliteEnv
from stable_baselines3 import PPO

def pack_model_if_needed(model_dir):
    import shutil
    if os.path.isdir(model_dir):
        print(f"Model path {model_dir} is a directory. Zipping for SB3...")
        shutil.make_archive(model_dir, 'zip', model_dir)
        return model_dir + ".zip"
    return model_dir

def compare_trajectories():
    # 1. Load JS Trajectory
    json_path = 'trajectory_data.json'
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, 'r') as f:
        js_data = json.load(f)
    
    # Extract JS points
    js_x = [d['x'] for d in js_data]
    js_y = [d['y'] for d in js_data]
    js_z = [d['z'] for d in js_data]
    
    # Initial State from JS
    start_node = js_data[0]
    initial_state = np.array([
        start_node['x'], start_node['y'], start_node['z'],
        start_node['vx'], start_node['vy'], start_node['vz']
    ], dtype=np.float64)
    
    print(f"Initial State from JSON: {initial_state}")

    # 2. Run Python Simulation
    model_path = os.path.join('phase_3', 'models', 'ppo_satellite_14000000_steps') # Adjust if needed
    
    # If .zip exists, use it. If directory, pack it.
    # If .zip exists, use it. If directory, pack it.
    root_model_path = 'ppo_sat_v4_final.zip'
    if os.path.exists(root_model_path):
        model_path = root_model_path
    elif os.path.exists('ppo_sat_v4_final') and os.path.isdir('ppo_sat_v4_final'):
         pack_model_if_needed('ppo_sat_v4_final')
         model_path = 'ppo_sat_v4_final.zip'
    else:
        # Fallback to check relative to root if running from root
        if os.path.exists('phase_3/models/ppo_satellite_14000000_steps.zip'):
             model_path = 'phase_3/models/ppo_satellite_14000000_steps.zip'
        else:
             print("Model not found.")
             return

    print(f"Loading model from {model_path}...")
    
    try:
        # Load without env first to avoid strict space checks failure if minor mismatch
        model = PPO.load(model_path)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    env = SatelliteEnv()

    # Set initial state
    # We need to manually override reset to force this state
    env.reset()
    env.state = initial_state.copy()
    env.fuel = start_node.get('fuel', 1.0)
    
    py_x = []
    py_y = []
    py_z = []

    # Simulation parameters
    # JS data is usually 0.1s intervals. 
    # Python dt is 0.01.
    # User said "for 10 seconds". 
    # That means 1000 Python steps (1000 * 0.01 = 10s).
    # We will record every step for smooth plot, or every 10th for direct comparison?
    # Let's record all for smooth line.
    
    steps = 1000 
    obs = env._get_obs()
    
    print("Running Python simulation...")
    for i in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, _ = env.step(action)
        
        state = env.state
        py_x.append(state[0])
        py_y.append(state[1])
        py_z.append(state[2])
        
        if done or truncated:
            print(f"Python simulation ended early at step {i}")
            break
            
    # 3. Plot Comparison
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot JS Data (Points/Line)
    ax.plot(js_x, js_y, js_z, label='HTML Env (JS)', color='blue', linestyle='--', linewidth=2, alpha=0.7)
    
    # Plot Python Data
    ax.plot(py_x, py_y, py_z, label='Python Env', color='orange', linewidth=2, alpha=0.9)
    
    # Plot Start
    ax.scatter([initial_state[0]], [initial_state[1]], [initial_state[2]], color='green', s=100, label='Start')
    
    # L1 Point
    ax.scatter([0.836915], [0], [0], color='red', marker='x', s=100, label='L1')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Environment Comparison (10s)')
    ax.legend()
    
    output_file = 'env_comparison_plot.png'
    plt.savefig(output_file)
    print(f"Comparison plot saved to {output_file}")

if __name__ == "__main__":
    compare_trajectories()
