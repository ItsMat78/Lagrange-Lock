import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.optimize import newton

# --- 1. SETUP & CONSTANTS ---
mu = 0.01215
resolution = 200  # Grid size (200x200 pixels)
limit = 1.5       # Zoom level (-1.5 to 1.5)

# Calculate Static L-Points (We do this ONCE)
# L1, L2, L3 require a solver
def eq_L1(x): return x - (1-mu)/(x+mu)**2 + mu/(x-(1-mu))**2
def eq_L2(x): return x - (1-mu)/(x+mu)**2 - mu/(x-(1-mu))**2
def eq_L3(x): return x + (1-mu)/(x+mu)**2 + mu/(x-(1-mu))**2

l1 = newton(eq_L1, 0.8)
l2 = newton(eq_L2, 1.2)
l3 = newton(eq_L3, -1.0)
l4_x, l4_y = 0.5 - mu, np.sqrt(3)/2
l5_x, l5_y = 0.5 - mu, -np.sqrt(3)/2

# Store static positions [x, y]
# Earth, Moon, L1, L2, L3, L4, L5
static_points = np.array([
    [-mu, 0],          # Earth
    [1-mu, 0],         # Moon
    [l1, 0],           # L1
    [l2, 0],           # L2
    [l3, 0],           # L3
    [l4_x, l4_y],      # L4
    [l5_x, l5_y]       # L5
])

# Define the Grid (Inertial Frame - Fixed Screen)
x = np.linspace(-limit, limit, resolution)
y = np.linspace(-limit, limit, resolution)
X_fixed, Y_fixed = np.meshgrid(x, y)

# --- 2. PHYSICS FUNCTION ---
def get_potential(angle):
    """
    Calculates the potential at every pixel for a given rotation angle.
    Instead of rotating the image, we rotate the coordinates BACKWARDS 
    to sample the static potential function.
    """
    # Create Rotation Matrix for BACKWARD rotation (-angle)
    c, s = np.cos(-angle), np.sin(-angle)
    
    # Rotate the grid coordinates
    X_rot = c * X_fixed - s * Y_fixed
    Y_rot = s * X_fixed + c * Y_fixed
    
    # Calculate Distances in this rotated frame
    r1 = np.sqrt((X_rot + mu)**2 + Y_rot**2)       # Dist to Earth
    r2 = np.sqrt((X_rot - (1-mu))**2 + Y_rot**2)   # Dist to Moon
    
    # Effective Potential Formula
    # Note: We clip the "gravity wells" so the heatmap doesn't turn all black
    U = -((1-mu)/r1) - (mu/r2) - 0.5 * (X_rot**2 + Y_rot**2)
    return np.clip(U, -2.5, -1.4)

# --- 3. ANIMATION SETUP ---
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_title("Rotating Gravitational Field (Inertial Frame)")
ax.set_xlabel("X (Inertial)")
ax.set_ylabel("Y (Inertial)")

# Initial Heatmap (t=0)
Z = get_potential(0)
heatmap = ax.imshow(Z, extent=[-limit, limit, -limit, limit], origin='lower', cmap='RdGy', animated=True)

# Scatter plots for Earth/Moon (Circles) and L-Points (X symbols)
# Index 0=Earth, 1=Moon
bodies_plot, = ax.plot([], [], 'o', color='blue', markersize=8) # Earth/Moon placeholders (colors fixed in update)
# Index 2-6 = L1-L5
lpoints_plot, = ax.plot([], [], 'rx', markersize=8, markeredgewidth=2) 

# Fix markers for Earth (Blue) and Moon (Grey) manually in update loop is tricky with single plot object
# So we use two objects
earth_moon_plot, = ax.plot([], [], 'o', markersize=10) # We will color them manually or just use one color
# Actually, let's just make Earth Blue and Moon Grey using separate calls for clarity
earth_dot, = ax.plot([], [], 'bo', markersize=12, label='Earth')
moon_dot, = ax.plot([], [], 'o', color='grey', markersize=8, label='Moon')

ax.legend(loc='upper right')

def update(frame):
    angle = np.radians(frame)
    
    # 1. Update Heatmap
    Z_new = get_potential(angle)
    heatmap.set_data(Z_new)
    
    # 2. Update Points (Forward Rotation)
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([[c, -s], [s, c]])
    
    # Rotate all static points to new inertial positions
    rotated_points = (R @ static_points.T).T
    
    # Update Earth (Index 0)
    earth_dot.set_data([rotated_points[0,0]], [rotated_points[0,1]])
    
    # Update Moon (Index 1)
    moon_dot.set_data([rotated_points[1,0]], [rotated_points[1,1]])
    
    # Update L-Points (Indices 2 through 6) - Marked with 'X'
    lpoints_plot.set_data(rotated_points[2:, 0], rotated_points[2:, 1])
    
    return heatmap, earth_dot, moon_dot, lpoints_plot

# --- 4. RUN ---
# Frames=0 to 360 degrees
anim = FuncAnimation(fig, update, frames=np.arange(0, 360, 2), interval=20, blit=True)
plt.show()