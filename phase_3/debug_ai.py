
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, '..'))

try:
    from satellite_env import SatelliteEnv
    from stable_baselines3 import PPO
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

# Pick first model found
models_dir = os.path.join(current_dir, 'models')
model_path = None
for root, dirs, files in os.walk(models_dir):
    for f in files:
        if f.endswith('.zip'):
            model_path = os.path.join(root, f)
            break
    if model_path: break

if not model_path:
    print("No model found!")
    sys.exit(1)

print(f"Loading model: {model_path}")

try:
    model = PPO.load(model_path)
    print("Model loaded.")
    
    env = SatelliteEnv()
    print("Env created.")
    
    obs, _ = env.reset()
    print("Env reset.")
    
    action, _ = model.predict(obs, deterministic=False)
    print(f"Prediction successful: {action}")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
