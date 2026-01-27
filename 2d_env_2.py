import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import CheckButtons
from scipy.optimize import newton

# --- 1. PHYSICS CONFIGURATION ---
mu = 0.01215        # Earth-Moon Mass Parameter
resolution = 150    # Grid Resolution (Lowered slightly for smoother animation)
zoom = 1.5          # View limits

# --- 2. CALCULATE L-POINTS (STATIC FRAME) ---
# We solve these once so we know where to draw the 'X' markers
def eq_L1(x): return x - (1-mu)/(x+mu)**2 + mu/(x-(1-mu))**2
def eq_L2(x): return x - (1-mu)/(x+mu)**2 - mu/(x-(1-mu))**2
def eq_L3(x): return x + (1-mu)/(x+mu)**2 + mu/(x-(1-mu))**2

print("Calculating Lagrange Points...")
l1 = newton(eq_L1, 0.8)
l2 = newton(eq_L2, 1.2)
l3 = newton(eq_L3, -1.0)
l4_x, l4_y = 0.5 - mu, np.sqrt(3)/2
l5_x, l5_y = 0.5 - mu, -np.sqrt(3)/2

# Static Positions [Earth, Moon, L1, L2, L3, L4, L5]
static_coords = np.array([
    [-mu, 0], [1-mu, 0],        # Earth, Moon
    [l1, 0], [l2, 0], [l3, 0],  # L1, L2, L3
    [l4_x, l4_y], [l5_x, l5_y]  # L4, L5
])

# --- 3. GRAPHICS SETUP ---
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(left=0.25, right=0.95) # Make room for controls on left

ax.set_title("Rotational Gravitational Potential\n(Inertial Frame)")
ax.set_xlabel("X (Inertial)")
ax.set_ylabel("Y (Inertial)")
ax.set_aspect('equal')

# --- 4. INITIALIZE LAYERS ---

# Layer 1: The Heatmap
x = np.linspace(-zoom, zoom, resolution)
y = np.linspace(-zoom, zoom, resolution)
X_screen, Y_screen = np.meshgrid(x, y)
# Initialize with zeros, updated in loop
heatmap = ax.imshow(np.zeros_like(X_screen), extent=[-zoom, zoom, -zoom, zoom], 
                    origin='lower', cmap='RdGy', vmin=-2.5, vmax=-1.4, animated=True)

# Layer 2: Planets (Blue/Grey Dots)
planets_plot, = ax.plot([], [], 'o', markersize=10, zorder=5) 
# Note: We will manually color them in the update loop or just use one color for simplicity, 
# but let's separate them for clarity:
earth_dot, = ax.plot([], [], 'bo', markersize=12, label='Earth', zorder=5)
moon_dot,  = ax.plot([], [], 'o', color='grey', markersize=8, label='Moon', zorder=5)

# Layer 3: L-Points (Red X)
lpoints_plot, = ax.plot([], [], 'rx', markersize=8, markeredgewidth=2, label='L-Points', zorder=6)

# --- 5. INTERFACE (CONTROLS & INFO) ---

# Checkbox Area
rax = plt.axes([0.02, 0.6, 0.18, 0.15]) # [left, bottom, width, height]
check = CheckButtons(rax, ['Heatmap', 'L-Points', 'Planets'], [True, True, True])

# Explanation Text Area
plt.figtext(0.02, 0.35, "COLOR LEGEND:\n\n"
                        "RED (Dark):\n"
                        "Gravity Wells.\n"
                        "Deep negative energy.\n"
                        "Objects fall in here.\n\n"
                        "WHITE (Bright):\n"
                        "High Ridges.\n"
                        "Higher potential energy.\n"
                        "Objects slide off here.\n\n"
                        "CALCULATION:\n"
                        "U = Gravity (Earth)\n"
                        "   + Gravity (Moon)\n"
                        "   + Centrifugal Force",
            fontsize=9, bbox={'facecolor':'white', 'alpha':0.8, 'pad':5})

# Visibility State
visible = {'Heatmap': True, 'L-Points': True, 'Planets': True}

def toggle(label):
    visible[label] = not visible[label]
    # Apply changes immediately
    if label == 'Heatmap': heatmap.set_visible(visible[label])
    if label == 'L-Points': lpoints_plot.set_visible(visible[label])
    if label == 'Planets': 
        earth_dot.set_visible(visible[label])
        moon_dot.set_visible(visible[label])
    plt.draw()

check.on_clicked(toggle)

# --- 6. ANIMATION LOOP ---
def update(frame):
    angle = np.radians(frame)
    c, s = np.cos(angle), np.sin(angle)
    
    # A. Rotate Heatmap (Inverse Rotation of Grid)
    # We only calc this if visible to save CPU, but for animation smoothness we usually calc it anyway.
    if visible['Heatmap']:
        # Rotate grid coords BACKWARDS to sample static potential
        X_static = X_screen * c + Y_screen * s
        Y_static = -X_screen * s + Y_screen * c
        
        # Distance to Earth (-mu) and Moon (1-mu)
        r1 = np.sqrt((X_static + mu)**2 + Y_static**2)
        r2 = np.sqrt((X_static - (1-mu))**2 + Y_static**2)
        
        # Effective Potential = Gravity - Centrifugal
        U = -((1-mu)/r1) - (mu/r2) - 0.5 * (X_static**2 + Y_static**2)
        
        # Update Image (Clipped for visual contrast)
        heatmap.set_data(np.clip(U, -2.5, -1.4))
    
    # B. Rotate Points (Forward Rotation)
    R = np.array([[c, -s], [s, c]])
    rot_pts = (R @ static_coords.T).T
    
    # Update Earth/Moon
    earth_dot.set_data([rot_pts[0,0]], [rot_pts[0,1]])
    moon_dot.set_data([rot_pts[1,0]], [rot_pts[1,1]])
    
    # Update L-Points
    lpoints_plot.set_data(rot_pts[2:, 0], rot_pts[2:, 1])
    
    return heatmap, earth_dot, moon_dot, lpoints_plot

# --- 7. RUN ---
# interval=50 is slightly slower to give time for calculation
anim = FuncAnimation(fig, update, frames=np.arange(0, 360, 2), interval=50, blit=False)
plt.show()