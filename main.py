import gymnasium as gym
import cr3bp_env  # This registers 'CR3BP-v0'
import time

def main():
    # Create the environment with human rendering to see the plot
    env = gym.make('CR3BP-v0', render_mode='human')
    
    # Reset to get initial state
    obs, info = env.reset()
    
    print("Running simulation...")
    
    for _ in range(200):  # Run for 200 steps
        # Sample a random action (thrust)
        action = env.action_space.sample()
        
        # Take a step
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Render the current state
        env.render()
        
        # Check if episode finished
        if terminated or truncated:
            obs, info = env.reset()
            
    print("Simulation finished. Press 'Enter' to close the window...")
    input()
    env.close()

if __name__ == "__main__":
    print("Starting Main Script...")
    main()
