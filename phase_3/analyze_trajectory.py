import json
import numpy as np

with open('trajectory_verify.json', 'r') as f:
    data = json.load(f)

print(f"Total points: {len(data)}")
actions = np.array([d['action'] for d in data])
obs = np.array([[d['x'], d['y'], d['z']] for d in data])
fuel = np.array([d['fuel'] for d in data])

# Analyze Actions
means = np.mean(actions, axis=0)
stds = np.std(actions, axis=0)
mins = np.min(actions, axis=0)
maxs = np.max(actions, axis=0)

print("Actions (Fx, Fy, Fz):")
print(f"Mean: {means}")
print(f"Std:  {stds}")
print(f"Min:  {mins}")
print(f"Max:  {maxs}")

# Analyze Drift
dist_from_l1 = np.linalg.norm(obs - np.array([0.836915, 0, 0]), axis=1)
print(f"Max Distance from L1: {np.max(dist_from_l1):.4f}")
print(f"Final Distance: {dist_from_l1[-1]:.4f}")

# Check when it crosses 0.1
idx = np.where(dist_from_l1 > 0.1)[0]
if len(idx) > 0:
    print(f"Crossed 0.1 dist at step {idx[0]}")
else:
    print("Never crossed 0.1 dist")

# Fuel usage
print(f"Fuel Remaining: {fuel[-1]:.4f}")
