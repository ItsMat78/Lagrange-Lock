import torch
import torch.nn as nn
import os

class Model(nn.Module):
    def forward(self, x): return x

try:
    print("Testing minimal ONNX export...")
    torch.onnx.export(Model(), torch.randn(1, 1), "test.onnx", opset_version=11)
    print("Export successful.")
    if os.path.exists("test.onnx"):
        os.remove("test.onnx")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Export failed: {e}")
