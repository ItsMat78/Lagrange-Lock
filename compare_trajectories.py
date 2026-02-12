import json
import numpy as np
import matplotlib.pyplot as plt
import os


output_buffer = ""
def log(msg):
    global output_buffer
    print(msg)
    output_buffer += str(msg) + "\n"

# 1. Load Viewer Data
# Find newest trajectory_data*.json
import glob
list_of_files = glob.glob('trajectory_data*.json') 
if not list_of_files:
    log("Error: No trajectory_data*.json files found.")
    exit()

viewer_file = max(list_of_files, key=os.path.getctime)
log(f"Loading newest viewer data: {viewer_file}")

with open(viewer_file, 'r') as f:
    viewer_data = json.load(f)

v_t = np.array([d['t'] for d in viewer_data])
v_pos = np.array([[d['x'], d['y'], d['z']] for d in viewer_data])
v_thrust = np.array([d['thrust'] for d in viewer_data])
v_fuel = np.array([d['fuel'] for d in viewer_data])

# 2. Load Python Verification Data (if available)
# Prefer ONNX verification file if it exists (matches Viewer model)
onnx_v_file = 'phase_3/trajectory_verify_onnx.json'
std_v_file = 'phase_3/trajectory_verify.json'

if os.path.exists(onnx_v_file):
    python_file = onnx_v_file
    log(f"Using ONNX verification data: {python_file}")
else:
    python_file = std_v_file
    log(f"Using Standard verification data: {python_file}")

p_data = None
if os.path.exists(python_file):
    with open(python_file, 'r') as f:
        p_temp = json.load(f)
        # Downsample Python data (0.01s) to match Viewer (0.1s approx) if needed, 
        # or just plot all. Viewer data is sparse (every 10 steps).
        
        p_t = np.array([d['t'] for d in p_temp])
        p_pos = np.array([[d['x'], d['y'], d['z']] for d in p_temp])
        
        # Determine if 'thrust' (force) or 'action' (control) is logged
        if 'thrust' in p_temp[0]:
            # ONNX script logs actual thrust force
            p_thrust = np.array([d['thrust'] for d in p_temp])
        else:
            # Standard script logs raw action, need to scale by 0.5
            p_thrust = np.array([d['action'] for d in p_temp]) * 0.5 
            
        p_fuel = np.array([d['fuel'] for d in p_temp])
        p_data = True

# 3. Analyze Viewer Drift
l1_pos = np.array([0.836915, 0, 0])
v_dist = np.linalg.norm(v_pos - l1_pos, axis=1)

log("--- VIEWER DATA ANALYSIS ---")
log(f"Duration: {v_t[-1]:.2f}s")
log(f"Final Distance from L1: {v_dist[-1]:.4f} AU")
log(f"Max Distance from L1: {np.max(v_dist):.4f} AU")

# Check where it 'crashes' (> 0.25 AU?)
crash_indices = np.where(v_dist > 0.25)[0]
if len(crash_indices) > 0:
    crash_t = v_t[crash_indices[0]]
    log(f"Viewer 'Crash' (>0.25 AU) time: {crash_t:.2f}s")
else:
    log("Viewer: No crash detected in log range.")

# 4. Compare with Python
if p_data:
    p_dist = np.linalg.norm(p_pos - l1_pos, axis=1)
    
    log("\n--- PYTHON DATA ANALYSIS ---")
    log(f"Duration: {p_t[-1]:.2f}s")
    log(f"Final Distance from L1: {p_dist[-1]:.4f} AU")
    
    p_crash_idx = np.where(p_dist > 0.25)[0]
    if len(p_crash_idx) > 0:
        p_crash_t = p_t[p_crash_idx[0]]
        log(f"Python 'Crash' time: {p_crash_t:.2f}s")
    else:
        log("Python: No crash detected locally.")


    # Plot Comparison
    log("\n--- DETAILED COMPARISON (First 5 seconds) ---")
    log(f"{'Time':<6} | {'View Dist':<10} | {'Py Dist':<10} | {'View X':<10} | {'Py X':<10}")
    log("-" * 60)
    
    for t_check in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]:
        # Find closest index in Viewer
        v_idx = (np.abs(v_t - t_check)).argmin()
        p_idx = (np.abs(p_t - t_check)).argmin()
        
        v_d = v_dist[v_idx]
        p_d = p_dist[p_idx]
        v_x_val = v_pos[v_idx, 0]
        p_x_val = p_pos[p_idx, 0]
        
        log(f"{t_check:<6.1f} | {v_d:<10.4f} | {p_d:<10.4f} | {v_x_val:<10.4f} | {p_x_val:<10.4f}")

    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(v_t, v_dist, label='Viewer (JS)', color='blue', marker='o', markersize=3)
    plt.plot(p_t, p_dist, label='Python (Sim)', color='orange', alpha=0.7)
    plt.axhline(0.25, color='r', linestyle='--', label='Fail Limit')
    plt.title("Distance from L1 over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Distance (AU)")
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    # Compare raw X coordinate
    plt.plot(v_t, v_pos[:,0], label='Viewer X', color='blue')
    plt.plot(p_t, p_pos[:,0], label='Python X', color='orange', alpha=0.7)
    plt.axhline(l1_pos[0], color='k', linestyle='--', label='L1 X')
    plt.title("X Coordinate Comparison")
    plt.xlabel("Time (s)")
    plt.legend()
    plt.grid(True)
    
    
    log("\nSaved comparison_plot.png")
    
    with open("comparison_log.txt", "w", encoding="utf-8") as f:
        f.write(output_buffer)

else:
    log("Python verification data not found.")
