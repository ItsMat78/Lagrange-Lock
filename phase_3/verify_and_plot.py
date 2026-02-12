import numpy as np
import matplotlib.pyplot as plt
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import torch
import os
import json
import sys

# Define path to the model relative to this script
MODEL_PATH = "ppo_satellite_14000000_steps.zip" # In phase_3 directory

# Ensure we can import the environment
# Assuming phase_3 contains satellite_env.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add parent directory to path so 'phase_3' package is found
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(current_dir)

from phase_3.satellite_env import SatelliteEnv

def verify_and_plot():
    print(f"Checking for model at: {os.path.abspath(MODEL_PATH)}")
    
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model file {MODEL_PATH} not found.")
        # Try checking parent dir just in case
        parent_path = os.path.join("..", MODEL_PATH)
        if os.path.exists(parent_path):
            print(f"Found in parent: {parent_path}")
            model_file = parent_path
        else:
            return
    else:
        model_file = MODEL_PATH

    # Initialize environment
    env = SatelliteEnv()
    
    # Load Model
    try:
        model = PPO.load(model_file, env=env, device='cpu') # Force CPU for verification
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    # --- ACTION MAGNITUDE CHECK ---
    print("\n--- CHECKING ACTION DISTRIBUTION ---")
    
    obs, info = env.reset()
    
    # Manually place at L1 perfectly to see what it does
    l1_state = np.array([0.836915, 0, 0, 0, 0, 0])
    env.state = l1_state.copy()
    env.fuel = 1.0
    obs = env._get_obs()
    
    print(f"Initial State (L1): {obs[:3]}")
    
    # --- CROSS-CHECK with ONNX ---
    onnx_path = os.path.join(project_root, "phase_2", "model.onnx")
    if os.path.exists(onnx_path):
        import onnxruntime as ort
        print(f"Loading ONNX for cross-check: {onnx_path}")
        sess = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
        
        # Prepare Input
        # Note: Input name is usually "input" from my export script
        input_name = sess.get_inputs()[0].name
        onx_in = {input_name: obs.reshape(1, 7).astype(np.float32)}
        
        onx_out = sess.run(None, onx_in)[0][0] # First batch
        
        # Get Torch Output
        torch_out, _ = model.predict(obs, deterministic=True)
        
        msg = f"""
--- MODEL OUTPUT COMPARISON (Step 0) ---
Torch Action: {torch_out}
ONNX Action:  {onx_out}
Diff:         {np.linalg.norm(torch_out - onx_out)}

Viewer (JS) First Thrust (Force): [0.2267, -0.0180, -0.0071]
Viewer (JS) Approx Action (x2):   [0.4534, -0.0360, -0.0142]
"""
        print(msg)
        with open("comparison_result.txt", "w") as f:
            f.write(msg)
        
        if np.linalg.norm(onx_out - torch_out) > 1e-4:
            print("CRITICAL: ONNX does not match Torch!")
        if np.linalg.norm(onx_out - np.array([0.4534, -0.0360, -0.0142])) > 0.1:
            print("CRITICAL: Viewer does not match ONNX!")
        else:
            print("SUCCESS: Viewer matches ONNX (approx).")
            
        print("----------------------------------------\n")
    else:
        print("ONNX model not found for cross-check.")

    trajectory = []
    actions = []
    
    steps = 10000 
    
    print(f"Simulating {steps} steps...")
    
    for i in range(steps):
        # Predict
        action, _ = model.predict(obs, deterministic=True)
        
        # Log first few actions
        if i < 10:
            print(f"Step {i} Action: {action} | Magnitude: {np.linalg.norm(action):.4f}")
            
        # Step
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Save for plotting
        trajectory.append({
            "t": i * env.dt,
            "x": float(obs[0]),
            "y": float(obs[1]),
            "z": float(obs[2]),
            "vx": float(obs[3]),
            "vy": float(obs[4]),
            "vz": float(obs[5]),
            "fuel": float(obs[6]),
            "action": action.tolist()
        })
        
        actions.append(action)
        
        if terminated or truncated:
            print(f"Terminated at step {i}")
            break
            
    # Convert to arrays
    traj_data = np.array([([t['x'], t['y'], t['z']]) for t in trajectory])
    actions_data = np.array(actions)
    
    # Analyze Actions
    max_action = np.max(np.abs(actions_data))
    avg_action_mag = np.mean(np.linalg.norm(actions_data, axis=1))
    # --- RANDOMIZED STABILITY CHECK ---
    print("\n--- RUNNING 20 RANDOM EPISODES ---")
    
    survived_steps = []
    best_steps = 0
    best_traj = []
    
    for ep in range(20):
        obs, _ = env.reset() # Random noise +/- 0.02 like training
        
        episode_traj = []
        for i in range(10000):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _ = env.step(action)
            
            episode_traj.append({
                "x": float(obs[0]), "y": float(obs[1]), "z": float(obs[2])
            })
            
            if terminated or truncated:
                survived_steps.append(i)
                if i > best_steps:
                    best_steps = i
                    best_traj = episode_traj
                break
        else:
            survived_steps.append(10000)
            if 10000 > best_steps: # Check if this full episode is the new best
                best_steps = 10000
                best_traj = episode_traj
            
    avg_steps = np.mean(survived_steps)
    print(f"Average Survival Steps: {avg_steps:.1f}")
    print(f"Max Survival Steps: {best_steps}")
    print(f"Survival Distribution: {survived_steps}")

    # Plot Best Trajectory
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Convert best traj
    if best_traj:
        traj_data = np.array([[t['x'], t['y'], t['z']] for t in best_traj])
        ax.plot(traj_data[:,0], traj_data[:,1], traj_data[:,2], label=f'Best ({best_steps} steps)', alpha=0.6)
        ax.scatter([traj_data[0,0]], [traj_data[0,1]], [traj_data[0,2]], color='g', label='Start')
        ax.scatter([traj_data[-1,0]], [traj_data[-1,1]], [traj_data[-1,2]], color='r', label='End')
    
    # L1
    ax.scatter([0.836915], [0], [0], color='k', s=100, label='L1 point')
    
    ax.set_title(f"Best Episode (Max Steps: {best_steps})")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()
    
    plot_path = "verification_plot_random.png"
    plt.savefig(plot_path)
    print(f"\nPlot saved to {os.path.abspath(plot_path)}")
    
    # Save JSON for Web Viewer
    json_path = "trajectory_verify.json"
    with open(json_path, 'w') as f:
        json.dump(trajectory, f)
    print(f"Trajectory JSON saved to {os.path.abspath(json_path)}")

if __name__ == "__main__":
    verify_and_plot()
