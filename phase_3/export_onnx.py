import sys
import os
import torch
import torch
import torch.nn as nn
# import onnx (Moved to local import to allow running without full onnx package if needed)
from stable_baselines3 import PPO

# Add path so phase_3 module is found
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

if __name__ == "__main__":
    pass

# Wrapper for the policy
class ActorWrapper(nn.Module):
    def __init__(self, policy):
        super().__init__()
        self.policy = policy
        
    def forward(self, obs):
        # Based on SB3 ActorCriticPolicy.forward / _predict
        features = self.policy.extract_features(obs)
        latent_pi = self.policy.mlp_extractor.forward_actor(features)
        mean_actions = self.policy.action_net(latent_pi)
        return torch.clamp(mean_actions, -1.0, 1.0)

def export():
    # Model path - assuming it is in the same directory as this script
    model_path = os.path.join(current_dir, "ppo_satellite_14000000_steps.zip")
    if not os.path.exists(model_path):
        # Fallback to root
        model_path = os.path.join(project_root, "ppo_satellite_14000000_steps.zip")
        if not os.path.exists(model_path):
            print(f"Model zip not found at {model_path}")
            return

    output_path = os.path.join(project_root, "phase_2", "model.onnx")
    data_path = output_path + ".data"
    
    # Clean up old external data if it exists
    if os.path.exists(data_path):
        try:
            os.remove(data_path)
            print(f"Removed old external data: {data_path}")
        except:
            pass

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Loading {model_path}...")
    try:
        model = PPO.load(model_path, device="cpu")
        actor = ActorWrapper(model.policy)
        actor.eval()
        
        # New input shape: (1, 7) [x, y, z, vx, vy, vz, fuel]
        dummy_input = torch.randn(1, 7)
        
        # Initial Export
        torch.onnx.export(
            actor,
            dummy_input,
            output_path,
            opset_version=11, # Keep 11 for broad compatibility
            input_names=["input"],
            output_names=["output"]
        )
        
        # Post-process to ensure single file
        # Validation skipped due to missing/broken 'onnx' package
        pass
        
        # try:
        #     import onnx
        #     onnx_model = onnx.load(output_path)
        #     onnx.checker.check_model(onnx_model)
        #     
        #     # Force save as single protobuf (no external data)
        #     onnx.save_model(onnx_model, output_path, save_as_external_data=False)
        #     print("Consolidated successfully using 'onnx' package.")
        # except ImportError:
        #     print("WARNING: 'onnx' package not found. Skipping validation/consolidation.")
        #     print("The model.onnx file should still work if it's <2GB (which it likely is).")
        # except Exception as e:
        #     print(f"Validation failed: {e}")

        size_kb = os.path.getsize(output_path) / 1024
        print(f"Exported to {output_path} ({size_kb:.2f} KB)")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Export failed: {e}")

if __name__ == "__main__":
    export()
