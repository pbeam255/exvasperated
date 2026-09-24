# Forces, cell stress and ionic motion: first pass

Reference: quarantined VASP 6.5.1, inspected 2026-09-24. The `ions` partition
contains 15 files and 18,470 lines; identities are in the
[inventory](../vasp-source-inventory.csv). This is original source analysis.
No trajectory, relaxation, finite-difference check or hardware experiment ran.

## Reading scope

Procedure/dependency maps were followed with selected body reads. These are
partial studies, including where small complete helpers were examined.

| Files | Inspected body scope; remaining limits |
| --- | --- |
| `force.F` | Kinetic stress 340–423; local-force accumulation 800–848; assembly 1300–1782, output fragments 1840–1953; dispersion preparation 2002–2070 and accumulation 2120–2148; kinetic-pressure reporting 2536–2597. Most individual derivative kernels remain unread. |
| `dyna.F` | Initialization 66–160, 199–249; optimizer state 534–615, 674–731, 865–938; selective motion 1197–1257. Line search, damping, velocity projection and correlation functions remain partial. |
| `dynbr.F` | Joint ion/cell adapter 47–188; update fragments 268–375, 379–510. Full history lifecycle and inversion remain partial. |
| `stepver.F` | Integrator body 58–234. Caller initialization and all continuation combinations remain open. |
| `dynconstr.F` | Driver fragments 298–348, 475–536, 580–673; stochastic/constraint step 1660–1785; cell restriction 2452–2477; bias history 3871–3895, 3912–3964. Most of this 6,373-line file, including complete thermostat splittings and constraint solves, remains unread. |
| `npt_dynamics.F` | Pressure body 176–244 and cell reconstruction 1382–1462. Extended-system equations, initialization and integration remain mostly unread. |
| `internals.F` | Coordinate geometry 663–785 and rank reduction 1939–1968. Readers and most coordinate Jacobians remain unread. |
| `gadget.inc`, `hills.inc` | Shared type declarations; embedded element tables noticed but not assessed or adopted. Ownership and full consumers remain partial. |
| `chain.F` | Force paths 76–270; replica-temperature exchange 423–511. Setup, endpoint handling and full cell coupling remain partial. |
| `dimer_heyden.F` | Entry/stop 57–147; operation fragments 180–258; translation 455–527. Full rotation, initialization and recovery remain partial. |
| `dvvtrajectory.F` | State 100–137; adaptive step/stop 177–265. Initialization, input and complete trajectory interpretation remain open. |
| `paircorrection.F` | Pair entry 545–566; periodic sum 617–691; interpolation 733–756. Other collective fields and full force accumulation remain unread. |
| `random.F` | Types and input 34–177; ionic state/reset 203–298; scalar generation 333–389; normal variate 403–421. Remaining generators and complete consumer graph remain unread. |
| `constr_cell_relax.F` | Complete file; active body 27–42 is an empty hook. |

Cross-partition reads followed the ionic driver in `main.F` 3868–3912,
4350–4445 and 4514–4562. They establish ordering and stopping behavior, not a
complete main-loop audit.

## Force evaluation consumes and changes electronic state

The force driver resets output arrays and can return before any evaluation when
forces are disabled. Otherwise it saves density and optional kinetic-density
state and may reconstruct charge from orbitals. Local, nonlocal-projector,
augmentation, exchange, partial-core and additional field contributions have
separate calls (`force.F` 1385–1603). In one real-space projector route it
temporarily substitutes reference positions, evaluates using displacements,
then restores the pointer (1473–1477). Correctness depends on which geometry
each cached representation describes.

The driver also rebuilds atomic operator matrices and can invalidate the
potential. After force corrections it either mixes charge/augmentation state
or restores the saved state. Within the selected mixing branch, an ionic-mode
condition can skip the mixing calls without entering the saved-state restoration
branch (1626–1670). A force evaluation is consequently more than a read-only mapping
from a geometry to a vector. The electronic study's outer stopping condition
does not prove the stationarity or density consistency needed here.

The sampled local-force kernel contracts Fourier density with ion-dependent
phase factors, multiplies reciprocal indices and converts the reduced result
through the reciprocal basis (`force.F` 800–848). The kinetic-stress body uses
wavevector dyadics, including spin-spiral shifts, and orbital norms weighted by
occupations and reciprocal-point weights (340–423). These connect derivative
normalization to the representation and sampling studies. Complete PAW,
overlap-metric and finite-basis derivatives remain to be derived jointly.

The assembled force includes external ionic forces, electrostatic corrections,
optional electric-field response, collective fields, solvation and dispersion.
Plugins can subsequently modify energy, forces and stress. Symmetry is applied
after these additions, and drift removal depends on the motion/compatibility
conditions (`force.F` 1677–1724). A test of the final vector alone would not
identify which constituent derivative, projection or state transition failed.

## Stress has units, composition and measurement context

The electronic cell-stress accumulator sums several extensive contributions.
Dispersion adds directly to it (`force.F` 2120–2135), and reporting multiplies
by an energy-to-pressure conversion divided by cell volume (1738–1739).
This resolves the immediate nonlocal-study question about why external
dispersion adapters did not themselves divide lattice derivatives by volume.
The full sign and tensor convention of each external adapter still needs an
energy-under-strain derivation.

External pressure enters the scalar pressure and later the cell-driving tensor.
The molecular-dynamics output helper adds an ionic kinetic contribution for
reporting but does not assign it back into the supplied electronic stress
(`force.F` 2536–2597). The sampled variable-cell dynamics instead combines
kinetic, lattice and constraint stresses in its own metric-based pressure
expression (`npt_dynamics.F` 199–244). Printed pressure, electronic stress and
the integrator's driving variable are therefore distinct quantities.

The variable-cell reconstruction takes square roots and divisions of metric
components before applying a rotation (1441–1461). Positive definiteness and
a nonsingular cell are necessary domains of those operations. Where the full
integrator enforces or diagnoses these domains was not traced.

## Ionic stopping is conditional on the selected motion

In the sampled relaxation driver, the force criterion compares each atom's
Cartesian force norm with a threshold magnitude. When the cell moves, it also
checks components of the restricted cell-driving tensor after the prescribed
scaling and normalization by atom count (`main.F` 4364–4417). This is not
simply a maximum stress in pressure units.

A positive threshold instead starts with an energy-change test; optimizers
can supplement it with expected-change tests. For a negative threshold the
final decision is replaced by the force/cell criterion. Decisions are combined
across images (`main.F` 4423–4438, 4524–4557). Thus a generic label such as
“relaxation converged” hides method, allowed degrees of freedom and stopping
reason. It also does not classify a stationary point as a minimum.

The quasi-Newton adapter packs ionic fractional coordinates and cell vectors
into one optimization state, using a metric for ionic inner products and
separate force/cell scaling (`dynbr.F` 47–188). Its history update can discard
older directions according to a generalized eigenvalue calculation. Two local
questions are concrete: normalization divides by the norm of a force difference
without a guard in the sampled body (295–302), and the non-ESSL eigensolver
status is not checked before its results are consumed (387–419). Reachability,
outer stopping and the numerical library contract remain to be traced before
asserting a reproduced failure.

The conjugate-gradient path keeps trial, direction and curvature state across
calls and couples cell and ionic directions (`dyna.F` selected ranges).
Continuation must account for such optimizer history separately from geometry
and electronic restart files. The full line-search acceptance rules remain
unread.

## Constraints operate in several coordinate systems

Selective motion zeros velocity components in fractional coordinates. For
forces it first transforms to that coordinate representation, zeros selected
components and transforms back (`dyna.F` 1197–1257). In a skew cell this needs
an explicit derivation of the intended constrained motion; treating these
flags as Cartesian component masks would change behavior.

The main driver applies those restrictions around chain corrections, with
exceptions for selected derivative workflows (`main.F` 3876–3905). The empty
cell-constraint hook in `constr_cell_relax.F` does not mean there are no cell
constraints: a separate helper zeros rows and columns of a cell update for
fixed axes (`dynconstr.F` 2463–2477). The main loop additionally restores
volume for selected cell modes (`main.F` 4528–4540).

Internal-coordinate geometry includes distances, angles, torsions and cell
quantities. Some angle calculations clamp inverse-cosine arguments, while
normalizations can still be singular for coincident atoms or collinear bonds
(`internals.F` 663–785). A transformation helper constructs a Gram matrix and
retains singular directions above a fixed threshold (1939–1968). Coordinate
units, redundant constraints, rank decisions and topology changes need a
joint analysis with the remaining Jacobian and constraint-solver bodies.

## Dynamics includes multiple clocks and persistent states

The older integrator stores velocities as fractional displacements scaled by
the time step, with kinetic-energy conversion using the cell. It iterates a
velocity/thermostat correction at most eleven times and then proceeds whether
the local tolerance or the iteration limit ended that loop (`stepver.F`
117–164). Its sampled position update wraps by at most one cell per component
(198–205). These imply bounded-displacement and correction-convergence
questions; they do not establish a problem on normal trajectories.

The larger dynamics driver dispatches stochastic, thermostat-chain,
rescaling, biased, subsystem and variable-cell paths (`dynconstr.F` 580–661).
The sampled stochastic path adds random and deterministic increments, applies
bias contributions and iterates friction with a velocity constraint solve.
That loop has an explicit iteration-limit error path (1660–1749). Its
convergence contract differs from the older integrator. Complete ensemble
measures and finite-time-step behavior require deriving each splitting, not
inferring them from the method selector.

Bias history also changes the trajectory's state. The sampled deposition
routine stores earlier collective-coordinate positions, adjusts widths in one
mode and accumulates forces from prior deposits (`dynconstr.F` 3871–3964).
The include files carry pointer-owned coordinate, topology, bias and auxiliary
thermostat arrays. Restart equivalence must include these histories, constraint
state and thermostat/barostat momenta; the present pass does not establish
which are serialized.

Randomness is another continuation contract. `random.F` maintains separate
wave and ion generators; its ionic wrapper can encode a seed and draw count
and recreate state by replaying draws (203–267). Another ion variate helper
accesses the underlying generator directly. Complete consumer accounting is
needed before claiming that one recorded count reconstructs every stochastic
workflow. Input selection has build-dependent seeding and an alternative
generator route (104–177). The centered/scaled variate at 403–421 uses a
normal-distribution transform with a lower cutoff on one uniform draw, despite
the helper's generic naming. No statistical tests ran.

## Path searches and added classical fields are distinct workflows

The image-chain body assembles periodic displacements and tangents, then either
adds spring forces/energy or projects force components along the path according
to a sign-selected branch (`chain.F` 76–270). Its tangent denominator requires
nonzero neighboring-image distances before the later norm guard (147–156).
Coincident images and skew-cell image choices need caller/domain analysis.
Replica-temperature exchange separately gathers temperatures and energies,
selects exchanges probabilistically and rescales velocities (423–511).

The dimer path is a state machine alternating displaced force evaluations,
rotation and translation, with finite-difference curvature and capped steps.
Its entry rejects cell relaxation. The sampled force-based early exit can occur
before a fresh curvature estimate (`dimer_heyden.F` 92–119, 180–258, 455–527).
Finding a small force here is not by itself evidence of the required saddle
index; that scientific interpretation needs a separate curvature check.

The damped trajectory path fixes a velocity norm, adapts the time step from a
trajectory discrepancy and keeps energy history. Its stop helper accepts an
entire window with no decrease toward the newest entry, including equality
(`dvvtrajectory.F` 177–265). This is different from a force-stationarity test.
Zero velocity and zero discrepancy domains still need inspection.

The sampled tabulated pair correction uses a periodic sum, cubic interpolation
and a finite isotropic scaling to estimate a pressure quantity. It detects
nonorthogonal cell vectors but continues after a warning (`paircorrection.F`
617–691); interpolation zeros the tail and clamps its lower argument
(733–756). Actual call reachability and intended scientific domain remain open.
Other collective fields in that file are largely unread.

## Execution targets and return conditions

Force kernels include accelerator reductions, atomics, wave synchronization
and explicit host/device transitions. Ionic optimizers, small tensor operations,
randomness and persistent histories add separate host-side behavior. All three
alpha targets need force/strain consistency and complete trajectory workloads;
source inspection provides no CPU/NVIDIA/AMD execution evidence.

Return with vibrations and response for differentiated electronic state and
force constants; with numerical helpers for rank, inversion and constraint
failure semantics; and with input/output for complete continuation. The later
reference campaign should derive energy-force-stress consistency, constrained
stationarity, equilibrium measures, time-step errors and saddle classification.
The local singular-domain and ignored-status concerns need bounded experiments
only after caller conditions are established. Substantial bodies remain unread;
this useful first pass is not completion of the ionic study.

## Review disposition

The [single independent review](reviews/ions.md) requested a more precise
description of the ionic-mode condition that bypasses both mixing and saved-state
restoration. That state transition is now explicit above. Other sampled material
claims were supported. No second review or numerical experiment ran.
