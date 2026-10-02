#!/usr/bin/env python3
"""Small, dependency-free experiments for the loss-function introduction."""
import json
import math
from pathlib import Path


def mse(pred, values):
    return sum((pred - y) ** 2 for y in values) / len(values)


def mae(pred, values):
    return sum(abs(pred - y) for y in values) / len(values)


def huber(error, delta=1.0):
    a = abs(error)
    return 0.5 * error * error if a <= delta else delta * (a - 0.5 * delta)


def ce(p):
    return -math.log(p)


def focal(p, gamma=2.0, alpha=1.0):
    return alpha * (1 - p) ** gamma * ce(p)


def main():
    values = [1, 2, 3, 4, 20]
    # Check the analytic minimizers against a dense grid, not an optimizer implementation.
    grid = [i / 100 for i in range(-100, 2501)]
    mse_best = min(grid, key=lambda x: mse(x, values))
    mae_best = min(grid, key=lambda x: mae(x, values))
    assert abs(mse_best - 6) < 1e-12 and abs(mae_best - 3) < 1e-12
    result = {
        "input": values,
        "mse_best": mse_best,
        "mae_best": mae_best,
        "candidate_scores": {str(x): {"mse": mse(x, values), "mae": mae(x, values)} for x in [3, 6]},
        "cross_entropy_natural_log": {str(p): ce(p) for p in [0.9, 0.5, 0.01]},
        "focal_gamma_2_alpha_1": {str(p): {"weight": (1-p)**2, "loss": focal(p)} for p in [0.99, 0.2]},
        "label_smoothing_K3_epsilon_0_1": [1 - 0.1 + 0.1/3, 0.1/3, 0.1/3],
        "huber_delta_1": {str(e): huber(e) for e in [0, 1, 3]},
        "note": "Focal weights are multiplicative loss weights, not gradient ratios; all logs are natural."
    }
    dest = Path(__file__).with_name('results.json')
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
