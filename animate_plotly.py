
import json
import numpy as np
import plotly.graph_objects as go
import os

def create_animation(json_file='trajectory_data.json'):
    if not os.path.exists(json_file):
        print(f"File not found: {json_file}")
        return

    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract Data
    x = [d['x'] for d in data]
    y = [d['y'] for d in data]
    z = [d['z'] for d in data]
    t = [d['t'] for d in data]
    
    # Lagrange Points (Earth-Moon approx)
    # L1 ~ 0.836915, Moon ~ 1-mu (0.98785)
    L1_x = 0.836915
    Moon_x = 1.0 - 0.01215
    
    # Create Figure
    fig = go.Figure(
        data=[
            # 1. Trajectory Path (Background Line)
            go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines',
                line=dict(width=4, color='blue', dash='solid'),
                opacity=0.3,
                name='Full Path'
            ),
            # 2. Satellite (Animated Marker)
            go.Scatter3d(
                x=[x[0]], y=[y[0]], z=[z[0]],
                mode='markers',
                marker=dict(size=5, color='orange'),
                name='Satellite'
            ),
            # 3. Reference Points
            go.Scatter3d(
                x=[-0.01215], y=[0], z=[0],
                mode='markers+text',
                marker=dict(size=15, color='blue'),
                text=['Earth'],
                name='Earth'
            ),
            go.Scatter3d(
                x=[Moon_x], y=[0], z=[0],
                mode='markers+text',
                marker=dict(size=8, color='gray'),
                text=['Moon'],
                name='Moon'
            ),
            go.Scatter3d(
                x=[L1_x], y=[0], z=[0],
                mode='markers',
                marker=dict(size=5, color='red', symbol='x'),
                name='L1 Point'
            )
        ],
        layout=go.Layout(
            title="Satellite Trajectory Animation (L1 Halo Orbit)",
            scene=dict(
                xaxis=dict(title='X (AU)', range=[min(x)-0.1, max(x)+0.1]),
                yaxis=dict(title='Y (AU)', range=[min(y)-0.1, max(y)+0.1]),
                zaxis=dict(title='Z (AU)', range=[min(z)-0.1, max(z)+0.1]),
                aspectmode='data'
            ),
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True)])]
            )]
        ),
        frames=[go.Frame(
            data=[go.Scatter3d(x=[x[k]], y=[y[k]], z=[z[k]])],
            name=str(k)
        ) for k in range(0, len(x), 5)] # Downsample for smoother animation speed if lengthy
    )

    output_file = 'trajectory_animation.html'
    fig.write_html(output_file)
    print(f"Animation saved to {output_file}")

if __name__ == "__main__":
    create_animation()
