import gymnasium as gym
import os
from gymnasium import spaces
import numpy as np
from phase_3 import fast_dynamics

class SatelliteEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    The goal is to keep the satellite near a Lagrange point.
    Includes Fuel constraints (~ Delta V budget).
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, mu=0.01215, target_point='L1', use_rsi=False):
        super(SatelliteEnv, self).__init__()
        
        self.mu = mu
        self.dt = 0.01  # Integration step size
        self.use_rsi = use_rsi # Reference State Initialization
        self.expert_states = []
        
        if self.use_rsi:
            try:
                # Load expert states for initialization
                # We need a way to load numpy data. Hardcoding path for simplicity in this phase.
                data_path = "phase_3/data/expert_trajectories.npz"
                if os.path.exists(data_path):
                    # We can't easily use imitation's serialize here due to dependency mess in pure env
                    # So we assume the user provides a raw .npy or we skip RSI if failed.
                    # Actually, let's just use the numpy load directly if possible or skip.
                    # Simplified: We will let the external script inject states, 
                    # OR we just rely on standard reset for now to avoid breaking imports.
                    pass 
            except Exception as e:
                print(f"RSI Load Failed: {e}")

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
        
        # Observation Space: [x, y, z, vx, vy, vz, fuel]
        # MATCH TRAINING ENV: -10 to 10
        self.observation_space = spaces.Box(low=-10.0, high=10.0, shape=(7,), dtype=np.float32)
        
        self.state = None
        self.fuel = 1.0
        self.max_steps = 10000 # Longer episodes to learn stability
        self.current_step = 0
        self.max_thrust = 0.5  # Relatively high thrust for initial control
        self.fuel_consumption_rate = 0.0005 # Rate of fuel burn per unit thrust per step

    def set_expert_states(self, states):
        """ Manually inject expert states for RSI """
        self.expert_states = states
        self.use_rsi = True if len(states) > 0 else False

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self.fuel = 1.0 # Reset fuel tank to 100%
        
        # RSI: Spawn from a random point in a known good trajectory
        if self.use_rsi and len(self.expert_states) > 0 and self.np_random.random() < 0.8:
            # 80% chance to start from expert state, 20% random
            idx = self.np_random.integers(0, len(self.expert_states))
            self.state = self.expert_states[idx].copy()
            # Add tiny noise to prevent memorization
            self.state += self.np_random.uniform(low=-0.001, high=0.001, size=(6,))
        else:
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
        
        # Check Fuel
        thrust_magnitude = np.linalg.norm(action)
        
        # Consume fuel
        if self.fuel <= 0:
            action[:] = 0.0
            thrust_magnitude = 0.0
        else:
            self.fuel -= thrust_magnitude * self.fuel_consumption_rate
            if self.fuel < 0: self.fuel = 0.0
        
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
        fuel_usage = thrust_magnitude # Action magnitude
        
        reward = 0.1 # Survival Baseline
        
        # A) Halo Shell Bonus (Strategic Position)
        # Tightened for strict L1 station keeping
        if 0.01 < dist < 0.08:
            reward += 1.0
            
        # B) Stability (Low Velocity relative to rotating frame)
        # We want orbit, so some velocity is needed, but minimize "wild" velocity
        reward -= 0.1 * velocity_mag
        
        # C) Fuel Efficiency (Requested Priority)
        # Penalize use of thrusters. This forces it to drift when possible (natural orbit).
        reward -= 0.5 * (fuel_usage ** 2) # Quadratic penalty encourages very small burns
        
        # D) Distance Gradient (Gentle centering)
        # Penalize any drift away from L1 to enforce strictness
        reward -= 2.0 * dist 
            
        # 3. Check Termination
        terminated = False
        truncated = False
        
        # Strict Limit: 0.1 AU radius (Earth-Moon distance unit).
        # L1 is at 0.83. Moon is at ~0.99. Gap is ~0.16.
        # 0.1 keeps it well away from Moon's direct capture.
        FULL_FAIL_DIST = 0.10
        
        if dist > FULL_FAIL_DIST:
            terminated = True
            reward -= 50.0 # Crash penalty
            
        if self.current_step >= self.max_steps:
            truncated = True
            
        return self._get_obs(), reward, terminated, truncated, {}

    def _get_obs(self):
        # Return state [x,y,z,vx,vy,vz,fuel]
        # Fast implementation
        obs = np.empty(7, dtype=np.float32)
        obs[:6] = self.state.astype(np.float32)
        obs[6] = float(self.fuel)
        return obs

    def render(self, mode='human'):
        pass

    def close(self):
        pass
