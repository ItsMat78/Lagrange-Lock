
import numpy as np
from scipy.optimize import newton

def get_lagrange_points(mu):
    """
    Returns dictionary with L1, L2, L3 locations (x-coordinates).
    Uses Hill Sphere approximation for better initial guesses.
    """
    # 1. Analytic Approximations (Hill Radius)
    # L1 and L2 are approx at distance alpha = (mu/3)^(1/3) from secondary
    alpha = (mu/3)**(1/3)
    
    guess_l1 = (1 - mu) - alpha
    guess_l2 = (1 - mu) + alpha
    guess_l3 = -1.0 # Roughly opposite
    
    # 2. Define Equations
    # L1: x < 1-mu (between primaries)
    def eq_L1(x): 
        # Singularity at x = -mu (Primary) and x = 1-mu (Secondary)
        return x - (1-mu)/(x+mu)**2 + mu/(x-(1-mu))**2
    
    # L2: x > 1-mu (outside secondary)
    def eq_L2(x): 
        return x - (1-mu)/(x+mu)**2 - mu/(x-(1-mu))**2
        
    # L3: x < -mu (outside primary)
    def eq_L3(x): 
        return x + (1-mu)/(x+mu)**2 + mu/(x-(1-mu))**2

    # 3. Solve with robust guesses
    try:
        l1 = newton(eq_L1, guess_l1, maxiter=50)
    except:
        l1 = guess_l1 # Fallback
        
    try:
        l2 = newton(eq_L2, guess_l2, maxiter=50)
    except:
        l2 = guess_l2
        
    try:
        l3 = newton(eq_L3, guess_l3, maxiter=50)
    except:
        l3 = guess_l3
    
    return {'L1': l1, 'L2': l2, 'L3': l3}
