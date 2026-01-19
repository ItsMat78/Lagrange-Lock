import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
import numpy as np
from scipy.integrate import solve_ivp
from numba import jit
import matplotlib.pyplot as plt

# CR3BP Constants for Earth-Moon
MU = 0.01215

@jit(nopython=True)
def cr3bp_equations(t, state, mu, thrust):
    """
    Differential equations for CR3BP in restricted rotating frame.
    state: [x, y, z, vx, vy, vz]
    mu: mass parameter
    thrust: [tx, ty, tz]
    """
    x, y, z, vx, vy, vz = state
    tx, ty, tz = thrust

    # Distances to primary (Earth) and secondary (Moon)
    # Earth at (-mu, 0, 0), Moon at (1-mu, 0, 0)
    r1 = np.sqrt((x + mu)**2 + y**2 + z**2)
    r2 = np.sqrt((x - (1 - mu))**2 + y**2 + z**2)

    # Partial derivatives of Omega (pseudo-potential)
    # Omega = 0.5 * (x^2 + y^2) + (1-mu)/r1 + mu/r2
    
    omega_x = x - (1 - mu) * (x + mu) / r1**3 - mu * (x - (1 - mu)) / r2**3
    omega_y = y - (1 - mu) * y / r1**3 - mu * y / r2**3
    omega_z = - (1 - mu) * z / r1**3 - mu * z / r2**3
    
    # Equations of motion
    # ax = 2*vy + dOmega/dx + Fx
    # ay = -2*vx + dOmega/dy + Fy
    # az = dOmega/dz + Fz
    
    ax = 2 * vy + omega_x + tx
    ay = -2 * vx + omega_y + ty
    az = omega_z + tz
    
    return np.array([vx, vy, vz, ax, ay, az])

class CR3BPEnv(gym.Env):
    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 30}

    def __init__(self, render_mode=None):
        super().__init__()
        self.mu = MU
        # Approximate L1 point for Earth-Moon
        self.L1 = np.array([0.836915127, 0, 0], dtype=np.float32)
        
        # Action Space: Thrust vector [Tx, Ty, Tz]
        # Box from -1 to 1, scaled by max_thrust in step()
        self.max_thrust = 0.01 
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(3,), dtype=np.float32)
        
        # Observation Space: State vector [x, y, z, vx, vy, vz]
        # Infinite bounds
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(6,), dtype=np.float32)
        
        self.state = None
        self.dt = 0.01  # Non-dimensional time step
        self.t = 0.0
        
        self.render_mode = render_mode
        self.trajectory = []
        
        # Visualization objects
        self.fig = None
        self.ax = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Initialize satellite near L1 with small random perturbation
        pos_noise = self.np_random.uniform(low=-0.01, high=0.01, size=3)
        vel_noise = self.np_random.uniform(low=-0.01, high=0.01, size=3)
        
        self.state = np.concatenate([self.L1 + pos_noise, vel_noise]).astype(np.float32)
        self.t = 0.0
        self.trajectory = [self.state[:3].copy()]
        
        return self._get_obs(), {}

    def _get_obs(self):
        # "Blindness" Constraint: Add Gaussian noise to observations
        noise = self.np_random.normal(loc=0.0, scale=1e-4, size=6)
        obs = self.state + noise
        return obs.astype(np.float32)

    def step(self, action):
        # Scale action to get actual thrust acceleration
        thrust = action * self.max_thrust
        
        # Integration step using RK45 via scipy.integrate.solve_ivp
        # We need to wrap the compiled Numba function
        fun = lambda t, y: cr3bp_equations(t, y, self.mu, thrust)
        
        # Integrate for one time step dt
        sol = solve_ivp(fun, [0, self.dt], self.state, method='RK45', rtol=1e-9, atol=1e-9)
        
        # Update state
        self.state = sol.y[:, -1].astype(np.float32)
        self.t += self.dt
        self.trajectory.append(self.state[:3].copy())
        
        # Calculate Reward
        # 1. Distance to L1 (Positive reward for being close)
        dist = np.linalg.norm(self.state[:3] - self.L1)
        reward_dist = np.exp(-10.0 * dist)
        
        # 2. Fuel Penalty (Negative reward for using thrust)
        # Using norm of action (0 to sqrt(3)) as proxy for effort
        reward_fuel = -0.1 * np.linalg.norm(action)
        
        # 3. Drift Penalty & Termination
        terminated = False
        reward_drift = 0.0
        
        if dist > 0.2:
            terminated = True
            reward_drift = -100.0  # Large penalty for losing station
            
        reward = reward_dist + reward_fuel + reward_drift
        
        truncated = False
        
        return self._get_obs(), reward, terminated, truncated, {}

    def render(self):
        if self.render_mode is None:
            return

        if self.fig is None:
            self.fig, self.ax = plt.subplots(figsize=(6, 6))
            
        self.ax.clear()
        
        # Plot fixed bodies in rotating frame
        # Earth at (-mu, 0), Moon at (1-mu, 0)
        self.ax.plot([-self.mu], [0], 'bo', markersize=8, label='Earth')
        self.ax.plot([1 - self.mu], [0], 'go', markersize=4, label='Moon')
        
        # Plot L1 Point
        self.ax.plot([self.L1[0]], [self.L1[1]], 'rx', markersize=6, label='L1')
        
        # Plot Satellite Trajectory
        traj = np.array(self.trajectory)
        if len(traj) > 0:
            self.ax.plot(traj[:, 0], traj[:, 1], 'k-', alpha=0.5, linewidth=1, label='Sat Path')
            # Current position
            self.ax.plot([traj[-1, 0]], [traj[-1, 1]], 'k*', markersize=6)

        self.ax.set_aspect('equal')
        # Zoom in near L1 to see station keeping
        window = 0.25
        self.ax.set_xlim(self.L1[0] - window, self.L1[0] + window)
        self.ax.set_ylim(-window, window)
        
        self.ax.set_title(f"CR3BP Station Keeping (T={self.t:.2f})")
        self.ax.set_xlabel("x (ND)")
        self.ax.set_ylabel("y (ND)")
        self.ax.legend(loc='upper right')
        self.ax.grid(True, alpha=0.3)

        if self.render_mode == 'human':
            plt.pause(0.001)
        elif self.render_mode == 'rgb_array':
            self.fig.canvas.draw()
            # Extract image from canvas
            # Note: impl depends on backend, but tostring_rgb is common for Agg
            try:
                buffer = self.fig.canvas.tostring_rgb()
                width, height = self.fig.canvas.get_width_height()
                image = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 3))
                return image
            except AttributeError:
                # Fallback for newer matplotlib versions if needed
                buffer = self.fig.canvas.buffer_rgba()
                width, height = self.fig.canvas.get_width_height()
                image = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 4))
                return image[:, :, :3]  # Drop alpha

    def close(self):
        if self.fig:
            plt.close(self.fig)

# Register the environment
register(
    id='CR3BP-v0',
    entry_point='cr3bp_env:CR3BPEnv',
    max_episode_steps=1000,
)
