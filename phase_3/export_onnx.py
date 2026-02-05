import torch
import torch.nn as nn
import onnx
from stable_baselines3 import PPO
import os
import glob
import json
import shutil

# Define paths
MODELS_DIR = "phase_3/models/PPO"
OUTPUT_DIR = "phase_2/models"

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
        # CRITICAL FIX: SB3 applies Tanh for continuous actions!
        return torch.tanh(mean_actions)

def export_model(model_name, source_path, dest_path):
    print(f"Exporting {model_name}...")
    try:
        model = PPO.load(source_path, device="cpu")
        onnx_actor = ActorWrapper(model.policy)
        dummy_input = torch.randn(1, 6)
        
        # Export
        torch.onnx.export(
            onnx_actor,
            dummy_input,
            dest_path,
            opset_version=17,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
        )
        
        # Post-process for single file
        onnx_model = onnx.load(dest_path)
        onnx.save_model(onnx_model, dest_path, save_as_external_data=False)
        print(f"Verified {dest_path}")
        return True
    except Exception as e:
        print(f"Failed to export {model_name}: {e}")
        return False

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # Clean up old intermediate ONNX files to match training cleanup
    print("Cleaning up old intermediate ONNX models...")
    for old_onnx in glob.glob(os.path.join(OUTPUT_DIR, "*_steps.onnx")):
        try:
            os.remove(old_onnx)
            print(f"Removed old export: {old_onnx}")
        except:
            pass
        
    model_files = glob.glob(os.path.join(MODELS_DIR, "*.zip"))
    exported_models = []
    
    print(f"Found {len(model_files)} models in {MODELS_DIR}")
    
    for f in model_files:
        name = os.path.splitext(os.path.basename(f))[0]
        out_name = f"{name}.onnx"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        
        if export_model(name, f, out_path):
            exported_models.append(out_name)
            
    # Save Index
    index_path = os.path.join(OUTPUT_DIR, "models.json")
    with open(index_path, "w") as f:
        json.dump(exported_models, f)
    
    # Also copy the latest one to root phase_2/model.onnx for backwards compatibility or default
    if exported_models:
        # Sort to find "final" or "latest steps"
        # Simple string sort works for date/version consistency usually
        exported_models.sort() 
        latest = exported_models[-1] 
        print(f"Selecting {latest} as default model.")
        
        shutil.copy(os.path.join(OUTPUT_DIR, latest), "phase_2/model.onnx")
        print(f"Copied {latest} to phase_2/model.onnx")

    print(f"Done. Exported {len(exported_models)} models.")
