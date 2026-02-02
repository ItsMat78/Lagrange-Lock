"""
Dynamics module for the Circular Restricted Three-Body Problem (CR3BP).
This module contains the Equations of Motion (EOM) and integration helpers.
"""

import numpy as np
from scipy.integrate import solve_ivp

def cr3bp_equations(t, state, mu):
    """
    Differential equations for the CR3BP in a rotating reference frame.
    
    Args:
        t (float): Time (needed by solve_ivp).
        state (array-like): State vector [x, y, z, vx, vy, vz].
        mu (float): Mass parameter = m2 / (m1 + m2).
        
    Returns:
        list: Derivatives [vx, vy, vz, ax, ay, az].
    """
    x, y, z, vx, vy, vz = state
    
    # Distance to primary (m1) located at (-mu, 0, 0)
    # Note: Primary is at -mu because barycenter is at origin.
    # r1 vector = (x - (-mu), y, z) = (x + mu, y, z)
    r1 = np.sqrt((x + mu)**2 + y**2 + z**2)
    
    # Distance to secondary (m2) located at (1-mu, 0, 0)
    r2 = np.sqrt((x - (1 - mu))**2 + y**2 + z**2)
    
    # Equations of Motion (EOM)
    # Derived from Lagrangian in rotating frame
    
    # Acceleration in x
    # ax = 2*vy + x - (1-mu)*(x+mu)/r1^3 - mu*(x-(1-mu))/r2^3
    ax = 2 * vy + x - ((1 - mu) * (x + mu) / r1**3) - (mu * (x - (1 - mu)) / r2**3)
    
    # Acceleration in y
    # ay = -2*vx + y - (1-mu)*y/r1^3 - mu*y/r2^3
    ay = -2 * vx + y - ((1 - mu) * y / r1**3) - (mu * y / r2**3)
    
    # Acceleration in z
    # az = -(1-mu)*z/r1^3 - mu*z/r2^3
    az = -((1 - mu) * z / r1**3) - (mu * z / r2**3)
    
    return [vx, vy, vz, ax, ay, az]

def propagate_orbit(state0, t_span, mu, rtol=1e-12, atol=1e-12):
    """
    Propagate the state vector forward in time using SciPy's RK45 integrator.
    
    Args:
        state0 (array-like): Initial state [x, y, z, vx, vy, vz].
        t_span (tuple): (t_start, t_end).
        mu (float): Mass parameter.
        rtol (float): Relative tolerance.
        atol (float): Absolute tolerance.
        
    Returns:
        float ndarray: Times
        float ndarray: States (shape: 6 x N)
    """
    sol = solve_ivp(
        fun=lambda t, y: cr3bp_equations(t, y, mu),
        t_span=t_span,
        y0=state0,
        method='RK45',
        rtol=rtol,
        atol=atol
    )
    return sol.t, sol.y

def jacobi_constant(state, mu):
    """
    Calculate the Jacobi Constant (C) for a given state.
    C = x^2 + y^2 + 2(1-mu)/r1 + 2mu/r2 - (vx^2 + vy^2 + vz^2)
    
    Note: Usage differs slightly in literature. This form is common in astrodynamics.
    """
    x, y, z, vx, vy, vz = state
    
    r1 = np.sqrt((x + mu)**2 + y**2 + z**2)
    r2 = np.sqrt((x - (1 - mu))**2 + y**2 + z**2)
    
    velocity_sq = vx**2 + vy**2 + vz**2
    potential_term = (x**2 + y**2) + 2*(1 - mu)/r1 + 2*mu/r2
    
    return potential_term - velocity_sq
