#!/usr/bin/env python3
"""Deterministic arithmetic examples; no model training or third-party packages."""
import json
import math
from pathlib import Path

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def relu(x):
    return max(0.0, x)

def gelu(x):
    return x * (1 + math.erf(x / math.sqrt(2))) / 2

def silu(x):
    return x * sigmoid(x)

def main():
    xor = []
    for x1, x2 in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        s = x1 + x2
        y = relu(s) - 2 * relu(s - 1)
        assert y == (x1 ^ x2)
        xor.append({"input": [x1, x2], "hidden": [relu(s), relu(s - 1)], "output": y})
    # Independent direct substitution verifies the affine composition identity.
    affine = [{"x": x, "stacked": 3 * (2 * x + 1) - 4, "folded": 6 * x - 1} for x in [-2, 0, 3]]
    assert all(r["stacked"] == r["folded"] for r in affine)
    assert math.isclose(gelu(1), 0.8413447460685429)
    values = [{"x": x, "sigmoid": sigmoid(x), "tanh": math.tanh(x), "relu": relu(x), "gelu_exact": gelu(x), "silu": silu(x)} for x in [-2, -1, 0, 1, 2]]
    result = {"scope": "hand-constructed XOR and exact arithmetic; not a trained model or a benchmark", "xor": xor, "affine_fold": affine, "activation_values": values, "ten_sigmoid_factors": 0.25 ** 10, "ffn_matched_width": {"ordinary": 3072, "gated": 2048}}
    (Path(__file__).parent / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"xor": [r["output"] for r in xor], "affine_fold": "verified", "gelu_at_one": gelu(1)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
