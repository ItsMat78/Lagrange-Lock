import gymnasium as gym
from stable_baselines3 import PPO
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from phase_3.satellite_env import SatelliteEnv
import os

def visualize():
    # Setup paths
    models_dir = "phase_3/models/PPO"
    results_dir = "phase_3/results"
    os.makedirs(results_dir, exist_ok=True)
    
    model_path = f"{models_dir}/ppo_sat_final"
    
    # Load Environment and Model
    env = SatelliteEnv()
    try:
        model = PPO.load(model_path, env=env)
    except FileNotFoundError:
        print(f"Model not found at {model_path}. Did training complete?")
        return

    # Run Episode
    print(f"Loading model from {model_path}...")
    obs, _ = env.reset()
    trajectory = []
    actions = []
    done = False
    truncated = False
    total_reward = 0

    print("Simulating episode...")
    while not (done or truncated):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, _ = env.step(action)
        
        trajectory.append(obs[:3])
        actions.append(action)
        total_reward += reward

    trajectory = np.array(trajectory)
    actions = np.array(actions)
    print(f"Episode finished. Steps: {len(trajectory)}, Total Reward: {total_reward:.2f}")

    # Visualization
    mu = 0.01215
    
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Plot Trajectory
    ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], label='Satellite Path', color='red', linewidth=1.5)
    # Mark Start and End
    ax.scatter(trajectory[0, 0], trajectory[0, 1], trajectory[0, 2], color='green', marker='o', s=50, label='Start')
    ax.scatter(trajectory[-1, 0], trajectory[-1, 1], trajectory[-1, 2], color='black', marker='x', s=50, label='End')

    # Plot Target (L1)
    target = env.target_pos
    ax.scatter([target[0]], [target[1]], [target[2]], color='lime', marker='*', s=150, label='Target (L1)')

    # Formatting
    ax.set_xlabel("X (ND)")
    ax.set_ylabel("Y (ND)")
    ax.set_zlabel("Z (ND)")
    ax.legend()
    ax.set_title(f"Agent Trajectory\nReward: {total_reward:.2f} | Steps: {len(trajectory)}")

    # Adjust view to focus on L1
    mid_x = target[0]
    zoom = 0.05 # Zoom in area
    
    # Check if we drifted way off
    max_range = np.max(np.abs(trajectory - target))
    if max_range > zoom:
        zoom = max_range * 1.1
    
    ax.set_xlim(mid_x - zoom, mid_x + zoom)
    ax.set_ylim(-zoom, zoom)
    ax.set_zlim(-zoom, zoom)
    
    # Save Plot
    save_path = f"{results_dir}/trajectory_plot.png"
    plt.savefig(save_path)
    print(f"Trajectory plot saved to {save_path}")
    
    # Also plot thrusts to see if it's banging-bang or continuous
    plt.figure(figsize=(10, 4))
    plt.plot(actions)
    plt.title("Thrust Actions over Time")
    plt.legend(['Fx', 'Fy', 'Fz'])
    plt.xlabel("Step")
    plt.ylabel("Thrust (Normalized)")
    plt.savefig(f"{results_dir}/thrust_profile.png")
    print(f"Thrust profile saved to {results_dir}/thrust_profile.png")

if __name__ == "__main__":
    visualize()
