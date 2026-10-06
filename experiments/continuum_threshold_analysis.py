"""Bridge exact engine jump laws to continuous task-level budget responses.

The Gaussian budget is sampled once per complete task, never once per reset
decision. The separate uniform-law quadrature experiment states its continuum
scaling explicitly and is not another model of the production workload.
"""

from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.optimize import brentq
from scipy.special import ndtr

from context_compaction_lab.continuum_symbolics import (
    GaussianThresholdModel,
    uniform_continuum_expressions,
)
from context_compaction_lab.structural_symbolics import (
    ALPHA,
    CHANNELS,
    THRESHOLD,
    OccupationVector,
    ThresholdBand,
    ThresholdCurve,
)


def load_curve(path: Path, policy: str = "first_use") -> ThresholdCurve:
    """Recover exact symbolic occupations, not cached floating cost estimates."""
    source = json.loads(path.read_text(encoding="utf-8"))
    bands = []
    for band in source["curves"][policy]["bands"]:
        entries = tuple(sp.sympify(band["occupation"][channel]["polynomial"],
                                   locals={"alpha": ALPHA}) for channel in CHANNELS)
        bands.append(ThresholdBand(band["lower_exclusive"], band["upper_inclusive"],
                                   OccupationVector(entries)))
    return ThresholdCurve(tuple(bands))


def numeric_model(curve: ThresholdCurve, read_price: sp.Rational) -> GaussianThresholdModel:
    """Apply exact alpha/prices before converting coefficients for numeric kernel evaluation."""
    prices = (sp.Rational(3, 10**6), sp.Rational(3, 800000), read_price,
              sp.Rational(3, 200000))
    model = GaussianThresholdModel.from_curve(curve, prices)
    return GaussianThresholdModel(model.base.subs(ALPHA, sp.Rational(7, 20)),
                                  model.boundaries, tuple(jump.subs(ALPHA, sp.Rational(7, 20))
                                                          for jump in model.jumps))


def raw_cost(model: GaussianThresholdModel, centers: np.ndarray) -> np.ndarray:
    """Evaluate right-closed exact cells, including the lower clipped task budget."""
    boundaries = np.asarray(model.boundaries)
    cells = float(model.base) + np.concatenate(([0], np.cumsum([float(j) for j in model.jumps])))
    index = np.searchsorted(boundaries, np.maximum(1, centers), side="left")
    return cells[index]


def stationary_points(model: GaussianThresholdModel, sigma: float) -> list[dict]:
    """Locate derivative sign changes without interpreting underflow as a flat stationary region."""
    boundaries = np.asarray(model.boundaries, dtype=float)
    jumps = np.array([float(jump) for jump in model.jumps])
    nonzero = jumps != 0
    edges, weights = boundaries[nonzero], jumps[nonzero]

    def scaled_gradient(center: float) -> float:
        """Normalize signed kernel terms before root search so tiny tails retain their sign."""
        logs = np.log(np.abs(weights)) - ((center - edges) / sigma)**2 / 2
        return float(np.sum(np.sign(weights) * np.exp(logs - logs.max())))

    grid = np.linspace(1, 320, 6381)
    signs = np.array([np.sign(scaled_gradient(center)) for center in grid])
    points = []
    for left, right, left_sign, right_sign in zip(grid, grid[1:], signs, signs[1:]):
        if left_sign == right_sign or left_sign == 0:
            continue
        root = brentq(scaled_gradient, left, right, xtol=1e-11)
        if points and abs(root - points[-1]["center"]) < 1e-7:
            continue
        evaluated = model.evaluate(root, sigma, {})
        log_curvature, sign = model.derivative_log(root, sigma, {}, order=2)
        points.append({
            "center": root, "kind": "minimum" if sign > 0 else "maximum",
            "cost_usd": float(evaluated["cost"]),
            "raw_cost_at_center_usd": float(raw_cost(model, np.array(root))),
            "bias_usd": float(evaluated["cost"] - raw_cost(model, np.array(root))),
            "local_error_bound_usd": float(evaluated["local_error_bound"]),
            "log10_local_error_bound": float(evaluated["log_local_error_bound"]) / math.log(10),
            "log10_absolute_curvature": log_curvature / math.log(10),
        })
    return points


def actual_curve_analysis(curve: ThresholdCurve) -> tuple[dict, dict]:
    """Evaluate both price regimes on the same real-engine symbolic stopping law."""
    cases = {
        "default_prices": numeric_model(curve, sp.Rational(3, 10**7)),
        "read_price_sensitivity": numeric_model(curve, sp.Rational(3, 10**6)),
    }
    grid = np.linspace(1, 320, 6381)
    results, plot_data = {}, {}
    for name, model in cases.items():
        original = raw_cost(model, grid)
        base_minimum = float(original.min())
        rows, plots = [], {}
        for sigma in (0.25, 1.0, 4.0, 12.0):
            values = model.evaluate(grid, sigma, {})
            integrated = model.band_integral(grid, sigma, {})
            discrepancy = float(np.max(np.abs(values["cost"] - integrated)))
            assert discrepancy < 2e-17
            assert np.all(np.abs(values["cost"] - original)
                          <= values["local_error_bound"] + 2e-17)
            assert float(values["cost"].min()) >= base_minimum - 2e-17
            points = stationary_points(model, sigma)
            minima = [point for point in points if point["kind"] == "minimum"]
            best = min(minima, key=lambda point: point["cost_usd"]) if minima else None
            # Numerical indistinguishability regions are more honest than one flat-tail optimum.
            near = grid[values["cost"] <= values["cost"].min() + 1e-8]
            checkpoints = {}
            for center in (100.0, 156.0, 167.0, 178.0, 268.0, 290.0):
                point = model.evaluate(center, sigma, {})
                checkpoints[str(center)] = {key: float(value) for key, value in point.items()}
                checkpoints[str(center)]["raw_cost_usd"] = float(raw_cost(model, np.array(center)))
            rows.append({
                "sigma_tokens": sigma, "stationary_points": points,
                "minimum_sign_changes": len(minima),
                "maximum_sign_changes": len(points) - len(minima),
                "best_local_minimum": best,
                "minimum_on_1_to_320_grid_usd": float(values["cost"].min()),
                "near_minimum_grid_envelope_at_1e_minus_8_usd": [float(near[0]), float(near[-1])],
                "band_integral_max_discrepancy_usd": discrepancy,
                "checkpoints": checkpoints,
            })
            plots[str(sigma)] = values
        results[name] = {
            "status": "declared price regimes on exact engine extraction, not provider advice",
            "base_global_minimum_usd": base_minimum,
            "exact_base": str(model.base), "boundaries": list(model.boundaries),
            "exact_jumps": [str(jump) for jump in model.jumps],
            "total_jump_variation_usd": sum(abs(float(jump)) for jump in model.jumps),
            "results": rows,
        }
        plot_data[name] = {"grid": grid, "raw": original, "smooth": plots}
    return results, plot_data


def uniform_lattice_bridge() -> dict:
    """Check continuum quadrature and a nonconverging fine-scale gradient regime."""
    expressions = uniform_continuum_expressions()
    rows = []
    for cells in (16, 64, 256, 1024):
        delta = 1 / cells
        locations = (np.arange(cells) + 0.5) * delta
        probe_centers = np.array([0.5, 0.5 + delta / 2])
        row = {"cells": cells, "delta": delta,
               "raw_lattice_cost_uniform_error": delta / 2}
        for regime, sigma in (("coarse", math.sqrt(delta)), ("resolves_lattice", delta / 8)):
            z = (probe_centers[:, None] - locations) / sigma
            cost = delta * np.sum(ndtr(-z), axis=-1)
            gradient = (-delta * np.sum(np.exp(-z**2 / 2), axis=-1)
                        / (sigma * math.sqrt(2 * math.pi)))
            continuum_gradient = -(ndtr(probe_centers / sigma) - ndtr((probe_centers - 1) / sigma))
            row[regime] = {
                "sigma": sigma, "sigma_over_delta": sigma / delta,
                "probe_centers": probe_centers.tolist(), "regularized_cost": cost.tolist(),
                "lattice_gradient": gradient.tolist(),
                "continuum_regularized_gradient": continuum_gradient.tolist(),
                "gradient_error_from_uniform_interior_minus_one": (gradient + 1).tolist(),
            }
        rows.append(row)
    return {
        "model": "U uniform(0,1), cost 1{U>=h}; midpoint lattice, one clipped Gaussian threshold",
        "not_claimed": "not a fitted or calibrated continuum law for working-set simulator",
        "symbolic": {key: str(value) for key, value in expressions.items()}, "rows": rows,
    }


def comparison_figure(plot_data: dict, destination: Path) -> None:
    """Plot exact base and whole-task regularization with their analytic kernel gradients."""
    os.environ.setdefault("MPLCONFIGDIR", str(Path(".cache/matplotlib").resolve()))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for column, (name, data) in enumerate(plot_data.items()):
        axes[0, column].plot(data["grid"], data["raw"], color="black", linewidth=1.5,
                             label="Exact endogenous ledger")
        for sigma, values in data["smooth"].items():
            axes[0, column].plot(data["grid"], values["cost"], label=f"Task budget sigma={sigma}")
            axes[1, column].plot(data["grid"], values["gradient"], label=f"sigma={sigma}")
        axes[0, column].set_title(name.replace("_", " "))
        axes[0, column].set_ylabel("Expected full invoice (USD)")
        axes[1, column].set_ylabel("Controller gradient (USD / threshold token)")
        for axis in axes[:, column]:
            axis.set_xlabel("Mean task budget h (fixture token units)")
            axis.grid(alpha=0.25)
            axis.legend(fontsize=8)
    figure.suptitle("Whole-task randomized budgets: continuous responses, not sweet spots")
    figure.savefig(destination, dpi=160)
    plt.close(figure)


def lattice_gradient_figure(destination: Path) -> None:
    """Show that cost convergence alone does not control the coarse gradient limit."""
    import matplotlib.pyplot as plt

    cells, delta = 64, 1 / 64
    grid = np.linspace(0.45, 0.55, 1601)
    locations = (np.arange(cells) + 0.5) * delta
    figure, axis = plt.subplots(figsize=(8, 3.5), constrained_layout=True)
    for label, sigma in (("sigma=sqrt(delta): coarse", math.sqrt(delta)),
                         ("sigma=delta/8: lattice resolved", delta / 8)):
        z = (grid[:, None] - locations) / sigma
        gradient = (-delta * np.sum(np.exp(-z**2 / 2), axis=-1)
                    / (sigma * math.sqrt(2 * math.pi)))
        axis.plot(grid, gradient, label=label)
    axis.axhline(-1, color="black", linestyle="--", label="Uniform-law interior derivative")
    axis.set(xlabel="Macroscopic threshold h", ylabel="Regularized derivative",
             title="Analytic midpoint quadrature: bandwidth/quantum controls gradient fidelity")
    axis.legend(fontsize=8)
    axis.grid(alpha=0.25)
    figure.savefig(destination, dpi=160)
    plt.close(figure)


def main() -> None:
    """Verify exact Gaussian calculus and materialize numeric continuum bridge evidence."""
    started = time.perf_counter()
    cached = Path(".cache/structural-symbolic-analysis/results.json")
    curve = load_curve(cached)
    symbolic = GaussianThresholdModel.from_curve(curve)
    cost = symbolic.symbolic_cost()
    gradient = symbolic.symbolic_gradient()
    curvature = symbolic.symbolic_curvature()
    assert sp.simplify(sp.diff(cost, THRESHOLD) - gradient) == 0
    assert sp.simplify(sp.diff(gradient, THRESHOLD) - curvature) == 0
    actual, plots = actual_curve_analysis(curve)
    output = {
        "semantics": "one H=max(1,h+sigma Z) for each whole task, not per-decision jitter",
        "exact_source": str(cached), "symbolic_cost": str(cost),
        "symbolic_gradient": str(gradient), "symbolic_curvature": str(curvature),
        "local_bound": "sum_b abs(Delta_b) Phi(-abs(h-b)/sigma), including half mass at h=b",
        "actual_curve_results": actual, "uniform_lattice_bridge": uniform_lattice_bridge(),
    }
    directory = Path(".cache/continuum-threshold-analysis")
    directory.mkdir(parents=True, exist_ok=True)
    comparison_figure(plots, directory / "comparison.png")
    lattice_gradient_figure(directory / "lattice-gradient.png")
    output["runtime_seconds"] = time.perf_counter() - started
    (directory / "results.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    compact = {name: [{key: row[key] for key in (
        "sigma_tokens", "minimum_sign_changes", "maximum_sign_changes", "best_local_minimum",
        "minimum_on_1_to_320_grid_usd", "near_minimum_grid_envelope_at_1e_minus_8_usd",
    )} for row in case["results"]] for name, case in actual.items()}
    print(json.dumps({"runtime_seconds": output["runtime_seconds"], "actual": compact,
                      "lattice": output["uniform_lattice_bridge"]["rows"]}, indent=2))


if __name__ == "__main__":
    main()
