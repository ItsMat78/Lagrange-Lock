import gymnasium as gym
from gymnasium import spaces
import numpy as np
from phase_3 import fast_dynamics

class SatelliteEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    The goal is to keep the satellite near a Lagrange point.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, mu=0.01215, target_point='L1'):
        super(SatelliteEnv, self).__init__()
        
        self.mu = mu
        self.dt = 0.01  # Integration step size
        
        # Target Point definition (approximate for L1/L2)
        # TODO: Calculate exactly using Newton's method if needed, but hardcoding for speed/simplicity first
        if target_point == 'L1':
            self.target_pos = np.array([0.836915, 0, 0], dtype=np.float32)
        elif target_point == 'L2':
            self.target_pos = np.array([1.15568, 0, 0], dtype=np.float32)
        else:
            raise ValueError("Target point must be 'L1' or 'L2'")

        # Action Space: Continuous Thrust (Fx, Fy, Fz)
        # Range: [-1, 1] scaled by max_thrust later
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(3,), dtype=np.float32)
        
        # Observation Space: [x, y, z, vx, vy, vz]
        # We assume relative position to target might be better, but let's start with absolute state
        # Bounds are roughly +/- 2.0 universe units
        self.observation_space = spaces.Box(low=-5.0, high=5.0, shape=(6,), dtype=np.float32)
        
        self.state = None
        self.max_steps = 2000 # Longer episodes to learn stability
        self.current_step = 0
        self.max_thrust = 0.5  # Relatively high thrust for initial control

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Initialize state near target (small perturbation)
        # Random noise: position +/- 0.01, velocity +/- 0.01
        noise = self.np_random.uniform(low=-0.01, high=0.01, size=(6,))
        self.state = np.concatenate([self.target_pos, [0, 0, 0]]) + noise
        self.state = self.state.astype(np.float64) # Ensure float64 for physics
        
        self.current_step = 0
        return self._get_obs(), {}

    def step(self, action):
        self.current_step += 1
        
        # 1. Apply Action (Thrust)
        # Clip action to ensure valid range [-1, 1]
        action = np.clip(action, -1.0, 1.0)
        
        # Scale action to max thrust
        thrust_vector = action * self.max_thrust
        
        # Propagate Physics
        self.state = fast_dynamics.rk4_step(self.state, self.dt, self.mu)
        
        # Apply Thrust Impulse
        self.state[3:6] += thrust_vector * self.dt
        
        # 2. Calculate Reward
        # Goal: Stable Halo Orbit, Min Fuel, Survival
        
        pos = self.state[:3]
        vel = self.state[3:6]
        
        dist = np.linalg.norm(pos - self.target_pos)
        velocity_mag = np.linalg.norm(vel)
        fuel_usage = np.linalg.norm(action) # 0 to sqrt(3) ~ 1.73
        
        reward = 0.1 # Survival Baseline
        
        # A) Halo Shell Bonus (Strategic Position)
        if 0.02 < dist < 0.10:
            reward += 0.5 
            
        # B) Stability (Low Velocity relative to rotating frame)
        # We want orbit, so some velocity is needed, but minimize "wild" velocity
        reward -= 0.1 * velocity_mag
        
        # C) Fuel Efficiency (Requested Priority)
        # Penalize use of thrusters. This forces it to drift when possible (natural orbit).
        reward -= 0.5 * (fuel_usage ** 2) # Quadratic penalty encourages very small burns
        
        # D) Distance Gradient (Gentle centering)
        if dist > 0.1:
            reward -= 1.0 * (dist - 0.1) # Only penalize if drifting far
            
        # 3. Check Termination
        terminated = False
        truncated = False
        
        FULL_FAIL_DIST = 0.25 
        
        if dist > FULL_FAIL_DIST:
            terminated = True
            reward -= 50.0 # Crash penalty
            
        if self.current_step >= self.max_steps:
            truncated = True
            
        return self._get_obs(), reward, terminated, truncated, {}

    def _get_obs(self):
        # Return state with some noise? For now, perfect state.
        return self.state.astype(np.float32)

    def render(self, mode='human'):
        pass

    def close(self):
        pass
