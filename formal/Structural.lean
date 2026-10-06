import Std

/-! Kernel-checked finite structural laws, not a verification of the Python simulator. -/
namespace ContextCompaction

/-- Four disjoint billing categories: input, write, read, and output. -/
abbrev Ledger := Fin 4 → Nat
/-- Nonnegative integer price units; a common rational scale can be applied afterward. -/
abbrev Prices := Fin 4 → Nat

/-- Componentwise composition of chronological ledgers. -/
def compose (a b : Ledger) : Ledger := fun i => a i + b i
/-- Invoice numerator in the common price unit. -/
def invoice (p : Prices) (a : Ledger) : Nat :=
  p 0 * a 0 + p 1 * a 1 + p 2 * a 2 + p 3 * a 3

/-- Splitting a trajectory into segments cannot change its invoice. -/
theorem invoice_compose (p : Prices) (a b : Ledger) :
    invoice p (compose a b) = invoice p a + invoice p b := by
  simp [invoice, compose, Nat.mul_add, Nat.add_assoc, Nat.add_left_comm]

/-- For a fixed trajectory ledger, increasing any prices cannot decrease the invoice. -/
theorem price_monotone (p q : Prices) (a : Ledger) (h : ∀ i, p i ≤ q i) :
    invoice p a ≤ invoice q a := by
  exact Nat.add_le_add
    (Nat.add_le_add
      (Nat.add_le_add (Nat.mul_le_mul_right (a 0) (h 0))
        (Nat.mul_le_mul_right (a 1) (h 1)))
      (Nat.mul_le_mul_right (a 2) (h 2)))
    (Nat.mul_le_mul_right (a 3) (h 3))

/-- A componentwise worse ledger is never cheaper under nonnegative prices. -/
theorem ledger_monotone (p : Prices) (a b : Ledger) (h : ∀ i, a i ≤ b i) :
    invoice p a ≤ invoice p b := by
  exact Nat.add_le_add
    (Nat.add_le_add
      (Nat.add_le_add (Nat.mul_le_mul_left (p 0) (h 0))
        (Nat.mul_le_mul_left (p 1) (h 1)))
      (Nat.mul_le_mul_left (p 2) (h 2)))
    (Nat.mul_le_mul_left (p 3) (h 3))

/-- Prices act linearly on a fixed ledger, independently of all state dynamics. -/
theorem invoice_price_add (p q : Prices) (a : Ledger) :
    invoice (fun i => p i + q i) a = invoice p a + invoice q a := by
  simp [invoice, Nat.add_mul, Nat.add_assoc, Nat.add_left_comm]

/-- Rescaling every price rescales the invoice, without changing its physical ledger. -/
theorem invoice_price_scale (k : Nat) (p : Prices) (a : Ledger) :
    invoice (fun i => k * p i) a = k * invoice p a := by
  simp [invoice, Nat.mul_add, Nat.mul_assoc]

/-- A policy minimizing two price vectors also minimizes their sum.
This is the integer-price version of the convex-cone structure of policy regions. -/
theorem minimizer_price_add {α : Type} (a : α → Ledger) (chosen : α)
    (p q : Prices) (hp : ∀ x, invoice p (a chosen) ≤ invoice p (a x))
    (hq : ∀ x, invoice q (a chosen) ≤ invoice q (a x)) :
    ∀ x, invoice (fun i => p i + q i) (a chosen) ≤
      invoice (fun i => p i + q i) (a x) := by
  intro x
  rw [invoice_price_add, invoice_price_add]
  exact Nat.add_le_add (hp x) (hq x)

/-- Every nonnegative common price scale preserves an already minimizing policy. -/
theorem minimizer_price_scale {α : Type} (a : α → Ledger) (chosen : α)
    (p : Prices) (k : Nat) (hp : ∀ x, invoice p (a chosen) ≤ invoice p (a x)) :
    ∀ x, invoice (fun i => k * p i) (a chosen) ≤
      invoice (fun i => k * p i) (a x) := by
  intro x
  rw [invoice_price_scale, invoice_price_scale]
  exact Nat.mul_le_mul_left k (hp x)

/-- Optimizing after adding prices cannot beat the sum of separately optimized values.
Together with positive homogeneity this is the finite rational form of concavity.
No existence assumption is needed for the combined-price minimizer: every candidate
already satisfies the lower bound, so taking its minimum preserves the inequality. -/
theorem optimized_price_superadditive {α : Type} (a : α → Ledger)
    (bestP bestQ candidate : α) (p q : Prices)
    (hp : ∀ x, invoice p (a bestP) ≤ invoice p (a x))
    (hq : ∀ x, invoice q (a bestQ) ≤ invoice q (a x)) :
    invoice p (a bestP) + invoice q (a bestQ) ≤
      invoice (fun i => p i + q i) (a candidate) := by
  rw [invoice_price_add]
  exact Nat.add_le_add (hp candidate) (hq candidate)
/-- Sum a finite list without requiring a measure-theory library. -/
def sumBy {α : Type} (xs : List α) (f : α → Nat) : Nat :=
  (xs.map f).foldr (· + ·) 0

/-- Finite sums distribute over pointwise addition. -/
theorem sumBy_add {α : Type} (xs : List α) (f g : α → Nat) :
    sumBy xs (fun x => f x + g x) = sumBy xs f + sumBy xs g := by
  induction xs with
  | nil => simp [sumBy]
  | cons x xs ih =>
    simpa [sumBy, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using ih

/-- A fixed scalar can be moved outside a finite sum. -/
theorem sumBy_mul {α : Type} (xs : List α) (k : Nat) (f : α → Nat) :
    sumBy xs (fun x => k * f x) = k * sumBy xs f := by
  induction xs with
  | nil => simp [sumBy]
  | cons x xs ih => simpa [sumBy, Nat.mul_add] using congrArg (fun n => k * f x + n) ih

/-- Probability numerator weights; normalization uses one common positive denominator. -/
def expectedLedger {α : Type} (xs : List α) (w : α → Nat)
    (a : α → Ledger) : Ledger := fun i => sumBy xs (fun x => w x * a x i)

/-- Exact finite expected invoice linearity, proved before dividing by the denominator. -/
theorem expected_invoice {α : Type} (xs : List α) (w : α → Nat)
    (a : α → Ledger) (p : Prices) :
    invoice p (expectedLedger xs w a) = sumBy xs (fun x => w x * invoice p (a x)) := by
  simp only [invoice, expectedLedger, Nat.mul_add]
  rw [sumBy_add, sumBy_add, sumBy_add]
  simp only [← sumBy_mul]
  simp [Nat.mul_comm, Nat.mul_left_comm]

/-- Summing an empty occupancy row contributes no residency. -/
theorem sumBy_zero {α : Type} (xs : List α) : sumBy xs (fun _ => 0) = 0 := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simpa [sumBy] using ih

/-- Weighted context occupancy can be counted by requests or by artifact lifetimes. -/
theorem occupancy_exchange {α β : Type} (requests : List α) (files : List β)
    (resident : α → β → Nat) :
    sumBy requests (fun t => sumBy files (resident t)) =
      sumBy files (fun j => sumBy requests (fun t => resident t j)) := by
  induction requests with
  | nil =>
    change 0 = sumBy files (fun _ => 0)
    exact (sumBy_zero files).symm
  | cons t ts ih =>
    change sumBy files (resident t) + sumBy ts (fun s => sumBy files (resident s)) =
      sumBy files (fun j => resident t j + sumBy ts (fun s => resident s j))
    rw [sumBy_add, ih]

/-- A positive rational trigger num/den in the half-open cell (k-1,k]
has exactly the same gate as integer k at every integer context x. -/
theorem rational_cell_gate (num den k x : Nat) (positiveDen : 0 < den)
    (lower : (k - 1) * den < num) (upper : num ≤ k * den) :
    (num ≤ x * den) ↔ (k ≤ x) := by
  constructor
  · intro hx
    have productLt : (k - 1) * den < x * den := Nat.lt_of_lt_of_le lower hx
    have predecessorLt : k - 1 < x := (Nat.mul_lt_mul_right positiveDen).mp productLt
    cases k with
    | zero => exact Nat.zero_le x
    | succ predecessor => simpa using Nat.succ_le_of_lt predecessorLt
  · intro hx
    exact Nat.le_trans upper (Nat.mul_le_mul_right den hx)

/-- Any finite threshold decision program after fixing its external trajectory.
Future contexts and terminal ledgers may differ arbitrarily between branches.
No independence, stationary growth, or fixed restoration volume is assumed.
Only threshold dependence through integer context comparisons is represented. -/
inductive ThresholdTree where
  | leaf (ledger : Ledger)
  | branch (context : Nat) (compact proceed : ThresholdTree)

/-- Execute a finite decision tree with an exact rational trigger num/den. -/
def evalRational (num den : Nat) : ThresholdTree → Ledger
  | .leaf ledger => ledger
  | .branch x compact proceed =>
      if num ≤ x * den then evalRational num den compact else evalRational num den proceed

/-- Execute the same tree with an integer trigger k. -/
def evalInteger (k : Nat) : ThresholdTree → Ledger
  | .leaf ledger => ledger
  | .branch x compact proceed =>
      if k ≤ x then evalInteger k compact else evalInteger k proceed

/-- Threshold quantization is exact for an arbitrary finite decision tree.
Thus every represented pathwise ledger is constant within each rational ceil cell. -/
theorem tree_cell_ledger (tree : ThresholdTree) (num den k : Nat)
    (positiveDen : 0 < den) (lower : (k - 1) * den < num)
    (upper : num ≤ k * den) :
    evalRational num den tree = evalInteger k tree := by
  induction tree with
  | leaf ledger => rfl
  | branch x compact proceed compactIH proceedIH =>
      simp only [evalRational, evalInteger]
      simp only [rational_cell_gate num den k x positiveDen lower upper, compactIH, proceedIH]

/-- Two exact rational thresholds in the same ceil cell produce identical ledgers. -/
theorem same_cell_ledger (tree : ThresholdTree) (n₁ d₁ n₂ d₂ k : Nat)
    (positive₁ : 0 < d₁) (lower₁ : (k - 1) * d₁ < n₁) (upper₁ : n₁ ≤ k * d₁)
    (positive₂ : 0 < d₂) (lower₂ : (k - 1) * d₂ < n₂) (upper₂ : n₂ ≤ k * d₂) :
    evalRational n₁ d₁ tree = evalRational n₂ d₂ tree := by
  rw [tree_cell_ledger tree n₁ d₁ k positive₁ lower₁ upper₁,
      tree_cell_ledger tree n₂ d₂ k positive₂ lower₂ upper₂]

/-- The quantized ledger yields exactly the same invoice at every nonnegative price. -/
theorem tree_cell_invoice (tree : ThresholdTree) (p : Prices) (num den k : Nat)
    (positiveDen : 0 < den) (lower : (k - 1) * den < num)
    (upper : num ≤ k * den) :
    invoice p (evalRational num den tree) = invoice p (evalInteger k tree) := by
  rw [tree_cell_ledger tree num den k positiveDen lower upper]

/-- Any fixed finite correlated task law inherits exact threshold-cell constancy.
The weights need not factor over events and are not required to be uniform. -/
theorem expected_tree_cell {α : Type} (xs : List α) (w : α → Nat)
    (trees : α → ThresholdTree) (num den k : Nat)
    (positiveDen : 0 < den) (lower : (k - 1) * den < num)
    (upper : num ≤ k * den) :
    expectedLedger xs w (fun x => evalRational num den (trees x)) =
      expectedLedger xs w (fun x => evalInteger k (trees x)) := by
  have functionsEqual : (fun x => evalRational num den (trees x)) =
      (fun x => evalInteger k (trees x)) := by
    funext x
    exact tree_cell_ledger (trees x) num den k positiveDen lower upper
  rw [functionsEqual]
/-- Uniform two-sided surrogate error transfers approximate optimality to exact regret.
Costs and error use common nonnegative rational numerator units. This theorem does
not establish the approximation error for any particular context model. -/
theorem approximation_optimization_transfer {α : Type}
    (exactCost approximateCost : α → Nat) (error : Nat) (chosen : α)
    (exactUpper : ∀ x, exactCost x ≤ approximateCost x + error)
    (approximateUpper : ∀ x, approximateCost x ≤ exactCost x + error)
    (chosenOptimal : ∀ x, approximateCost chosen ≤ approximateCost x) :
    ∀ y, exactCost chosen ≤ exactCost y + 2 * error := by
  intro y
  have first := exactUpper chosen
  have second := chosenOptimal y
  have third := approximateUpper y
  calc
    exactCost chosen ≤ approximateCost chosen + error := first
    _ ≤ approximateCost y + error := Nat.add_le_add_right second error
    _ ≤ (exactCost y + error) + error := Nat.add_le_add_right third error
    _ = exactCost y + 2 * error := by simp [Nat.two_mul, Nat.add_assoc]
/-- Strict reset controller phases; execution is distinct from prerequisite restoration. -/
inductive Phase where
  | missing
  | ready
  | done
  deriving DecidableEq, Repr

/-- Rechecking after restoration compacts again if the mandatory restored size reaches h.
The reset destroys the prerequisite. No progress occurs in either housekeeping phase. -/
def strictStep (h restoredSize : Nat) : Phase → Phase
  | .missing => .ready
  | .ready => if h ≤ restoredSize then .missing else .done
  | .done => .done

/-- Execute exactly n controller microsteps, not n ordinary task actions. -/
def iterateStrict (h r : Nat) : Nat → Phase → Phase
  | 0, s => s
  | n + 1, s => strictStep h r (iterateStrict h r n s)

/-- A strict reset loop can never execute when restoration itself reaches the trigger.
This holds for every finite attempt bound, not just a chosen numerical example. -/
theorem strict_obstruction (h r : Nat) (blocked : h ≤ r) (n : Nat) :
    iterateStrict h r n .missing ≠ .done := by
  induction n with
  | zero => simp [iterateStrict]
  | succ n ih =>
    simp only [iterateStrict]
    cases hs : iterateStrict h r n .missing with
    | missing => simp [strictStep]
    | ready => simp [strictStep, blocked]
    | done => exact False.elim (ih hs)

/-- Six-action exact control: each action grows context by one, carries current context,
and resets to zero with overhead four when its pre-action length reaches h. -/
def fixtureCost (h : Nat) : Nat → Nat → Nat
  | 0, _ => 0
  | n + 1, x =>
      if h ≤ x then 4 + fixtureCost h n 1
      else x + fixtureCost h n (x + 1)

/-- Even deterministic admissible tasks do not make threshold cost globally decreasing. -/
theorem threshold_not_decreasing : fixtureCost 3 6 0 < fixtureCost 4 6 0 := by decide
/-- Nor is threshold cost globally increasing: it can have a genuine interior minimum. -/
theorem threshold_not_increasing : fixtureCost 3 6 0 < fixtureCost 2 6 0 := by decide

#print axioms invoice_compose
#print axioms price_monotone
#print axioms ledger_monotone
#print axioms invoice_price_add
#print axioms invoice_price_scale
#print axioms minimizer_price_add
#print axioms minimizer_price_scale
#print axioms optimized_price_superadditive
#print axioms sumBy_add
#print axioms sumBy_mul
#print axioms sumBy_zero
#print axioms expected_invoice
#print axioms occupancy_exchange
#print axioms rational_cell_gate
#print axioms tree_cell_ledger
#print axioms same_cell_ledger
#print axioms tree_cell_invoice
#print axioms expected_tree_cell
#print axioms approximation_optimization_transfer
#print axioms strict_obstruction
#print axioms threshold_not_decreasing
#print axioms threshold_not_increasing
end ContextCompaction
