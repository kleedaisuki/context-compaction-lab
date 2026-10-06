"""Exact algebra checks for finite-resolution continuum-bridge statements."""

import sympy as sp


def test_midpoint_lattice_transport_error() -> None:
    """The Uniform-to-midpoint coupling has mean error delta/4, not zero."""
    x = sp.Symbol("x", real=True)
    delta = sp.Symbol("delta", positive=True)
    one_cell = sp.integrate(delta / 2 - x, (x, 0, delta / 2)) + sp.integrate(
        x - delta / 2, (x, delta / 2, delta)
    )
    total_error = sp.simplify(one_cell / delta)
    assert total_error == delta / 4


def test_quadratic_staircase_jump_is_a_riemann_weight() -> None:
    """Vanishing jump masses can carry a nonzero macroscopic derivative."""
    k = sp.Symbol("k", integer=True, nonnegative=True)
    delta = sp.Symbol("delta", positive=True)
    x, a, b, c = sp.symbols("x a b c", real=True)
    function = a * x + b * x**2 / 2 + c
    jump = sp.expand(function.subs(x, (k + 1) * delta) - function.subs(x, k * delta))
    assert jump == a * delta + b * k * delta**2 + b * delta**2 / 2
    normalized_jump = sp.simplify((jump / delta).subs(k, x / delta))
    assert sp.limit(normalized_jump, delta, 0, dir="+") == sp.diff(function, x)


def test_gaussian_kernel_lipschitz_constant() -> None:
    """A coupling-based smoothed-gradient bound uses the correct sigma squared."""
    x = sp.Symbol("x", real=True)
    sigma = sp.Symbol("sigma", positive=True)
    density = sp.exp(-x**2 / (2 * sigma**2)) / (sigma * sp.sqrt(2 * sp.pi))
    kernel_slope = sp.diff(density, x)
    assert sp.simplify(kernel_slope.subs(x, sigma)) == -1 / (
        sigma**2 * sp.sqrt(2 * sp.pi * sp.E)
    )


def test_gradient_bridge_balancing_scale() -> None:
    """The surrogate-bias/noise balance is symbolic, not a guessed bandwidth."""
    sigma, error, curvature = sp.symbols("sigma error curvature", positive=True)
    bound = sp.sqrt(2 / sp.pi) * (error / sigma + curvature * sigma)
    stationary = sp.solve(sp.diff(bound, sigma), sigma)
    assert stationary == [sp.sqrt(error) / sp.sqrt(curvature)]
    assert sp.simplify(bound.subs(sigma, stationary[0])) == (
        2 * sp.sqrt(2 / sp.pi) * sp.sqrt(error * curvature)
    )
