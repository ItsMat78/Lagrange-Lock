
import json
import numpy as np
import os
import webbrowser

# --- SYSTEM CONFIGS ---
SYSTEMS = {
    "Earth-Moon": { "mu": 0.012, "color_p": 0x2a6fdb, "color_s": 0x888888, "l1": 0.83 },
    "Sun-Jupiter": { "mu": 0.001, "color_p": 0xffcc00, "color_s": 0xd4a076, "l1": 0.93 },
}

def create_realtime_viewer():
    print("Generating Realtime Engine v5 (Surreal)...")
    
    js_content = f"window.SYSTEMS = {json.dumps(SYSTEMS)};"
    with open("phase_2/systems_data.js", "w", encoding='utf-8') as f:
        f.write(js_content)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Phase 2: Environment v5</title>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: 'Consolas', monospace; color: white; user-select: none; }}
        
        #hud {{
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            text-align: center; pointer-events: none;
            background: rgba(0,0,0,0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(4px);
        }}
        
        #controls {{
            position: absolute; top: 20px; right: 20px; width: 220px;
            background: rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.1); padding: 15px;
            display: flex; flex-direction: column; gap: 10px; backdrop-filter: blur(4px);
        }}
        
        select, input, button {{
            background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; padding: 5px; font-family: monospace; font-size: 12px;
        }}
        
        .row {{ display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: #ccc; }}
        .header {{ color: #4a8ffb; font-size: 11px; border-bottom: 1px solid rgba(255,255,255,0.2); margin-top: 5px; padding-bottom: 2px; text-transform: uppercase; }}
        input {{ width: 60px; text-align: right; }}
        
        button {{ margin-top: 10px; background: rgba(42, 111, 219, 0.6); border: none; padding: 8px; cursor: pointer; transition: background 0.2s; }}
        button:hover {{ background: rgba(42, 111, 219, 1.0); }}
        
        .stat {{ color: #4a8ffb; font-weight: bold; }}
        .crash {{ color: #ff3333; font-weight: bold; animation: blink 1s infinite; }}
        @keyframes blink {{ 50% {{ opacity: 0; }} }}
        
        #crash-msg {{ display: none; font-size: 20px; color: red; position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); text-shadow: 0 0 10px red; pointer-events:none; }}
    </style>
    
    <script type="importmap">
      {{ "imports": {{ "three": "https://unpkg.com/three@0.160.0/build/three.module.js" }} }}
    </script>
</head>
<body>
    <div id="crash-msg">IMPACT DETECTED</div>

    <!-- CONTROLS -->
    <div id="controls">
        <div class="header" style="margin-top:0;">System Preset</div>
        <select id="sys-select"></select>
        
        <div class="header">Parameters</div>
        <div class="row" title="Gravity Ratio (μ)"><span>Gravity Ratio (μ)</span> <input id="in-mu" type="number" step="0.001"></div>
        
        <div class="header">Initial Position</div>
        <div class="row"><span>X (Distance)</span> <input id="in-x" type="number" step="0.01"></div>
        <div class="row"><span>Y (Vertical)</span> <input id="in-y" type="number" step="0.01"></div>
        <div class="row"><span>Z (Depth)</span> <input id="in-z" type="number" step="0.01"></div>
        
        <button id="btn-play">PLAY SIMULATION</button>
    </div>

    <!-- HUD -->
    <div id="hud">
        <div>STATUS: <span id="status-val" class="stat">READY</span> | T: <span id="time-val">0.00</span></div>
        <div style="margin-top:5px; font-size:11px; color:#aaa;">
            WASD: Fly Camera | Arrows: Look | Space: Pause
        </div>
    </div>

    <script src="systems_data.js"></script>

    <script type="module">
        import * as THREE from 'three';

        // --- PHYSICS (Unchanged) ---
        class Physics {{
            constructor() {{
                this.mu = 0.012;
                this.state = [0,0,0,0,0,0];
                this.crashed = false;
                this.t = 0;
            }}
            reset(mu, x, y, z) {{
                this.mu = mu;
                this.state = [x, y, z, 0, 0.05, 0.05]; 
                this.crashed = false;
                this.t = 0;
            }}
            step(dt) {{
                if(this.crashed) return;
                const k1 = this.d(this.state);
                const k2 = this.d(this.add(this.state, k1, dt*0.5));
                const k3 = this.d(this.add(this.state, k2, dt*0.5));
                const k4 = this.d(this.add(this.state, k3, dt));
                for(let i=0; i<6; i++) this.state[i] += (dt/6)*(k1[i] + 2*k2[i] + 2*k3[i] + k4[i]);
                this.t += dt;
            }}
            d(s) {{
                const x=s[0], y=s[1], z=s[2], vx=s[3], vy=s[4], vz=s[5];
                const mu = this.mu;
                const r1 = Math.sqrt((x+mu)**2 + y**2 + z**2);
                const r2 = Math.sqrt((x-1+mu)**2 + y**2 + z**2);
                return [vx, vy, vz, 2*vy + x - (1-mu)*(x+mu)/(r1**3) - mu*(x-1+mu)/(r2**3), -2*vx + y - (1-mu)*y/(r1**3) - mu*y/(r2**3), -(1-mu)*z/(r1**3) - mu*z/(r2**3)];
            }}
            add(s, k, h) {{ return s.map((v, i) => v + k[i]*h); }}
        }}

        // --- APP ---
        class App {{
            constructor() {{
                this.phys = new Physics();
                this.running = false;
                this.initViz();
                this.initUI();
                this.loop();
            }}
            
            initUI() {{
                const sel = document.getElementById('sys-select');
                for(let k in window.SYSTEMS) {{
                    let o = document.createElement('option'); o.value=k; o.innerText=k; sel.appendChild(o);
                }}
                this.ui = {{
                    mu: document.getElementById('in-mu'),
                    x: document.getElementById('in-x'), y: document.getElementById('in-y'), z: document.getElementById('in-z'),
                    btn: document.getElementById('btn-play')
                }};
                sel.onchange = () => this.loadPreset(sel.value);
                ['mu','x','y','z'].forEach(k => {{ this.ui[k].addEventListener('input', () => {{ if(!this.running) this.previewState(); }}); }});
                this.ui.btn.onclick = () => {{
                    this.running = !this.running;
                    if(this.phys.crashed && this.running) {{ this.phys.crashed=false; this.previewState(); }}
                    this.updateStatus();
                }};
                this.loadPreset("Earth-Moon");
            }}
            
            loadPreset(name) {{
                const cfg = window.SYSTEMS[name];
                this.ui.mu.value = cfg.mu;
                this.ui.x.value = cfg.l1 - 0.01;
                this.ui.y.value = 0;
                this.ui.z.value = 0;
                this.running = false;
                this.previewState();
                this.updateStatus();
            }}
            
            previewState() {{
                const mu = parseFloat(this.ui.mu.value);
                const x = parseFloat(this.ui.x.value);
                const y = parseFloat(this.ui.y.value);
                const z = parseFloat(this.ui.z.value);
                this.phys.reset(mu, x, y, z);
                this.updateBodies(mu);
                this.sat.position.set(x, y, z);
                this.trailIdx = 0; this.trailPos.fill(0); this.trailGeo.setDrawRange(0, 0);
                document.getElementById('crash-msg').style.display = 'none';
            }}
            
            updateBodies(mu) {{
                const s1 = 1.0; 
                this.p1.scale.setScalar(0.04 * s1); this.p1.position.set(-mu, 0, 0); this.p1.rad = 0.04 * s1;
                const s2 = 0.3;
                this.p2.scale.setScalar(0.04 * s2); this.p2.position.set(1-mu, 0, 0); this.p2.rad = 0.04 * s2;
            }}
            
            updateStatus() {{
                const el = document.getElementById('status-val'); const b = this.ui.btn;
                if(this.phys.crashed) {{ el.innerText="CRASH"; el.className="crash"; b.innerText="RESPAWN"; }}
                else if(this.running) {{ el.innerText="RUNNING"; el.className="stat"; b.innerText="PAUSE"; }}
                else {{ el.innerText="READY / PAUSED"; el.className=""; b.innerText="PLAY"; }}
            }}
            
            checkCrash() {{
                const s = this.phys.state;
                if(this.dist(s, this.p1.position) < this.p1.rad * 0.9) this.crash();
                if(this.dist(s, this.p2.position) < this.p2.rad * 0.9) this.crash();
            }}
            
            crash() {{
                this.phys.crashed = true; this.running = false;
                document.getElementById('crash-msg').style.display='block'; this.updateStatus();
            }}
            
            dist(p1, p2) {{ 
                const x = (Array.isArray(p1) ? p1[0] : p1.x) - p2.x;
                const y = (Array.isArray(p1) ? p1[1] : p1.y) - p2.y;
                const z = (Array.isArray(p1) ? p1[2] : p1.z) - p2.z;
                return Math.sqrt(x*x + y*y + z*z);
            }}

            initViz() {{
                this.scene = new THREE.Scene(); 
                this.scene.background = new THREE.Color(0x050510);
                // SURREAL FOG
                this.scene.fog = new THREE.FogExp2(0x050510, 0.025);
                
                this.camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.001, 1000);
                this.camera.position.set(0.8, -0.4, 0.2);
                this.camera.lookAt(0.8, 0, 0);
                
                this.renderer = new THREE.WebGLRenderer({{ antialias:true }});
                this.renderer.setSize(window.innerWidth, window.innerHeight);
                this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                document.body.appendChild(this.renderer.domElement);
                
                // LIGHTING
                const sun = new THREE.PointLight(0xffffff, 3.0, 100); 
                sun.position.set(-2, 1, 1);
                this.scene.add(sun); 
                this.scene.add(new THREE.AmbientLight(0x404050, 2.0)); // Brighter Ambient
                
                // MATERIALS - SciFi/Surreal
                const matP1 = new THREE.MeshStandardMaterial({{ 
                    color: 0x4a8ffb, roughness: 0.6, metalness: 0.7, emissive: 0x112244, emissiveIntensity: 0.8
                }});
                const matP2 = new THREE.MeshStandardMaterial({{ 
                    color: 0xaaaaaa, roughness: 0.8, metalness: 0.5 
                }});
                
                // Objects
                this.p1 = new THREE.Mesh(new THREE.SphereGeometry(1, 64, 64), matP1);
                this.p2 = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 48), matP2);
                this.sat = new THREE.Mesh(new THREE.SphereGeometry(0.007), new THREE.MeshBasicMaterial({{ color: 0xffff00 }}));
                this.scene.add(this.p1, this.p2, this.sat);
                
                // STARFIELD (Surreal)
                const sGeo = new THREE.BufferGeometry();
                const sPos = [];
                for(let i=0; i<4000; i++) {{
                    sPos.push((Math.random()-0.5)*80, (Math.random()-0.5)*80, (Math.random()-0.5)*80);
                }}
                sGeo.setAttribute('position', new THREE.Float32BufferAttribute(sPos, 3));
                const sMat = new THREE.PointsMaterial({{ 
                    size: 0.04, color: 0xffffff, transparent: true, opacity: 0.8, sizeAttenuation: true 
                }});
                this.scene.add(new THREE.Points(sGeo, sMat));

                // Trail (Brighter)
                this.trailMax = 5000;
                this.trailPos = new Float32Array(this.trailMax*3);
                this.trailGeo = new THREE.BufferGeometry();
                this.trailGeo.setAttribute('position', new THREE.BufferAttribute(this.trailPos, 3));
                this.scene.add(new THREE.Line(this.trailGeo, new THREE.LineBasicMaterial({{ color: 0x00ffff, opacity: 0.8, transparent: true }})));
                
                // Input
                this.keys = {{}};
                window.addEventListener('keydown', e => {{
                    this.keys[e.key] = true;
                    if(e.code === 'Space') this.ui.btn.click();
                }});
                window.addEventListener('keyup', e => this.keys[e.key] = false);
            }}
            
            loop() {{
                requestAnimationFrame(() => this.loop());
                if(this.running) {{
                    for(let i=0; i<10; i++) this.phys.step(0.0005);
                    this.checkCrash();
                    const s = this.phys.state;
                    this.sat.position.set(s[0], s[1], s[2]);
                    this.trailPos[this.trailIdx*3] = s[0];
                    this.trailPos[this.trailIdx*3+1] = s[1];
                    this.trailPos[this.trailIdx*3+2] = s[2];
                    this.trailIdx = (this.trailIdx+1) % this.trailMax;
                    this.trailGeo.attributes.position.needsUpdate = true;
                    this.trailGeo.setDrawRange(0, this.trailMax);
                    document.getElementById('time-val').innerText = this.phys.t.toFixed(2);
                }}
                const sp = 0.01;
                if(this.keys['w']) this.camera.translateZ(-sp);
                if(this.keys['s']) this.camera.translateZ(sp);
                if(this.keys['a']) this.camera.translateX(-sp);
                if(this.keys['d']) this.camera.translateX(sp);
                if(this.keys['ArrowUp']) this.camera.rotateX(0.02);
                if(this.keys['ArrowDown']) this.camera.rotateX(-0.02);
                if(this.keys['ArrowLeft']) this.camera.rotateY(0.02);
                if(this.keys['ArrowRight']) this.camera.rotateY(-0.02);
                this.renderer.render(this.scene, this.camera);
            }}
        }}
        new App();
    </script>
</body>
</html>
    """
    
    path = "phase_2/realtime_viewer.html"
    with open(path, "w", encoding='utf-8') as f:
        f.write(html_content)
    print(f"Created Engine V5 (Surreal): {path}")
    return path

if __name__ == "__main__":
    path = create_realtime_viewer()
    webbrowser.open('file://' + os.path.realpath(path))
