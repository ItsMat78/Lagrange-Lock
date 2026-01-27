import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import EvalCallback # <--- NEW IMPORT
import cr3bp_env
import numpy as np
import os

def train_and_visualize():
    # --- 1. SETUP ENVIRONMENTS ---
    # Training Environment
    env = gym.make('CR3BP-v0')
    env = DummyVecEnv([lambda: env])
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.)

    # Evaluation Environment (The "Test" Bench)
    # We need a separate env to test the agent without noise/exploration
    eval_env = gym.make('CR3BP-v0')
    eval_env = DummyVecEnv([lambda: eval_env])
    # Important: Link the normalization stats so eval_env knows what "normal" looks like
    eval_env = VecNormalize(eval_env, norm_obs=True, norm_reward=True, clip_obs=10.)

    # --- 2. SETUP CALLBACK (The "Best Model" Saver) ---
    save_path = "./logs/best_model/"
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=save_path,
        log_path="./logs/results/",
        eval_freq=5000,          # Test the agent every 5000 steps
        deterministic=True,      # Test without random noise (pure skill)
        render=False
    )

    # --- 3. TRAIN ---
    print("Starting training with Best Model Callback...")
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=3e-4, ent_coef=0.01)
    
    # Add the callback here
    model.learn(total_timesteps=500000, callback=eval_callback) 
    print("Training finished.")

    # Save the final model (just in case)
    model.save("ppo_cr3bp_final")
    env.save("vec_normalize.pkl") # Save normalization stats

    # --- 4. VISUALIZATION (Load the BEST model) ---
    print("Loading the BEST model for visualization...")
    
    # 1. Load the best model instead of the final one
    best_model_path = os.path.join(save_path, "best_model.zip")
    model = PPO.load(best_model_path)

    # 2. Setup visualization env
    viz_env = gym.make('CR3BP-v0', render_mode='human')
    viz_env = DummyVecEnv([lambda: viz_env])
    viz_env = VecNormalize.load("vec_normalize.pkl", viz_env)
    viz_env.training = False 
    viz_env.norm_reward = False

    obs = viz_env.reset()
    
    for _ in range(2000):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = viz_env.step(action)
        viz_env.render()
        
        # SB3 handles the reset automatically if done=True

    viz_env.close()

if __name__ == "__main__":
    train_and_visualize()