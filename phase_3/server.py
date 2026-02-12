
import http.server
import socketserver
import json
import os
import sys
import numpy as np
import gymnasium as gym

# Ensure we can import fast_dynamics
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add both ./ and ../ to path so imports work whether running from root or phase_3
if current_dir not in sys.path: sys.path.append(current_dir)
parent_dir = os.path.join(current_dir, '..')
if parent_dir not in sys.path: sys.path.append(parent_dir)

try:
    # Try importing as module first
    from phase_3 import fast_dynamics
    from phase_3.satellite_env import SatelliteEnv
except ImportError:
    # Fallback to local import
    import fast_dynamics
    try:
        from satellite_env import SatelliteEnv
    except ImportError:
        pass

# Import PPO regardless of local imports failing
try:
    from stable_baselines3 import PPO
except ImportError:
    print("Warning: stable_baselines3 not found. AI features will not work.")
    PPO = None

PORT = 8081

def get_available_models():
    models = []
    # Check root of phase_3
    for f in os.listdir(current_dir):
        if f.endswith(".zip"):
            models.append(f)
    
    # Check models subdir
    models_dir = os.path.join(current_dir, "models")
    if os.path.exists(models_dir):
        for root, dirs, files in os.walk(models_dir):
            for f in files:
                if f.endswith(".zip"):
                    rel_path = os.path.relpath(os.path.join(root, f), current_dir)
                    models.append(rel_path.replace("\\", "/"))
    return sorted(models)

class SimulationHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/models':
            try:
                models = get_available_models()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(models).encode('utf-8'))
            except Exception as e:
                self.send_error(500, str(e))
        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/simulate':
            self.handle_physics_sim()
        elif self.path == '/simulate_ai':
            self.handle_ai_sim()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_physics_sim(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
            mu = float(data.get('mu', 0.01215))
            state = np.array(data.get('state', [0.83, 0, 0, 0, 0, 0]), dtype=np.float64)
            duration = int(data.get('duration', 1000))
            dt = 0.01
            
            trajectory = []
            curr_state = state.copy()
            
            for i in range(duration):
                step_data = {
                    "t": i * dt,
                    "x": float(curr_state[0]), "y": float(curr_state[1]), "z": float(curr_state[2]),
                    "vx": float(curr_state[3]), "vy": float(curr_state[4]), "vz": float(curr_state[5])
                }
                trajectory.append(step_data)
                curr_state = fast_dynamics.rk4_step(curr_state, dt, mu)
            
            self._send_json(trajectory)
        except Exception as e:
            self._send_error(500, str(e))

    def handle_ai_sim(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
            model_path = data.get('model')
            target_file = os.path.join(current_dir, model_path)
            
            if not os.path.exists(target_file):
                self._send_error(404, f"Model file not found: {model_path}")
                return

            mu = float(data.get('mu', 0.01215))
            initial_state = np.array(data.get('state'), dtype=np.float64)
            duration = int(data.get('duration', 1000))
            num_sims = 20
            
            # Load Model
            model = PPO.load(target_file)
            
            # Create Env (Ensure it matches training config roughly)
            env = SatelliteEnv() 
            env.mu = mu # Override mu if needed, though env usually has fixed mu
            
            best_trajectory = []
            best_reward = -float('inf')
            
            print(f"Running {num_sims} simulations for model: {model_path}")
            
            for sim_idx in range(num_sims):
                # Reset
                obs, _ = env.reset()
                # Manually set state if we want to force the specific initial condition
                # The env.reset() usually randomizes. We want to start from USER defined state?
                # BUT user defined state might be far from what model expects if normalization is used.
                # However, usually we want to see how model performs from THIS state.
                env.state = initial_state.copy()
                env.steps = 0
                
                sim_trajectory = []
                total_reward = 0
                terminated = False
                truncated = False
                
                # Run Episode
                for _ in range(duration):
                    # Record step
                    s = env.state
                    sim_trajectory.append({
                        "x": float(s[0]), "y": float(s[1]), "z": float(s[2]),
                        "vx": float(s[3]), "vy": float(s[4]), "vz": float(s[5])
                    })
                    
                    # Predict Action (Stochastic to get variation)
                    action, _ = model.predict(obs, deterministic=False)
                    
                    # Step
                    obs, reward, terminated, truncated, _ = env.step(action)
                    total_reward += reward
                    
                    if terminated or truncated:
                        break
                
                # Evaluation
                # We prefer longer survival (more steps) and higher reward
                # If all terminated early, pick the one with highest reward?
                # Actually, distance to L1 stability is often better metric but reward should capture it.
                if total_reward > best_reward:
                    best_reward = total_reward
                    best_trajectory = sim_trajectory
            
            print(f"Best Reward: {best_reward:.4f} with {len(best_trajectory)} steps")
            self._send_json(best_trajectory)
            
        except Exception as e:
            print(f"AI Sim Error: {e}")
            self._send_error(500, str(e))

    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_error(self, code, message):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))

if __name__ == "__main__":
    os.chdir(current_dir)
    with socketserver.TCPServer(("", PORT), SimulationHandler) as httpd:
        print(f"Serving at port {PORT}")
        print(f"Open http://localhost:{PORT}/realtime_viewer.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.server_close()
