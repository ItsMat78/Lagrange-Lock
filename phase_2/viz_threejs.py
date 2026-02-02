import json
import numpy as np
from fast_dynamics import rk4_step
from utils import get_lagrange_points
import webbrowser
import os

# --- Simulation Config ---
MU = 0.01215
STEPS = 6000  
DT = 0.005    

def get_sim_data():
    """Calculates the physics and returns a list of positions."""
    l1 = get_lagrange_points(MU)['L1']
    state = np.array([l1 - 0.01, 0.0, 0.0, 0.0, 0.1, 0.06], dtype=np.float64)
    trajectory = []
    curr = state.copy()
    for i in range(STEPS):
        trajectory.append(curr[:3].tolist())
        curr = rk4_step(curr, DT, MU)
    return trajectory, MU, l1

def generate_html(trajectory, mu, l1):
    data_json = json.dumps(trajectory)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lagrange Lock - Free Flight</title>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #000; color: white; font-family: sans-serif; user-select: none; }}
        #info {{ position: absolute; top: 10px; left: 10px; z-index: 100; pointer-events: none; }}
        #controls {{ position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 100; 
                     background: rgba(20, 20, 40, 0.8); padding: 10px; border-radius: 8px; display: flex; gap: 10px; align-items: center; pointer-events: auto; }}
        button {{ background: #2a6fdb; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold; }}
        button:hover {{ background: #4a8ffb; }}
        #scrubber {{ width: 300px; cursor: pointer; }}
        .label {{ color: white; font-size: 14px; margin-right: 10px; }}
        .instructions {{ font-size: 12px; color: #aaa; margin-top: 5px; }}
    </style>
    <script type="importmap">
      {{
        "imports": {{
          "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
          "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
        }}
      }}
    </script>
</head>
<body>
    <div id="info">
        <h1>Lagrange Point L1: Halo Orbit</h1>
        <p><b>WASD + Mouse</b> to Fly. <b>Q/E</b> to Roll. Speed varies with scroll.</p>
        <p class="instructions">Current Mode: Free Flight</p>
    </div>
    
    <div id="controls">
        <button id="playPauseBtn">PAUSE</button>
        <input type="range" id="scrubber" min="0" max="{len(trajectory)-1}" value="0">
        <span class="label" id="frameLabel">Step: 0</span>
    </div>

    <script type="module">
        import * as THREE from 'three';
        import {{ FlyControls }} from 'three/addons/controls/FlyControls.js';

        // --- DATA ---
        const trajectory = {data_json};
        const MU = {mu};
        const L1 = {l1};
        const TOTAL_FRAMES = trajectory.length;
        
        let currentFrame = 0;
        let isPlaying = true;
        let playbackSpeed = 2; 

        // --- SCENE ---
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x020205);
        scene.fog = new THREE.FogExp2(0x020205, 0.05);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.001, 1000);
        camera.position.set(L1, -0.2, 0.1);
        camera.lookAt(L1, 0, 0);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // --- CONTROLS (FLY) ---
        const controls = new FlyControls(camera, renderer.domElement);
        controls.movementSpeed = 0.5;
        controls.domElement = renderer.domElement;
        controls.rollSpeed = 0.5;
        controls.autoForward = false;
        controls.dragToLook = true; // Use mouse drag to turn
        
        // --- OBJECTS ---
        // Earth
        const earth = new THREE.Mesh(
            new THREE.SphereGeometry(MU*3, 32, 32), 
            new THREE.MeshLambertMaterial({{ color: 0x2a6fdb }})
        );
        earth.position.set(-MU, 0, 0);
        scene.add(earth);
        
        // Moon
        const moon = new THREE.Mesh(
            new THREE.SphereGeometry(0.01, 32, 32), 
            new THREE.MeshLambertMaterial({{ color: 0x888888 }})
        );
        moon.position.set(1 - MU, 0, 0);
        scene.add(moon);
        
        // L1
        const l1Marker = new THREE.Mesh(
            new THREE.OctahedronGeometry(0.005), 
            new THREE.MeshBasicMaterial({{ color: 0x00ff00, wireframe: true }})
        );
        l1Marker.position.set(L1, 0, 0);
        scene.add(l1Marker);
        
        // Satellite
        const satellite = new THREE.Mesh(
            new THREE.SphereGeometry(0.006, 16, 16), 
            new THREE.MeshBasicMaterial({{ color: 0xffff00 }})
        );
        scene.add(satellite);
        
        // Path
        const points = trajectory.map(p => new THREE.Vector3(p[0], p[1], p[2]));
        const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
        const lineMat = new THREE.LineBasicMaterial({{ color: 0x00ffff, opacity: 0.4, transparent: true }});
        const orbitLine = new THREE.Line(lineGeo, lineMat);
        scene.add(orbitLine);
        
        // Starfield
        const starGeo = new THREE.BufferGeometry();
        const starPos = [];
        for(let i=0; i<3000; i++) {{
            starPos.push((Math.random()-0.5)*20, (Math.random()-0.5)*20, (Math.random()-0.5)*20);
        }}
        starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPos, 3));
        const stars = new THREE.Points(starGeo, new THREE.PointsMaterial({{ color: 0xffffff, size: 0.015, transparent: true, opacity: 0.6 }}));
        scene.add(stars);

        // Lighting
        const sun = new THREE.DirectionalLight(0xffffff, 1.5);
        sun.position.set(-5, 2, 2);
        scene.add(sun);
        scene.add(new THREE.AmbientLight(0x404040));

        // UI
        const scrubber = document.getElementById('scrubber');
        const playBtn = document.getElementById('playPauseBtn');
        const frameLabel = document.getElementById('frameLabel');
        
        playBtn.addEventListener('click', () => {{ isPlaying = !isPlaying; playBtn.innerText = isPlaying ? "PAUSE" : "PLAY"; }});
        scrubber.addEventListener('input', (e) => {{ isPlaying = false; playBtn.innerText = "PLAY"; currentFrame = parseInt(e.target.value); updateSat(currentFrame); }});

        function updateSat(idx) {{
            const p = trajectory[idx];
            satellite.position.set(p[0], p[1], p[2]);
            frameLabel.innerText = "Step: " + idx;
            scrubber.value = idx;
        }}

        // Loop
        const clock = new THREE.Clock();
        function animate() {{
            requestAnimationFrame(animate);
            const delta = clock.getDelta();
            
            controls.update(delta); // Updates the camera fly movement
            
            if(isPlaying) {{
                currentFrame += playbackSpeed;
                if(currentFrame >= TOTAL_FRAMES) currentFrame = 0;
                updateSat(Math.floor(currentFrame));
            }}
            
            renderer.render(scene, camera);
        }}
        animate();
        
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
    """
    
    with open("phase_2/interactive_mission.html", "w") as f:
        f.write(html_content)
    return "phase_2/interactive_mission.html"

if __name__ == "__main__":
    traj, mu, l1 = get_sim_data()
    path = generate_html(traj, mu, l1)
    webbrowser.open('file://' + os.path.realpath(path))
