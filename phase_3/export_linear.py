import sys
import os
import torch
import torch.nn as nn
from stable_baselines3 import PPO

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

model_path = os.path.join(current_dir, "ppo_satellite_14000000_steps.zip")
output_path = os.path.join(project_root, "phase_2", "model_linear.onnx") # NEW NAME

class LinearActorWrapper(nn.Module):
    def __init__(self, policy):
        super().__init__()
        self.policy = policy
        
    def forward(self, obs):
        features = self.policy.extract_features(obs)
        latent_pi = self.policy.mlp_extractor.forward_actor(features)
        mean_actions = self.policy.action_net(latent_pi)
        
        # PURE LINEAR (No Clamp, No Tanh) - Let the Env clip it.
        # This matches the Torch output exactly.
        return mean_actions

def export_force():
    target_path = model_path
    
    if not os.path.exists(target_path):
        print(f"Model not found: {target_path}")
        # Try fallback
        fallback = os.path.join(project_root, "ppo_satellite_14000000_steps.zip")
        if os.path.exists(fallback):
             print(f"Found at fallback: {fallback}")
             target_path = fallback
        else:
            print("Model path not found anywhere.")
            return

    print(f"Loading PPO model from {target_path}...")
    model = PPO.load(target_path, device="cpu")
    
    actor = LinearActorWrapper(model.policy)
    actor.eval()
    
    dummy_input = torch.randn(1, 7)
    
    print(f"Exporting Linear Model to {output_path}...")
    torch.onnx.export(
        actor,
        dummy_input,
        output_path,
        opset_version=11,
        input_names=["input"],
        output_names=["output"]
    )
    print("Export Complete.")
    
    # Validation
    try:
        import onnx
        m = onnx.load(output_path)
        onnx.checker.check_model(m)
        print("ONNX Check Passed.")
    except Exception as e:
        print(f"ONNX Check Warning: {e}")

if __name__ == "__main__":
    export_force()
