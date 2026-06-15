"""
Export trained PPO policy weights to a compact JSON so the agent can run
*in the browser* (no Python server needed). The default MlpPolicy is a tiny
network: obs(7) -> Linear(64) -> tanh -> Linear(64) -> tanh -> action_net(3) mean,
plus a state-independent log_std(3) for the Gaussian action distribution.

We dump a few checkpoints so the static viewer can show convergence improving.

Run from the repo root:
    python phase_3/export_policy.py
Writes: docs/policy.json
"""

import os
import json
import numpy as np
from stable_baselines3 import PPO

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
MODELS_DIR = os.path.join(HERE, "models", "PPO_5M")
OUT_PATH = os.path.join(ROOT, "docs", "policy.json")

# (display name, checkpoint file) — early / converging / final
CHECKPOINTS = [
    ("PPO 0.5M (early)", "ppo_sat_5M_500000_steps.zip"),
    ("PPO 2M (converging)", "ppo_sat_5M_2000000_steps.zip"),
    ("PPO 5M (final)", "ppo_sat_5M_5000000_steps.zip"),
]


def extract(model_path):
    model = PPO.load(model_path, device="cpu")
    sd = model.policy.state_dict()

    def arr(key):
        return sd[key].cpu().numpy()

    # mlp_extractor.policy_net is Sequential(Linear, Tanh, Linear, Tanh)
    # -> Linear layers live at indices .0 and .2
    w0, b0 = arr("mlp_extractor.policy_net.0.weight"), arr("mlp_extractor.policy_net.0.bias")
    w1, b1 = arr("mlp_extractor.policy_net.2.weight"), arr("mlp_extractor.policy_net.2.bias")
    wout, bout = arr("action_net.weight"), arr("action_net.bias")
    log_std = arr("log_std")

    # torch Linear weight is (out, in); we store rows so JS does sum_j W[o][j]*x[j].
    return {
        "obs_dim": int(w0.shape[1]),
        "act_dim": int(wout.shape[0]),
        "w0": w0.tolist(), "b0": b0.tolist(),
        "w1": w1.tolist(), "b1": b1.tolist(),
        "w_out": wout.tolist(), "b_out": bout.tolist(),
        "log_std": log_std.tolist(),
    }


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    models = []
    for name, fname in CHECKPOINTS:
        path = os.path.join(MODELS_DIR, fname)
        if not os.path.exists(path):
            print(f"  SKIP (missing): {fname}")
            continue
        print(f"  Exporting {name} <- {fname}")
        m = extract(path)
        m["name"] = name
        models.append(m)

    with open(OUT_PATH, "w") as f:
        json.dump({"models": models}, f)

    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"Wrote {len(models)} models to {OUT_PATH} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
