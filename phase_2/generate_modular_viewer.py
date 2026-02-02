
import json
import numpy as np
import math
from fast_dynamics import rk4_step
from utils import get_lagrange_points
import os
import webbrowser

# --- CONFIGURATION ---
SYSTEM_CONFIG = {
    "Earth-Moon": {
        "mu": 0.01215,
        "color_p": 0x2a6fdb, 
        "color_s": 0x888888, 
        "scale_p": 1.0, 
        "scale_s": 0.27
    }
}

def generate_trajectory(mu, steps=6000, dt=0.005):
    l_points = get_lagrange_points(mu)
    l1 = l_points['L1']
    x0 = l1 - 0.01
    state = np.array([x0, 0.0, 0.0, 0.0, 0.1, 0.06], dtype=np.float64)
    
    trajectory = []
    curr = state.copy()
    
    for _ in range(steps):
        pos = [round(float(x), 5) for x in curr[:3]]
        trajectory.append(pos) 
        curr = rk4_step(curr, dt, mu)
        
    return trajectory, float(l1)

def create_viewer():
    print("Generating Simulation Data...")
    sys_name = "Earth-Moon"
    params = SYSTEM_CONFIG[sys_name]
    traj, l1 = generate_trajectory(params['mu'])
    
    sim_data = {
        "system": sys_name,
        "mu": params['mu'],
        "l1": l1,
        "trajectory": traj,
        "config": params
    }
    
    json_str = json.dumps(sim_data, allow_nan=False)
    js_content = f"window.SIM_DATA = {json_str};"
    
    with open("phase_2/mission_data.js", "w", encoding='utf-8') as f:
        f.write(js_content)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lagrange Lock: Minimal</title>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: 'Consolas', 'Courier New', monospace; color: white; }}
        
        /* MINIMAL HUD (Bottom Center) */
        #hud {{
            position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
            text-align: center; pointer-events: none;
            text-shadow: 0 2px 4px rgba(0,0,0,0.8);
        }}
        
        .stat-row {{ font-size: 14px; margin-bottom: 5px; color: #4a8ffb; letter-spacing: 1px; }}
        .hint-row {{ font-size: 11px; color: #666; margin-top: 10px; }}
        
        #loading {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; align-items: center; justify-content: center;
            background: #020205; z-index: 100;
        }}
        
        canvas {{ outline: none; }}
    </style>
    
    <script type="importmap">
      {{ "imports": {{ "three": "https://unpkg.com/three@0.160.0/build/three.module.js" }} }}
    </script>
</head>
<body>
    <div id="loading">SYSTEM INITIALIZING...</div>

    <div id="hud">
        <div class="stat-row">
            <span id="status">PAUSED</span> | T: <span id="time">0</span>
        </div>
        <div class="stat-row" style="color: #ccc; font-size: 12px;">
            POS: <span id="pos">0.00, 0.00, 0.00</span>
        </div>
        <div class="hint-row">
            WASD: Move | ARROWS: Look | Q/E: Roll | SPACE: Play/Pause
        </div>
    </div>

    <!-- DATA -->
    <script src="mission_data.js"></script>

    <script type="module">
        import * as THREE from 'three';

        class App {{
            constructor() {{
                this.initThree();
                this.initObjects();
                this.initInput();
                
                this.isPlaying = false;
                this.step = 0;
                this.speed = 1; // Steps per frame
                
                document.getElementById('loading').remove();
                this.animate();
            }}
            
            initThree() {{
                this.scene = new THREE.Scene();
                this.scene.background = new THREE.Color(0x020205);
                this.scene.fog = new THREE.FogExp2(0x020205, 0.02);
                
                this.camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.001, 1000);
                this.renderer = new THREE.WebGLRenderer({{ antialias: true }});
                this.renderer.setSize(window.innerWidth, window.innerHeight);
                document.body.appendChild(this.renderer.domElement);
                
                this.clock = new THREE.Clock();
                
                // Focus for keys
                this.renderer.domElement.tabIndex = 1;
                this.renderer.domElement.focus();
                this.renderer.domElement.onclick = () => this.renderer.domElement.focus();
                
                window.addEventListener('resize', () => {{
                    this.camera.aspect = window.innerWidth/window.innerHeight;
                    this.camera.updateProjectionMatrix();
                    this.renderer.setSize(window.innerWidth, window.innerHeight);
                }});
            }}
            
            initObjects() {{
                const d = window.SIM_DATA;
                
                // Light
                const sun = new THREE.PointLight(0xffffff, 2, 100);
                sun.position.set(-2, 1, 1);
                this.scene.add(sun);
                this.scene.add(new THREE.AmbientLight(0x202020));
                
                // Bodies
                const p1 = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 48), new THREE.MeshStandardMaterial({{ color: d.config.color_p }}));
                p1.position.set(-d.mu, 0, 0);
                p1.scale.setScalar(0.04 * d.config.scale_p);
                this.scene.add(p1);
                
                const p2 = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 32), new THREE.MeshStandardMaterial({{ color: d.config.color_s }}));
                p2.position.set(1 - d.mu, 0, 0);
                p2.scale.setScalar(0.04 * d.config.scale_s);
                this.scene.add(p2);
                
                // Satellite
                this.sat = new THREE.Mesh(new THREE.SphereGeometry(0.008), new THREE.MeshBasicMaterial({{ color: 0xffff00 }}));
                this.scene.add(this.sat);
                
                // Orbit Points
                if(d.trajectory) {{
                    const pts = d.trajectory.map(p => new THREE.Vector3(p[0], p[1], p[2]));
                    const geo = new THREE.BufferGeometry().setFromPoints(pts);
                    const line = new THREE.Line(geo, new THREE.LineBasicMaterial({{ color: 0x00ffff, opacity: 0.3, transparent: true }}));
                    this.scene.add(line);
                    
                    // Init Sat Pos
                    this.sat.position.copy(pts[0]);
                }}
                
                // Stars
                const sGeo = new THREE.BufferGeometry();
                const sPos = [];
                for(let i=0; i<5000; i++) sPos.push((Math.random()-0.5)*100, (Math.random()-0.5)*100, (Math.random()-0.5)*100);
                sGeo.setAttribute('position', new THREE.Float32BufferAttribute(sPos, 3));
                this.scene.add(new THREE.Points(sGeo, new THREE.PointsMaterial({{ size: 0.04, opacity: 0.4 }})));
                
                // Cam Start
                this.camera.position.set(d.l1, -0.2, 0.1);
                this.camera.lookAt(d.l1, 0, 0);
            }}
            
            initInput() {{
                this.keys = {{}};
                window.addEventListener('keydown', e => {{
                    this.keys[e.code] = true;
                    if(e.code === 'Space') {{
                        this.isPlaying = !this.isPlaying;
                        document.getElementById('status').innerText = this.isPlaying ? "RUNNING" : "PAUSED";
                    }}
                }});
                window.addEventListener('keyup', e => this.keys[e.code] = false);
            }}
            
            updateCam(dt) {{
                const moveSpeed = 0.5 * dt;
                const turnSpeed = 1.5 * dt;
                
                // 1. WASD Movement (Relative to Camera)
                if(this.keys['KeyW']) this.camera.translateZ(-moveSpeed);
                if(this.keys['KeyS']) this.camera.translateZ(moveSpeed);
                if(this.keys['KeyA']) this.camera.translateX(-moveSpeed);
                if(this.keys['KeyD']) this.camera.translateX(moveSpeed);
                
                // 2. Arrow Keys Look (Pitch/Yaw)
                if(this.keys['ArrowUp'])    this.camera.rotateX(turnSpeed);
                if(this.keys['ArrowDown'])  this.camera.rotateX(-turnSpeed); 
                if(this.keys['ArrowLeft'])  this.camera.rotateY(turnSpeed);
                if(this.keys['ArrowRight']) this.camera.rotateY(-turnSpeed);
                
                // 3. Q/E Roll
                if(this.keys['KeyQ']) this.camera.rotateZ(turnSpeed);
                if(this.keys['KeyE']) this.camera.rotateZ(-turnSpeed);
                
                // Update HUD Pos
                const cp = this.camera.position;
                document.getElementById('pos').innerText = `${{cp.x.toFixed(2)}}, ${{cp.y.toFixed(2)}}, ${{cp.z.toFixed(2)}}`;
            }}
            
            updateSat() {{
                if(!this.isPlaying) return;
                
                const traj = window.SIM_DATA.trajectory;
                this.step += this.speed;
                
                if(this.step >= traj.length) this.step = 0; // Loop
                
                const idx = Math.floor(this.step);
                const pos = traj[idx];
                if(pos) {{
                    this.sat.position.set(pos[0], pos[1], pos[2]);
                    document.getElementById('time').innerText = idx;
                }}
            }}

            animate() {{
                requestAnimationFrame(() => this.animate());
                const dt = this.clock.getDelta();
                
                this.updateCam(dt);
                this.updateSat();
                
                this.renderer.render(this.scene, this.camera);
            }}
        }}
        
        new App();
    </script>
</body>
</html>
    """
    
    path = "phase_2/modular_viewer.html"
    with open(path, "w", encoding='utf-8') as f:
        f.write(html_content)
    print(f"Created Minimal Viewer: {path}")
    return path

if __name__ == "__main__":
    path = create_viewer()
    webbrowser.open('file://' + os.path.realpath(path))
