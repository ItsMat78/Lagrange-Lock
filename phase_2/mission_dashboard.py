
import json
import numpy as np
import math
from fast_dynamics import rk4_step
from utils import get_lagrange_points
import webbrowser
import os

STEPS = 8000
DT = 0.005

SYSTEMS = {
    "Earth-Moon": { "mu": 0.01215, "color_p": 0x2a6fdb, "color_s": 0x888888, "scale_p": 1.0, "scale_s": 0.27 },
    "Sun-Jupiter": { "mu": 0.0009537, "color_p": 0xffcc00, "color_s": 0xd4a076, "scale_p": 4.0, "scale_s": 0.4 },
    "Binary Stars": { "mu": 0.5, "color_p": 0xff4400, "color_s": 0x0044ff, "scale_p": 1.5, "scale_s": 1.5 }
}

def clean_float(val):
    if math.isnan(val) or math.isinf(val): return None
    return val

def generate_trajectory(mu):
    l_points = get_lagrange_points(mu)
    l1 = l_points['L1']
    dist = abs(l1 - (1-mu))
    offset = dist * 0.1 
    x0 = l1 - offset
    vy0 = 0.1 * (1 - mu)
    state = np.array([x0, 0.0, 0.0, 0.0, vy0, 0.06], dtype=np.float64)
    traj = []
    curr = state.copy()
    for i in range(STEPS):
        pos = [clean_float(x) for x in curr[:3]]
        if None in pos: break
        traj.append(pos)
        curr = rk4_step(curr, DT, mu)
    return traj, clean_float(l1)

def build_dashboard():
    print("Computing trajectories...")
    data_bundle = {}
    for name, params in SYSTEMS.items():
        traj, l1 = generate_trajectory(params['mu'])
        data_bundle[name] = { "mu": params['mu'], "l1": l1, "trajectory": traj, "config": params }
    
    json_data = json.dumps(data_bundle)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Universal CR3BP Dashboard v3</title>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #020205; color: white; font-family: 'Segoe UI', sans-serif; }}
        #container {{ position: relative; width: 100vw; height: 100vh; }}
        canvas {{ display: block; width: 100%; height: 100%; outline: none; }}

        /* --- UI DESIGN v3: BOTTOM BAR --- */
        #bottom-bar {{
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 10px; align-items: center;
            background: rgba(15, 15, 30, 0.9);
            padding: 10px 15px; border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            z-index: 100;
        }}
        
        .divider {{ width: 1px; height: 30px; background: rgba(255,255,255,0.2); margin: 0 10px; }}
        
        select {{ background: #222; color: #fff; border: 1px solid #444; padding: 5px 10px; border-radius: 4px; }}
        
        button {{
            background: rgba(255,255,255,0.1); border: none; color: white;
            padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 13px;
        }}
        button:hover {{ background: rgba(255,255,255,0.2); }}
        button.active {{ background: #2a6fdb; color: white; }}
        
        /* Scrubber */
        .scrubber-group {{ display: flex; align-items: center; gap: 10px; }}
        input[type=range] {{ width: 150px; cursor: pointer; }}
        
        /* INFO OVERLAY (Top Left - Minimal) */
        #top-overlay {{
            position: absolute; top: 20px; left: 20px; pointer-events: none;
        }}
        h1 {{ margin: 0; font-size: 20px; font-weight: 300; color: rgba(255,255,255,0.9); }}
        .subtext {{ font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 4px; }}
        
        #error-msg {{ position: fixed; top: 10px; right: 10px; color: #ff5555; font-weight: bold; }}
    </style>
    <script type="importmap">
      {{ "imports": {{ 
          "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
          "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/" 
      }} }}
    </script>
</head>
<body>
    <div id="container">
        <div id="error-msg"></div>

        <!-- TOP INFO -->
        <div id="top-overlay">
            <h1>LAGRANGE LOCK <span style="font-size: 12px; opacity:0.5; vertical-align: middle;"> MISSION CONTROL</span></h1>
            <div id="data-display" class="subtext">Earth-Moon System | L1 Halo Orbit</div>
        </div>
        
        <!-- BOTTOM BAR -->
        <div id="bottom-bar">
            <!-- Systems -->
            <select id="systemSelect"></select>
            
            <div class="divider"></div>
            
            <!-- Camera -->
            <div style="display:flex; gap:5px;">
                <button id="camOrbitBtn" class="active">Orbit</button>
                <button id="camFreeBtn">Free Flight</button>
            </div>
            
            <div class="divider"></div>
            
            <!-- Playback -->
            <div class="scrubber-group">
                <button id="playPauseBtn">PAUSE</button>
                <input type="range" id="scrubber" min="0" max="100" value="0">
                <span id="stepLabel" style="font-family: monospace; width: 50px;">T=0</span>
            </div>
        </div>
    </div>

    <script type="module">
        import * as THREE from 'three';
        import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
        import {{ FlyControls }} from 'three/addons/controls/FlyControls.js';

        const ALL_DATA = {json_data};
        let currentSystemName = Object.keys(ALL_DATA)[0];
        let currentData = ALL_DATA[currentSystemName];
        let frame = 0, isPlaying = true, camMode = 'orbit';

        // SETUP
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x020205);
        scene.fog = new THREE.FogExp2(0x020205, 0.02);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('container').appendChild(renderer.domElement);
        
        // FOCUS FIXES
        renderer.domElement.tabIndex = 1;
        renderer.domElement.style.outline = 'none';
        renderer.domElement.focus();
        document.body.onclick = () => renderer.domElement.focus();

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.001, 1000);
        
        // CAMERAS
        const orbitControls = new OrbitControls(camera, renderer.domElement);
        orbitControls.enableDamping = true;
        orbitControls.dampingFactor = 0.1;
        
        const flyControls = new FlyControls(camera, renderer.domElement);
        flyControls.movementSpeed = 0.2; // Slower for precision
        flyControls.rollSpeed = 0.3; // Slower roll
        flyControls.dragToLook = true; 
        flyControls.enabled = false;

        // OBJECTS
        const primary = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 32), new THREE.MeshStandardMaterial({{ emissive: 0x111111 }}));
        scene.add(primary);
        const secondary = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 32), new THREE.MeshStandardMaterial());
        scene.add(secondary);
        const satellite = new THREE.Mesh(new THREE.SphereGeometry(0.008, 16, 16), new THREE.MeshBasicMaterial({{ color: 0xffff00 }}));
        scene.add(satellite);
        const l1Marker = new THREE.Mesh(new THREE.OctahedronGeometry(0.01), new THREE.MeshBasicMaterial({{ color: 0x00ff00, wireframe: true }}));
        scene.add(l1Marker);
        const orbitLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({{ color: 0x00ffff, opacity: 0.5, transparent: true }}));
        scene.add(orbitLine);
        
        // ENV
        const starsGeo = new THREE.BufferGeometry();
        const starPos = [];
        for(let i=0; i<3000; i++) starPos.push((Math.random()-0.5)*30, (Math.random()-0.5)*30, (Math.random()-0.5)*30);
        starsGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPos, 3));
        scene.add(new THREE.Points(starsGeo, new THREE.PointsMaterial({{ size: 0.02, opacity: 0.5 }})));
        const sunLight = new THREE.PointLight(0xffffff, 2, 100);
        scene.add(sunLight);
        scene.add(new THREE.AmbientLight(0x404040));

        // LOGIC
        function loadSystem(name) {{
            currentSystemName = name;
            currentData = ALL_DATA[name];
            const cfg = currentData.config;
            
            document.getElementById('data-display').innerText = `${{name}} | MU: ${{currentData.mu}} | L1: ${{currentData.l1.toFixed(3)}}`;
            
            primary.position.set(-currentData.mu, 0, 0);
            primary.scale.setScalar(0.04 * cfg.scale_p);
            primary.material.color.setHex(cfg.color_p);
            primary.material.emissive.setHex(cfg.color_p);
            
            secondary.position.set(1 - currentData.mu, 0, 0);
            secondary.scale.setScalar(0.04 * cfg.scale_s);
            secondary.material.color.setHex(cfg.color_s);
            
            l1Marker.position.set(currentData.l1, 0, 0);
            sunLight.position.copy(name.includes("Sun") ? primary.position : new THREE.Vector3(-5, 2, 2));

            const points = currentData.trajectory.filter(p=>p).map(p => new THREE.Vector3(p[0], p[1], p[2]));
            orbitLine.geometry.setFromPoints(points);
            
            frame = 0;
            document.getElementById('scrubber').max = points.length - 1;
            
            // Reset Cam
            if(camMode !== 'free') {{
                camera.position.set(currentData.l1, -0.4, 0.2);
                orbitControls.target.set(currentData.l1, 0, 0);
            }}
        }}

        function setupUI() {{
             const sel = document.getElementById('systemSelect');
             for(let k in ALL_DATA) {{
                 let opt = document.createElement('option');
                 opt.value = k; opt.innerText = k;
                 sel.appendChild(opt);
             }}
             sel.onchange = e => loadSystem(e.target.value);
             
             const setMode = (m) => {{
                 camMode = m;
                 orbitControls.enabled = (m==='orbit');
                 flyControls.enabled = (m==='free');
                 
                 document.getElementById('camOrbitBtn').classList.toggle('active', m==='orbit');
                 document.getElementById('camFreeBtn').classList.toggle('active', m==='free');
                 
                 if(m==='orbit') orbitControls.reset();
             }};
             
             document.getElementById('camOrbitBtn').onclick = () => setMode('orbit');
             document.getElementById('camFreeBtn').onclick = () => setMode('free');
             
             const btn = document.getElementById('playPauseBtn');
             btn.onclick = () => {{ isPlaying = !isPlaying; btn.innerText = isPlaying ? "PAUSE" : "PLAY"; }};
             
             document.getElementById('scrubber').oninput = e => {{
                 isPlaying = false; btn.innerText = "PLAY";
                 frame = parseInt(e.target.value);
             }};
        }}

        const clock = new THREE.Clock();
        function animate() {{
            requestAnimationFrame(animate);
            const dt = clock.getDelta();
            
            if(isPlaying && currentData.trajectory) {{
                frame += 2;
                if(frame >= currentData.trajectory.length) frame = 0;
                document.getElementById('scrubber').value = frame;
                document.getElementById('stepLabel').innerText = "T=" + frame;
            }}
            if(currentData.trajectory) {{
                const pos = currentData.trajectory[Math.floor(frame)];
                if(pos) satellite.position.set(pos[0], pos[1], pos[2]);
            }}

            orbitControls.update();
            if(camMode === 'free') flyControls.update(dt);
            renderer.render(scene, camera);
        }}

        setupUI();
        loadSystem(currentSystemName);
        animate();
        
        window.onresize = () => {{
            camera.aspect = window.innerWidth/window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }};
    </script>
</body>
</html>
    """
    path = "phase_2/mission_dashboard.html"
    with open(path, "w") as f:
        f.write(html_content)
    print(f"Created Dashboard v3: {path}")
    return path

if __name__ == "__main__":
    path = build_dashboard()
    webbrowser.open('file://' + os.path.realpath(path))
