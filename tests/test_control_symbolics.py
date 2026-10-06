"""Independent exact checks for general finite-horizon operator identities."""

import pytest
import sympy as sp

from context_compaction_lab.control_symbolics import (
    FiniteControl,
    adjoint_derivative,
    performance_difference,
)


def fixture(horizon: int, parameter: sp.Symbol) -> FiniteControl:
    """Build correlated state evolution, not independent category marginals."""
    kernels, ledgers = [], []
    for t in range(horizon):
        kernels.append(
            sp.Matrix([[parameter, 1 - parameter], [sp.Rational(1, 3), sp.Rational(2, 3)]])
        )
        ledgers.append(sp.Matrix([[t + 1, 2, 3 * parameter, 4], [5, t + 2, 1, 2 + parameter]]))
    return FiniteControl(sp.Matrix([[parameter, 1 - parameter]]), tuple(kernels), tuple(ledgers))


@pytest.mark.parametrize("horizon", range(5))
def test_occupation_and_adjoint(horizon: int) -> None:
    """The direct derivative includes correlated occupancy and initial-law effects."""
    theta = sp.Symbol("theta", nonnegative=True)
    model = fixture(horizon, theta)
    p = sp.Matrix(sp.symbols("pi pw pr po", nonnegative=True))
    invoice = model.invoice(p)
    assert sp.expand(invoice - (model.expected_ledger() * p)[0]) == 0
    assert sp.expand(sp.diff(invoice, theta) - adjoint_derivative(model, p, theta)) == 0
    for category, price in enumerate(p):
        assert sp.expand(sp.diff(invoice, price) - model.expected_ledger()[category]) == 0
    assert all(sp.expand(sum(row) - 1) == 0 for row in model.occupations())


def test_parameterized_prices_direct_term() -> None:
    """A changing tariff contributes a direct term even with unchanged transitions."""
    theta = sp.Symbol("theta", nonnegative=True)
    model = fixture(2, theta)
    p = sp.Matrix([theta, 2, 3, 4])
    assert sp.expand(sp.diff(model.invoice(p), theta) - adjoint_derivative(model, p, theta)) == 0


@pytest.mark.parametrize("horizon", (0, 1, 2, 3))
def test_performance_difference(horizon: int) -> None:
    """Independent backward totals equal the alternative-occupation advantage sum."""
    theta = sp.Symbol("theta", nonnegative=True)
    base = fixture(horizon, theta)
    alternative = FiniteControl(
        base.initial,
        tuple(sp.Matrix([[sp.Rational(1, 4), sp.Rational(3, 4)], [1, 0]]) for _ in range(horizon)),
        tuple(sp.Matrix([[9, 2, 3, 1], [2, 5, 8, 6]]) for _ in range(horizon)),
    )
    p = sp.Matrix(sp.symbols("pi pw pr po"))
    direct = alternative.invoice(p) - base.invoice(p)
    assert sp.expand(direct - performance_difference(base, alternative, p)) == 0


def test_immutable_and_bad_flow() -> None:
    """External matrix edits cannot mutate a validated probability model."""
    initial = sp.Matrix([[1]])
    model = FiniteControl(initial, (sp.eye(1),), (sp.ones(1, 4),))
    initial[0] = 0
    assert model.initial[0] == 1
    with pytest.raises(ValueError, match="sum to one"):
        FiniteControl(sp.Matrix([[1]]), (sp.Matrix([[2]]),), (sp.ones(1, 4),))
    with pytest.raises(ValueError, match="negative"):
        FiniteControl(sp.Matrix([[-1, 2]]), (), ())
    with pytest.raises(ValueError, match="four-category"):
        FiniteControl(sp.Matrix([[1]]), (sp.eye(1),), (sp.ones(1, 3),))
    with pytest.raises(ValueError, match="not floats"):
        FiniteControl(sp.Matrix([[1.0]]), (), ())
    with pytest.raises(ValueError, match="not floats"):
        model.invoice(sp.Matrix([1.0, 2, 3, 4]))
    with pytest.raises(ValueError, match="nonnegative prices"):
        model.invoice(sp.Matrix([-1, 2, 3, 4]))


def test_continuous_boundary_is_not_pathwise_gradient() -> None:
    """Integration adds a boundary term which a hard branch's ordinary diff omits."""
    x, h = sp.symbols("x h", real=True)
    a, b, c = sp.symbols("a b c", nonnegative=True)
    path = sp.Piecewise((c, h <= x), (a + b * x, True))
    expected = a * h + b * h**2 / 2 + c * (1 - h)
    assert sp.diff(path, h) == 0
    assert sp.diff(expected, h) == a + b * h - c
