
import numpy as np
import matplotlib.pyplot as plt
from dynamics import propagate_orbit, jacobi_constant

def test_conservation_of_energy():
    print("Running Jacobi Constant Conservation Test...")
    
    # 1. Setup
    mu = 0.01215 # Earth-Moon
    # Random initial state (not too close to singularities)
    state0 = np.array([0.5, 0.5, 0.1, 0.1, -0.1, 0.05])
    
    # 2. Propagate
    t_span = (0, 10) # 10 non-dimensional time units (~43 days for Earth-Moon)
    times, states = propagate_orbit(state0, t_span, mu)
    
    # 3. Check Energy
    energies = []
    for i in range(states.shape[1]):
        c = jacobi_constant(states[:, i], mu)
        energies.append(c)
        
    energies = np.array(energies)
    delta_e = np.max(energies) - np.min(energies)
    
    print(f"Time steps: {len(times)}")
    print(f"Initial Jacobi Constant: {energies[0]:.6f}")
    print(f"Final Jacobi Constant:   {energies[-1]:.6f}")
    print(f"Max Deviation:           {delta_e:.6e}")
    
    if delta_e < 1e-6:
        print("SUCCESS: Energy is conserved.")
    else:
        print("WARNING: Energy drift detected!")
        
    # Optional: Plot
    # plt.plot(times, energies)
    # plt.show()

if __name__ == "__main__":
    test_conservation_of_energy()
