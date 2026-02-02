
import time
import numpy as np
from fast_dynamics import propagate_numba, cr3bp_derivs
import matplotlib.pyplot as plt

def benchmark():
    mu = 0.01215
    state0 = np.array([1.01, 0.0, 0.0, 0.0, -0.01, 0.0], dtype=np.float64)
    dt = 0.001
    n_steps = 100_000
    
    # --- Warmup JIT ---
    print("Warming up JIT...")
    propagate_numba(state0, dt, 10, mu)
    
    # --- Benchmark ---
    print(f"Running {n_steps} steps via Numba RK4...")
    start_time = time.time()
    final_state = propagate_numba(state0, dt, n_steps, mu)
    end_time = time.time()
    
    duration = end_time - start_time
    sps = n_steps / duration
    
    print(f"Time Taken: {duration:.4f} s")
    print(f"Steps Per Second: {sps:,.0f}")
    
    target_sps = 10_000
    if sps > target_sps:
        print(f"SUCCESS: Speed > {target_sps} SPS")
    else:
        print(f"WARNING: Speed < {target_sps} SPS")
        
    print(f"Final State: {final_state}")

if __name__ == "__main__":
    benchmark()
