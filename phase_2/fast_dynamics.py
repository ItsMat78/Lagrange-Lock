"""
JIT-accelerated dynamics module using Numba.
This provides >10,000 steps/sec performance required for RL.
"""

import numpy as np
from numba import njit

@njit(cache=True)
def cr3bp_derivs(state, mu):
    """
    Equations of Motion for CR3BP (JIT Compiled).
    """
    x, y, z, vx, vy, vz = state
    
    # Pre-compute distances
    # Primary (m1) at (-mu, 0, 0)
    r1_sq = (x + mu)**2 + y**2 + z**2
    r1 = np.sqrt(r1_sq)
    r1_cub = r1_sq * r1
    
    # Secondary (m2) at (1-mu, 0, 0)
    r2_sq = (x - (1 - mu))**2 + y**2 + z**2
    r2 = np.sqrt(r2_sq)
    r2_cub = r2_sq * r2
    
    # Derivatives
    
    # ax
    ax = 2 * vy + x - ((1 - mu) * (x + mu) / r1_cub) - (mu * (x - (1 - mu)) / r2_cub)
    
    # ay
    ay = -2 * vx + y - ((1 - mu) * y / r1_cub) - (mu * y / r2_cub)
    
    # az
    az = -((1 - mu) * z / r1_cub) - (mu * z / r2_cub)
    
    # Manual array construction implies simpler C-like handling in Numba
    res = np.empty(6, dtype=np.float64)
    res[0] = vx
    res[1] = vy
    res[2] = vz
    res[3] = ax
    res[4] = ay
    res[5] = az
    return res

@njit(cache=True)
def rk4_step(state, dt, mu):
    """
    Single RK4 integration step (JIT Compiled).
    """
    k1 = cr3bp_derivs(state, mu)
    k2 = cr3bp_derivs(state + 0.5 * dt * k1, mu)
    k3 = cr3bp_derivs(state + 0.5 * dt * k2, mu)
    k4 = cr3bp_derivs(state + dt * k3, mu)
    
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

@njit(cache=True)
def propagate_numba(state0, dt, n_steps, mu):
    """
    Propagate for n_steps with fixed dt.
    Returns the final state.
    """
    current_state = state0.copy()
    for _ in range(n_steps):
        current_state = rk4_step(current_state, dt, mu)
    return current_state
