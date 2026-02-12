
import http.server
import socketserver
import json
import os
import sys
import numpy as np

# Ensure we can import fast_dynamics
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
try:
    import fast_dynamics
except ImportError:
    # If running from project root, phase_3.fast_dynamics might be needed
    # But since we append current_dir (phase_3), import fast_dynamics should work if in same dir
    pass

PORT = 8080

class SimulationHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/simulate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # Extract parameters
                mu = float(data.get('mu', 0.01215))
                state = np.array(data.get('state', [0.83, 0, 0, 0, 0, 0]), dtype=np.float64)
                duration = int(data.get('duration', 1000))
                dt = 0.01
                
                trajectory = []
                
                # Run Simulation
                # Use fast_dynamics if available, else simple fallback (unlikely if setup correctly)
                for i in range(duration):
                    # Save step
                    step_data = {
                        "t": i * dt,
                        "x": float(state[0]),
                        "y": float(state[1]),
                        "z": float(state[2]),
                        "vx": float(state[3]),
                        "vy": float(state[4]),
                        "vz": float(state[5])
                    }
                    trajectory.append(step_data)
                    
                    # Integration Step
                    # state = fast_dynamics.rk4_step(state, dt, mu) 
                    # We need to make sure fast_dynamics is imported correctly.
                    # Assuming it is:
                    state = fast_dynamics.rk4_step(state, dt, mu)

                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(trajectory).encode('utf-8'))
                
            except Exception as e:
                print(f"Simulation Error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self.send_error(404, "File not found")

    def do_GET(self):
        # Serve static files normally
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    # Change into the directory of this script so it serves files from there
    os.chdir(current_dir)
    
    with socketserver.TCPServer(("", PORT), SimulationHandler) as httpd:
        print(f"Serving at port {PORT}")
        print(f"Open http://localhost:{PORT}/realtime_viewer.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.server_close()
