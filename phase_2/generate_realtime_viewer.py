
import json
import numpy as np
import os
import webbrowser

# --- SYSTEM CONFIGS ---
SYSTEMS = {
    "Earth-Moon": { "mu": 0.01215, "color_p": 0x2a6fdb, "color_s": 0x888888, "scale_p": 1.0, "scale_s": 0.27, "l1": 0.836915 },
    "Sun-Jupiter": { "mu": 0.0009537, "color_p": 0xffcc00, "color_s": 0xd4a076, "scale_p": 4.0, "scale_s": 0.4, "l1": 0.9323 }, # Approx
    "Binary Stars": { "mu": 0.5, "color_p": 0xff4400, "color_s": 0x0044ff, "scale_p": 1.5, "scale_s": 1.5, "l1": 0.0 }
}

def create_realtime_viewer():
    print("Generating Realtime Engine...")
    
    # Store configs in a JS file
    js_content = f"window.SYSTEMS = {json.dumps(SYSTEMS)};"
    with open("phase_2/systems_data.js", "w", encoding='utf-8') as f:
        f.write(js_content)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lagrange Lock: Realtime</title>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: 'Consolas', monospace; color: white; }}
        
        #hud {{
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            text-align: center; pointer-events: none;
            background: rgba(0,0,0,0.5); padding: 10px 20px; border-radius: 8px;
        }}
        
        #system-selector {{
            position: absolute; top: 20px; right: 20px;
            background: rgba(0,0,0,0.8); border: 1px solid #444; color: white;
            padding: 5px; font-family: monospace; cursor: pointer;
        }}
        
        .stat {{ color: #4a8ffb; }}
        .hint {{ font-size: 11px; color: #888; margin-top: 5px; }}
        
        canvas {{ display: block; }}
    </style>
    
    <script type="importmap">
      {{ "imports": {{ "three": "https://unpkg.com/three@0.160.0/build/three.module.js" }} }}
    </script>
</head>
<body>
    <select id="system-selector"></select>

    <div id="hud">
        <div>
            M: <span id="mu-val" class="stat">0.00</span> | 
            POS: <span id="pos-val" class="stat">0,0,0</span>
        </div>
        <div style="font-size: 12px; margin-top: 4px; color: #aaa;">
            SIM TIME: <span id="sim-time">0.00</span>
        </div>
        <div class="hint">WASD: Camera | Arrow: Look | Space: Pause</div>
    </div>

    <script src="systems_data.js"></script>

    <script type="module">
        import * as THREE from 'three';

        // --- REALTIME PHYSICS ENGINE (CR3BP) ---
        class PhysicsEngine {{
            constructor() {{
                this.mu = 0.01215;
                // State: x, y, z, vx, vy, vz
                this.state = [0.82, 0, 0, 0, 0, 0]; 
            }}
            
            setSystem(mu, l1) {{
                this.mu = mu;
                // Reset to an approximate halo orbit condition near L1
                this.state = [l1 - 0.01, 0, 0, 0, 0.01, 0.05]; 
            }}

            // RK4 Integrator
            step(dt) {{
                const k1 = this.derivatives(this.state);
                const k2 = this.derivatives(this.add(this.state, this.mul(k1, dt*0.5)));
                const k3 = this.derivatives(this.add(this.state, this.mul(k2, dt*0.5)));
                const k4 = this.derivatives(this.add(this.state, this.mul(k3, dt)));
                
                // s = s + (dt/6)*(k1 + 2k2 + 2k3 + k4)
                for(let i=0; i<6; i++) {{
                    this.state[i] += (dt/6.0) * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i]);
                }}
            }}
            
            derivatives(s) {{
                const x=s[0], y=s[1], z=s[2], vx=s[3], vy=s[4], vz=s[5];
                const mu = this.mu;
                
                const r1 = Math.sqrt( (x+mu)*(x+mu) + y*y + z*z );
                const r2 = Math.sqrt( (x-1+mu)*(x-1+mu) + y*y + z*z );
                
                const r1_3 = r1*r1*r1;
                const r2_3 = r2*r2*r2;
                
                const ax = 2*vy + x - (1-mu)*(x+mu)/r1_3 - mu*(x-1+mu)/r2_3;
                const ay = -2*vx + y - (1-mu)*y/r1_3 - mu*y/r2_3;
                const az = -(1-mu)*z/r1_3 - mu*z/r2_3;
                
                return [vx, vy, vz, ax, ay, az];
            }}
            
            // Vector helpers
            add(a, b) {{ return a.map((v, i) => v + b[i]); }}
            mul(a, s) {{ return a.map(v => v * s); }}
        }}

        // --- APP ---
        class App {{
            constructor() {{
                this.physics = new PhysicsEngine();
                this.simTime = 0;
                this.isPaused = false;
                
                this.initThree();
                this.initScene();
                this.initUI();
                
                // Boot first system
                this.loadSystem("Earth-Moon");
                
                this.animate();
            }}
            
            initThree() {{
                this.scene = new THREE.Scene();
                this.scene.background = new THREE.Color(0x020205);
                this.camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.001, 1000);
                this.renderer = new THREE.WebGLRenderer({{ antialias: true }});
                this.renderer.setSize(window.innerWidth, window.innerHeight);
                document.body.appendChild(this.renderer.domElement);
                
                this.clock = new THREE.Clock();
                this.keys = {{}};
                
                window.addEventListener('keydown', e => {{
                    this.keys[e.code] = true;
                    if(e.code === 'Space') this.isPaused = !this.isPaused;
                }});
                window.addEventListener('keyup', e => this.keys[e.code] = false);
            }}
            
            initScene() {{
                // Shared Objects
                const geo = new THREE.SphereGeometry(1, 32, 32);
                this.p1 = new THREE.Mesh(geo, new THREE.MeshBasicMaterial());
                this.p2 = new THREE.Mesh(geo, new THREE.MeshBasicMaterial());
                this.scene.add(this.p1);
                this.scene.add(this.p2);
                
                this.sat = new THREE.Mesh(new THREE.SphereGeometry(0.01), new THREE.MeshBasicMaterial({{ color:0xffff00 }}));
                this.scene.add(this.sat);
                
                // Trail
                this.trailMax = 10000;
                this.trailPositions = new Float32Array(this.trailMax * 3);
                this.trailGeo = new THREE.BufferGeometry();
                this.trailGeo.setAttribute('position', new THREE.BufferAttribute(this.trailPositions, 3));
                this.trailIdx = 0;
                this.scene.add(new THREE.Line(this.trailGeo, new THREE.LineBasicMaterial({{ color: 0x00ffff, opacity: 0.5 }})));
                
                // Stars
                const sGeo = new THREE.BufferGeometry();
                const sPos = [];
                for(let i=0; i<1000; i++) sPos.push((Math.random()-0.5)*100, (Math.random()-0.5)*100, (Math.random()-0.5)*100);
                sGeo.setAttribute('position', new THREE.Float32BufferAttribute(sPos, 3));
                this.scene.add(new THREE.Points(sGeo, new THREE.PointsMaterial({{ size: 0.1, opacity: 0.5 }})));
            }}
            
            initUI() {{
                const sel = document.getElementById('system-selector');
                for(let k in window.SYSTEMS) {{
                    const opt = document.createElement('option');
                    opt.value = k;
                    opt.innerText = k;
                    sel.appendChild(opt);
                }}
                sel.onchange = (e) => this.loadSystem(e.target.value);
            }}
            
            loadSystem(name) {{
                const cfg = window.SYSTEMS[name];
                this.physics.setSystem(cfg.mu, cfg.l1);
                
                this.p1.material.color.setHex(cfg.color_p);
                this.p1.scale.setScalar(0.04 * cfg.scale_p);
                this.p1.position.set(-cfg.mu, 0, 0);
                
                this.p2.material.color.setHex(cfg.color_s);
                this.p2.scale.setScalar(0.04 * cfg.scale_s);
                this.p2.position.set(1 - cfg.mu, 0, 0);
                
                // Reset View
                this.camera.position.set(cfg.l1, -0.3, 0.2);
                this.camera.lookAt(cfg.l1, 0, 0);
                
                // Reset Trail
                this.trailIdx = 0;
                this.trailPositions.fill(0);
                this.simTime = 0;
                
                document.getElementById('mu-val').innerText = cfg.mu;
            }}
            
            updatePhysics(dt) {{
                if(this.isPaused) return;
                
                // Run Physics Steps (Sub-steps for stability)
                const simDt = 0.001; // Tiny steps
                const steps = 5; 
                
                for(let i=0; i<steps; i++) {{
                    this.physics.step(simDt);
                    this.simTime += simDt;
                }}
                
                const s = this.physics.state;
                this.sat.position.set(s[0], s[1], s[2]);
                
                // Update Trail
                this.trailPositions[this.trailIdx*3] = s[0];
                this.trailPositions[this.trailIdx*3+1] = s[1];
                this.trailPositions[this.trailIdx*3+2] = s[2];
                this.trailIdx = (this.trailIdx + 1) % this.trailMax;
                this.trailGeo.attributes.position.needsUpdate = true;
                this.trailGeo.setDrawRange(0, this.trailMax);
                
                document.getElementById('sim-time').innerText = this.simTime.toFixed(2);
            }}
            
            updateCamera(dt) {{
                const speed = 1.0 * dt; // Movement speed
                const turn = 2.0 * dt;  // Turn speed
                
                if(this.keys['KeyW']) this.camera.translateZ(-speed);
                if(this.keys['KeyS']) this.camera.translateZ(speed);
                if(this.keys['KeyA']) this.camera.translateX(-speed);
                if(this.keys['KeyD']) this.camera.translateX(speed);
                
                if(this.keys['ArrowUp']) this.camera.rotateX(turn);
                if(this.keys['ArrowDown']) this.camera.rotateX(-turn);
                if(this.keys['ArrowLeft']) this.camera.rotateY(turn);
                if(this.keys['ArrowRight']) this.camera.rotateY(-turn);
                
                if(this.keys['KeyQ']) this.camera.rotateZ(turn);
                if(this.keys['KeyE']) this.camera.rotateZ(-turn);
                
                const p = this.camera.position;
                document.getElementById('pos-val').innerText = `${{p.x.toFixed(2)}}, ${{p.y.toFixed(2)}}`;
            }}

            animate() {{
                requestAnimationFrame(() => this.animate());
                const dt = this.clock.getDelta();
                
                this.updatePhysics(dt);
                this.updateCamera(dt);
                
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
    print(f"Created Realtime Engine: {path}")
    return path

if __name__ == "__main__":
    path = create_realtime_viewer()
    webbrowser.open('file://' + os.path.realpath(path))
