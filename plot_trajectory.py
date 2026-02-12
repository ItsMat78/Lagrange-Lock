import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
import time
import os

def plot_trajectory():
    # Load data
    try:
        with open('trajectory_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: trajectory_data.json not found.")
        return

    # Extract coordinates
    x = [d['x'] for d in data]
    y = [d['y'] for d in data]
    z = [d['z'] for d in data]
    
    # Create plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot trajectory
    ax.plot(x, y, z, label='Trajectory', marker='.', markersize=2, linewidth=1)
    
    # Mark start and end
    ax.scatter(x[0], y[0], z[0], color='green', label='Start', s=50)
    ax.scatter(x[-1], y[-1], z[-1], color='red', label='End', s=50)
    
    # Add labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Orbit Trajectory')
    ax.legend()
    
    # Save plot
    output_file = 'trajectory_plot.png'
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

    print("Displaying plot for 10 seconds...")
    try:
        plt.show(block=False)
        plt.pause(10)
        plt.close()
    except Exception as e:
        print(f"Could not display plot window: {e}")
        # Build environments might not support display, but we saved the file

    
if __name__ == "__main__":
    plot_trajectory()
