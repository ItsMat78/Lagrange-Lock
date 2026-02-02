
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from fast_dynamics import propagate_numba, cr3bp_derivs, rk4_step
from utils import get_lagrange_points

# Constants
MU = 0.01215
L_POINTS = get_lagrange_points(MU)
L1 = L_POINTS['L1']

def event_y_crossing(state):
    """Event function for when y crosses 0 (half period). Not used directly in fixed-step."""
    return state[1]

def objective(decision_vars):
    """
    Objective function for Shooting Method.
    Vars: [vy_0]
    Fixed: [x_0, z_0] (Start at a fixed offset from L1)
    Goal: Minimize x_dot at the next y=0 crossing (Perpendicular Crossing).
    """
    vy_0 = decision_vars[0]
    
    # Initial State: Start at offset from L1
    # Lyapunov Orbit (Planar)
    Ax = 0.01 # Amplitude in x
    x_0 = L1 - Ax
    z_0 = 0.0
    
    # State: [x, y, z, vx, vy, vz]
    # Orthogonal departure: vx=0, vy=?, vz=0
    state = np.array([x_0, 0.0, z_0, 0.0, vy_0, 0.0], dtype=np.float64)
    
    # Propagate until y changes sign (half orbit)
    # Using fixed step loop with break for simplicity/speed
    dt = 0.001
    max_steps = 10000
    
    current_state = state.copy()
    prev_y = current_state[1]
    
    for _ in range(max_steps):
        current_state = rk4_step(current_state, dt, MU)
        curr_y = current_state[1]
        
        # Check crossing
        if prev_y > 0 and curr_y <= 0: # Crossing downwards
            # Linear interpolation for precise crossing state
            # not strictly necessary for coarse minimize, but good for accuracy
            break
        if prev_y < 0 and curr_y >= 0: # Crossing upwards (shouldn't happen for first half)
             break
             
        prev_y = curr_y
        
    # At crossing, we want vx = 0 for periodicity (symmetric)
    vx_final = current_state[3]
    return abs(vx_final)

def find_lyapunov_orbit():
    print(f"Searching for Lyapunov Orbit around L1 ({L1:.4f})...")
    
    # Guess Vy
    guess_vy = -0.1 # Some downward/upward velocity
    
    res = minimize(objective, [guess_vy], method='Nelder-Mead', tol=1e-5)
    
    best_vy = res.x[0]
    print(f"Found Vy: {best_vy:.6f} with residual: {res.fun:.6e}")
    
    # Propagate Full Orbit for Visualization
    Ax = 0.01
    state0 = np.array([L1 - Ax, 0.0, 0.0, 0.0, best_vy, 0.0], dtype=np.float64)
    
    # Propagate for a longer time to see full closed loop
    dt = 0.001
    steps = 4000
    
    traj = []
    curr = state0.copy()
    for _ in range(steps):
        traj.append(curr.copy())
        curr = rk4_step(curr, dt, MU)
    traj = np.array(traj)
    
    # Plot
    plt.figure(figsize=(8, 6))
    plt.plot(traj[:, 0], traj[:, 1], label='Orbit')
    plt.plot(L1, 0, 'rx', label='L1')
    plt.title(f"L1 Lyapunov Orbit (mu={MU})")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    
    # Save generic plot
    plt.savefig('phase_2/lyapunov_orbit.png')
    print("Saved plot to phase_2/lyapunov_orbit.png")

if __name__ == "__main__":
    find_lyapunov_orbit()
