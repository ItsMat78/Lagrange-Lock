import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import CheckButtons
from scipy.optimize import newton

# --- 1. CONFIGURATION ---
mu = 0.01215
resolution = 100   
zoom = 1.5
z_min, z_max = -2.5, -1.4
z_offset = 0.02  # FIX: Lift points slightly above surface so they are always visible

ANGLE_STEP = 1  
FRAME_DELAY = 30 

# --- 2. CALCULATE MATH ---
def eq_L1(x): return x - (1-mu)/(x+mu)**2 + mu/(x-(1-mu))**2
def eq_L2(x): return x - (1-mu)/(x+mu)**2 - mu/(x-(1-mu))**2
def eq_L3(x): return x + (1-mu)/(x+mu)**2 + mu/(x-(1-mu))**2

l1 = newton(eq_L1, 0.8)
l2 = newton(eq_L2, 1.2)
l3 = newton(eq_L3, -1.0)
l4_x, l4_y = 0.5 - mu, np.sqrt(3)/2
l5_x, l5_y = 0.5 - mu, -np.sqrt(3)/2

def get_potential_value(x, y):
    r1 = np.sqrt((x + mu)**2 + y**2)
    r2 = np.sqrt((x - (1-mu))**2 + y**2)
    return -((1-mu)/r1) - (mu/r2) - 0.5 * (x**2 + y**2)

# Calculate exact Z-heights
z_vals = [
    z_min, z_min, # Earth, Moon (Floored)
    get_potential_value(l1, 0),
    get_potential_value(l2, 0),
    get_potential_value(l3, 0),
    get_potential_value(l4_x, l4_y),
    get_potential_value(l5_x, l5_y)
]

# Dictionary to store everything for easy access
# Format: 'Name': [x, y, z, color, marker, size]
objects_data = {
    'Earth': [-mu, 0, z_vals[0], 'blue', 'o', 150],
    'Moon':  [1-mu, 0, z_vals[1], 'grey', 'o', 60],
    'L1':    [l1, 0, z_vals[2] + z_offset, 'lime', 'X', 100],      # Added offset
    'L2':    [l2, 0, z_vals[3] + z_offset, 'lime', 'X', 100],
    'L3':    [l3, 0, z_vals[4] + z_offset, 'lime', 'X', 100],
    'L4':    [l4_x, l4_y, z_vals[5] + z_offset, 'cyan', 'D', 60],  # Cyan Diamond
    'L5':    [l5_x, l5_y, z_vals[6] + z_offset, 'cyan', 'D', 60]
}

# --- 3. PLOT SETUP ---
fig = plt.figure(figsize=(14, 9))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(left=0.0, right=0.80) # More room on right for long menu

ax.set_title(f"3D Topology (Granular Controls)")
ax.set_xlabel("X Axis")
ax.set_ylabel("Y Axis")
ax.set_zlabel("Potential Energy")
ax.set_xlim(-zoom, zoom)
ax.set_ylim(-zoom, zoom)
ax.set_zlim(z_min, z_max)
ax.view_init(elev=55, azim=-60) # Higher elevation to see "From Top"

# Axis Lines
axis_lines, = ax.plot([], [], [], 'k--', linewidth=1, alpha=0.5)

# Grid for Surface
x = np.linspace(-zoom, zoom, resolution)
y = np.linspace(-zoom, zoom, resolution)
X_screen, Y_screen = np.meshgrid(x, y)

# Initial Surface
global surf
surf = ax.plot_surface(X_screen, Y_screen, np.zeros_like(X_screen), alpha=0)

# Create Scatter Objects for each item individually
scatters = {}
for name, data in objects_data.items():
    scatters[name] = ax.scatter([data[0]], [data[1]], [data[2]], 
                                c=data[3], marker=data[4], s=data[5], 
                                depthshade=False, label=name)

# --- 4. CONTROLS ---
# List of controls
labels = ['Surface', 'Axes', 'Earth', 'Moon', 'L1', 'L2', 'L3', 'L4', 'L5']
# Initial states (All True)
visibility = {label: True for label in labels}

# Create Checkbox Widget
rax = plt.axes([0.82, 0.3, 0.15, 0.4]) # [left, bottom, width, height]
check = CheckButtons(rax, labels, [True]*len(labels))

def toggle(label):
    visibility[label] = not visibility[label]

check.on_clicked(toggle)

# --- 5. ANIMATION LOOP ---
def update(frame):
    global surf
    angle = np.radians(frame)
    c, s = np.cos(angle), np.sin(angle)
    
    # Rotation Matrix
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

    # 1. Update Surface
    try: surf.remove()
    except: pass

    if visibility['Surface']:
        X_static = X_screen * c + Y_screen * s
        Y_static = -X_screen * s + Y_screen * c
        r1 = np.sqrt((X_static + mu)**2 + Y_static**2)
        r2 = np.sqrt((X_static - (1-mu))**2 + Y_static**2)
        U = -((1-mu)/r1) - (mu/r2) - 0.5 * (X_static**2 + Y_static**2)
        Z = np.clip(U, z_min, z_max)
        
        surf = ax.plot_surface(X_screen, Y_screen, Z, cmap='RdGy', 
                               rstride=1, cstride=1, linewidth=0, antialiased=False, 
                               alpha=1.0, vmin=z_min, vmax=z_max)

    # 2. Update Each Object Separately
    for name, data in objects_data.items():
        if visibility[name]:
            # Rotate this specific point
            pos_static = np.array([data[0], data[1], data[2]])
            pos_rot = R @ pos_static
            scatters[name]._offsets3d = ([pos_rot[0]], [pos_rot[1]], [pos_rot[2]])
        else:
            scatters[name]._offsets3d = ([], [], [])

    # 3. Update Axes
    if visibility['Axes']:
        axis_x = np.array([[-zoom, 0, z_min], [zoom, 0, z_min]])
        axis_y = np.array([[0, -zoom, z_min], [0, zoom, z_min]])
        rot_x = (R @ axis_x.T).T
        rot_y = (R @ axis_y.T).T
        combined_x = [rot_x[0,0], rot_x[1,0], np.nan, rot_y[0,0], rot_y[1,0]]
        combined_y = [rot_x[0,1], rot_x[1,1], np.nan, rot_y[0,1], rot_y[1,1]]
        combined_z = [rot_x[0,2], rot_x[1,2], np.nan, rot_y[0,2], rot_y[1,2]]
        axis_lines.set_data(combined_x, combined_y)
        axis_lines.set_3d_properties(combined_z)
    else:
        axis_lines.set_data([], [])
        axis_lines.set_3d_properties([])

    return [surf] + list(scatters.values()) + [axis_lines]

# --- 6. RUN ---
print(f"Rendering with Granular Controls...")
anim = FuncAnimation(fig, update, frames=np.arange(0, 360, ANGLE_STEP), interval=FRAME_DELAY, blit=False)
plt.show()