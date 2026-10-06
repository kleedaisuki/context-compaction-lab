"""Exact finite-horizon occupation, adjoint and policy-difference identities.

These operators act on a supplied finite sufficient-state model, not a fitted
scalar context process. Transition entries may be symbolic on a declared
parameter domain; row sums are checked, while symbolic nonnegativity remains
the caller's explicit assumption. There is no claim that token length alone
is a sufficient state or that a hard threshold has an ordinary derivative.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class FiniteControl:
    """A finite, possibly nonstationary policy-induced control model.

    ``initial`` is a 1-by-d probability row. ``transitions[t]`` is the d-by-d
    kernel AFTER action t, and ``ledgers[t]`` is a d-by-4 conditional mean
    token ledger BEFORE that transition. Kernels and ledgers can encode
    arbitrary dependence through the supplied sufficient state. Terminal
    cost is zero; a terminal reward can instead be represented as a final
    ledger. All four categories must have the same disjoint billing semantics.

    Example:
        model = FiniteControl(sp.Matrix([[1]]), (sp.eye(1),),
                              (sp.Matrix([[2, 3, 5, 7]]),))
        invoice = model.invoice(sp.Matrix(sp.symbols("pi pw pr po")))

    The policy evaluation is price-linear ONLY if this initial law, its
    kernels and ledgers do not themselves depend on the prices.
    """

    initial: sp.MatrixBase
    transitions: tuple[sp.MatrixBase, ...]
    ledgers: tuple[sp.MatrixBase, ...]

    def __post_init__(self) -> None:
        """Freeze matrices and reject malformed probability-flow identities."""
        initial = sp.ImmutableMatrix(self.initial)
        transitions = tuple(sp.ImmutableMatrix(p) for p in self.transitions)
        ledgers = tuple(sp.ImmutableMatrix(ledger) for ledger in self.ledgers)
        if any(x.has(sp.Float) for matrix in (initial, *transitions, *ledgers) for x in matrix):
            raise ValueError("Exact control entries must be symbolic or rational, not floats.")
        d = initial.cols
        if initial.rows != 1 or d < 1 or len(transitions) != len(ledgers):
            raise ValueError("Require one initial probability row and equal kernel/ledger counts.")
        if any(p.shape != (d, d) for p in transitions):
            raise ValueError("Each transition kernel must match the state dimension.")
        if any(ledger.shape != (d, 4) for ledger in ledgers):
            raise ValueError("Each state needs a disjoint four-category conditional mean ledger.")
        probability_rows = [list(initial)]
        probability_rows.extend(list(p.row(i)) for p in transitions for i in range(d))
        if any(sp.simplify(sum(row) - 1) != 0 for row in probability_rows):
            raise ValueError("Initial law and transition rows must sum to one identically.")
        if any(
            x.is_negative is True or x.is_real is False or x.is_finite is False
            for row in probability_rows
            for x in row
        ):
            raise ValueError("Require finite, real, nonnegative probability entries.")
        if any(
            x.is_negative is True or x.is_real is False or x.is_finite is False
            for ledger in ledgers
            for x in ledger
        ):
            raise ValueError("Require finite, real, nonnegative conditional token occupations.")
        object.__setattr__(self, "initial", initial)
        object.__setattr__(self, "transitions", transitions)
        object.__setattr__(self, "ledgers", ledgers)

    def occupations(self) -> tuple[sp.ImmutableMatrix, ...]:
        """Return all forward state laws, including the terminal law."""
        rows = [self.initial]
        for kernel in self.transitions:
            rows.append(sp.ImmutableMatrix(rows[-1] * kernel))
        return tuple(rows)

    def expected_ledger(self) -> sp.ImmutableMatrix:
        """Compute the four expected category totals by occupation integration."""
        result = sp.zeros(1, 4)
        for row, ledger in zip(self.occupations(), self.ledgers):
            result += row * ledger
        return sp.ImmutableMatrix(result)

    def values(self, prices: sp.MatrixBase) -> tuple[sp.ImmutableMatrix, ...]:
        """Solve backward value equations without discarding future reset effects."""
        p = _prices(prices)
        values = [sp.zeros(self.initial.cols, 1)]
        for kernel, ledger in zip(reversed(self.transitions), reversed(self.ledgers)):
            values.append(sp.ImmutableMatrix(ledger * p + kernel * values[-1]))
        return tuple(reversed(values))

    def invoice(self, prices: sp.MatrixBase) -> sp.Expr:
        """Evaluate initial expected full-horizon cost with a zero terminal bill."""
        return (self.initial * self.values(prices)[0])[0]


def _prices(prices: sp.MatrixBase) -> sp.ImmutableMatrix:
    """Require exact nonnegative category prices; do not infer a provider tariff."""
    p = sp.ImmutableMatrix(prices)
    if p.shape != (4, 1):
        raise ValueError("Prices must be a four-category column vector.")
    if any(x.has(sp.Float) for x in p):
        raise ValueError("Exact price algebra requires symbolic or rational entries, not floats.")
    if any(x.is_negative is True or x.is_real is False or x.is_finite is False for x in p):
        raise ValueError("Require finite, real, nonnegative prices on the declared domain.")
    return p


def adjoint_derivative(
    model: FiniteControl, prices: sp.MatrixBase, parameter: sp.Symbol
) -> sp.Expr:
    """Differentiate smooth kernel/ledger parameters using forward-backward states.

    Includes the initial-law term and the full future value of a transition
    change. Applies where entries are genuinely differentiable and all terms
    finite. A hard-threshold indicator is NOT such a kernel; its boundary
    derivative requires a signed measure or a separately justified density.
    Price derivatives are also supported, with their direct ledger term.
    """
    p = _prices(prices)
    values, occupations = model.values(p), model.occupations()
    answer = (model.initial.diff(parameter) * values[0])[0]
    for t, (kernel, ledger) in enumerate(zip(model.transitions, model.ledgers)):
        direct = ledger.diff(parameter) * p + ledger * p.diff(parameter)
        propagated = kernel.diff(parameter) * values[t + 1]
        answer += (occupations[t] * (direct + propagated))[0]
    return answer


def performance_difference(
    baseline: FiniteControl, alternative: FiniteControl, prices: sp.MatrixBase
) -> sp.Expr:
    """Evaluate the exact alternative-minus-baseline telescoping identity.

    Requires the same state space, horizon and initial law. It weights the
    baseline action advantage by ALTERNATIVE state occupations, not baseline
    occupations. The models represent two nonanticipating policies of the
    same environment only if the caller supplies compatible action kernels.
    The algebra itself remains exact for arbitrary compatible matrix models.
    """
    if baseline.initial != alternative.initial:
        raise ValueError("Policies must share their initial law and state space.")
    if len(baseline.transitions) != len(alternative.transitions):
        raise ValueError("Policies must have the same fixed ordinary horizon.")
    p = _prices(prices)
    values, occupations = baseline.values(p), alternative.occupations()
    answer = sp.S.Zero
    for t, (kernel, ledger) in enumerate(zip(alternative.transitions, alternative.ledgers)):
        advantage = ledger * p + kernel * values[t + 1] - values[t]
        answer += (occupations[t] * advantage)[0]
    return answer
