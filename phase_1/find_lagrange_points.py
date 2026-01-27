"""
Finds the Collinear Lagrange Points (L1, L2, L3) for a given mu.
L4 and L5 are analytical and trivial.
Using scipy.optimize.brentq (finding roots of a scalar function).
"""

import numpy as np
from scipy.optimize import brentq

def collinear_derivative(x, mu):
    """
    The derivative of the potential function Omega w.r.t x, specifically for y=0, z=0.
    We need to find x where this equals 0.
    
    Equations derived from d(Omega)/dx = 0.
    Includes the proper sign handling for the gravitational terms based on regions.
    """
    # r1 = distance to primary (located at -mu)
    # r2 = distance to secondary (located at 1-mu)
    
    # We use the raw form: x - (1-mu)*(x+mu)/|x+mu|^3 - mu*(x-(1-mu))/|x-(1-mu)|^3
    # Note: (val) / |val|^3 is equivalent to sign(val) / val^2
    
    term1 = x
    
    dist_1 = x + mu
    grav_1 = -(1 - mu) * np.sign(dist_1) / (abs(dist_1)**2)
    
    dist_2 = x - (1 - mu)
    grav_2 = -mu * np.sign(dist_2) / (abs(dist_2)**2)
    
    return term1 + grav_1 + grav_2

def find_points(mu):
    # Primary is at -mu
    # Secondary is at 1-mu
    
    pos_primary = -mu
    pos_secondary = 1 - mu
    
    print(f"Calculating for mu = {mu}")
    print(f"Primary at: {pos_primary:.4f}")
    print(f"Secondary at: {pos_secondary:.4f}")
    
    # --- SEARCH REGIONS ---
    # L3 is to the left of Primary (-inf to -mu)
    l3 = brentq(collinear_derivative, -3.0, pos_primary - 1e-6, args=(mu,))
    
    # L1 is between Primary and Secondary (-mu to 1-mu)
    l1 = brentq(collinear_derivative, pos_primary + 1e-6, pos_secondary - 1e-6, args=(mu,))
    
    # L2 is to the right of Secondary (1-mu to +inf)
    l2 = brentq(collinear_derivative, pos_secondary + 1e-6, 3.0, args=(mu,))
    
    return l1, l2, l3

def main():
    # Earth-Moon System
    mu_earth_moon = 0.0121505856
    l1, l2, l3 = find_points(mu_earth_moon)
    
    print("\n--- Results (Earth-Moon) ---")
    print(f"L1: {l1:.6f} (Between Earth and Moon)")
    print(f"L2: {l2:.6f} (Behind Moon)")
    print(f"L3: {l3:.6f} (Opposite side of Earth)")
    
    # Verify by plugging back in (Should be close to 0.0)
    resid_l1 = collinear_derivative(l1, mu_earth_moon)
    print(f"Check L1 (Residual): {resid_l1:.2e}")

if __name__ == "__main__":
    main()
