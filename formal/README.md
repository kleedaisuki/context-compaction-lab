# Lean structural verification

This directory contains dependency-free Lean 4 / Std proofs of finite accounting,
price geometry, occupancy exchange, exact threshold quantization for arbitrary finite
branch programs, uniform-approximation optimization transfer, and a strict-reset obstruction. It does not
formalize the Python simulator or an infinite stochastic process.

Install Lean 4 separately (checked with version 4.33.1), then run from the repository:

```powershell
./formal/verify.ps1
# If lean is not on PATH, pass the path to an already installed executable:
./formal/verify.ps1 -LeanExecutable '<installed-lean-executable>'
```

The script does not install toolchains or dependencies. Generated `Structural.olean`
and `verification.log` are written to `.cache/lean/`. Every key theorem prints its
axiom dependencies. Compiler errors or an admitted-proof dependency fail the check.

See `docs/research/lean-structural-verification.md` for precise mathematical scope.
