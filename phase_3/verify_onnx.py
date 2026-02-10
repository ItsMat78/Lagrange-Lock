import onnxruntime as ort
import numpy as np
import os

model_path = "phase_2/model.onnx"

if not os.path.exists(model_path):
    print(f"File not found: {model_path}")
    exit(1)

print(f"Testing model: {model_path}")
print(f"Size: {os.path.getsize(model_path)} bytes")

try:
    session = ort.InferenceSession(model_path)
    print("Session created successfully.")
    
    input_name = session.get_inputs()[0].name
    print(f"Input name: {input_name}")
    
    input_shape = session.get_inputs()[0].shape
    print(f"Input shape: {input_shape}")
    
    # Create dummy input [1, 7]
    data = np.random.randn(1, 7).astype(np.float32)
    
    output = session.run(None, {input_name: data})
    print("Inference successful.")
    print(f"Output shape: {output[0].shape}")
    print(f"Output: {output[0]}")
    
except Exception as e:
    print(f"Verification failed: {e}")
