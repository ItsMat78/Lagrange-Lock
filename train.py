import gymnasium as gym
from stable_baselines3 import PPO
import cr3bp_env  # Registers the 'CR3BP-v0' environment
import numpy as np

def train_and_visualize():
    # 1. Initialize the Environment
    env = gym.make('CR3BP-v0')
    
    # 2. Initialize the PPO Model
    # MlpPolicy is suitable for vector observation spaces
    model = PPO("MlpPolicy", env, verbose=1)
    
    print("Starting training...")
    # 3. Train the model
    # 200,000 timesteps as requested
    model.learn(total_timesteps=200000)
    print("Training finished.")
    
    # 4. Save the model
    model_name = "ppo_cr3bp_station_keeping"
    model.save(model_name)
    print(f"Model saved to {model_name}.zip")
    
    # Close training environment
    env.close()
    
    # 5. Validation / Visualization
    print("Starting validation with visualization...")
    
    # Re-initialize environment with human rendering enabled
    env_eval = gym.make('CR3BP-v0', render_mode='human')
    
    obs, info = env_eval.reset()
    
    total_reward = 0.0
    steps = 1000
    
    for _ in range(steps):
        # Predict action using the trained model
        # deterministic=True is better for evaluation
        action, _ = model.predict(obs, deterministic=True)
        
        obs, reward, terminated, truncated, info = env_eval.step(action)
        env_eval.render()
        
        total_reward += reward
        
        if terminated or truncated:
            obs, info = env_eval.reset()
            
    mean_reward = total_reward / steps
    print(f"Validation finished.")
    print(f"Mean Reward over {steps} steps: {mean_reward:.4f}")
    
    print("Press Enter to close window...")
    input()
    env_eval.close()

if __name__ == "__main__":
    train_and_visualize()
