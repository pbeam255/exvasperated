# Forces, cell stress and ionic motion first-pass review

Reviewed 2026-09-24 against the quarantined VASP 6.5.1 source and the
[first-pass report](../ions.md). This is the requested single independent
review at depth one. No child review, build, trajectory, relaxation or numerical
experiment was performed.

## Correction required

**Identify the state-restoration exception more precisely.** The force-state
section describes a “solver-dependent exception.” In `force.F` 1626–1656 the
outer condition selects the mixing branch; within its selected mixing method,
1630–1650 skips the mixing calls for one ionic mode. The saved-state restoration
at 1658–1670 belongs to the outer alternative and is also bypassed in this
case. Say that an ionic-mode condition can skip mixing without taking the
restoration branch. This clarifies which control governs the exception and
the resulting state transition; it does not establish a defect. The associated
setup also changes electronic iteration controls in `main.F` 1939–1942.

## Material claims checked

- **Force state and ordering.** `force.F` 1387–1435 supports clearing outputs,
  the early return, saving density/augmentation state and conditional charge
  reconstruction. Lines 1458–1503 support reference-geometry displacements,
  temporary projector-position association and reconstruction of atomic
  operator matrices. Lines 1561–1603 support potential rebuilding and
  invalidation. Lines 1626–1670 support the mixing/restoration account subject
  to the clarification above. Lines 1677–1724 support constituent accumulation,
  additional field and solvation contributions, dispersion, plugin changes,
  subsequent symmetry and conditional drift removal.
- **Derivative normalization and stress composition.** `force.F` 367–418
  contains reciprocal wavevectors with spin shifts, orbital coefficient
  magnitudes, occupation/sampling weights and accelerator/MPI reductions.
  Lines 814–842 support reciprocal-index contraction and basis conversion
  in the local-force kernel. Lines 1677–1739 and 2133–2135 support direct
  addition of dispersion to the extensive stress accumulator and the later
  volume-dependent pressure conversion. The report appropriately leaves each
  adapter's full sign and tensor derivation open.
- **Kinetic pressure and variable-cell domains.** `force.F` 2550–2593
  constructs a separate ionic kinetic contribution for output and does not
  write it into the supplied stress tensor. `npt_dynamics.F` 199–240 supports
  the distinct kinetic/lattice/constraint combination and metric contraction.
  Lines 1441–1461 support the stated square-root and nonsingularity domains
  of cell reconstruction. No enforcement of those domains was established.
- **Relaxation stopping.** `main.F` 4364–4417 checks Cartesian atomic force
  norms and the scaled, restricted cell-driving components. Lines 4423–4438
  support the energy-change condition, expected-change supplement and image
  combination. Lines 4524–4557 support the later image combination,
  selected volume restoration and final force-based replacement for a
  negative threshold. These conditions do not classify stationary points.
- **Optimizer state and local concerns.** `dynbr.F` 69–91 and 128–173
  support the fractional-coordinate/cell packing, metric and different
  scaling. Lines 295–307 contain force-difference normalization without a
  local zero-norm guard. Lines 363–419 contain history selection based on
  generalized eigenvalues and use the non-ESSL eigensolver's output without
  checking its returned status. The report correctly leaves caller conditions
  and reproducible consequences open. `dyna.F` 548–558, 674–728 and 902–934
  support persistent conjugate-gradient state and coupled ionic/cell updates.
- **Coordinate restrictions.** `dyna.F` 1210–1229 supports direct masking
  of stored fractional velocities and transformation/masking/back-transformation
  of forces. `main.F` 3878–3905 places these calls before and after the chain
  and exchange work with the stated exceptions. `constr_cell_relax.F` 27–42
  has no active adjustment; `dynconstr.F` 2463–2476 separately masks rows
  and columns. `internals.F` 663–784 supports distances, cell quantities,
  clamped atomic-angle/torsion arguments and the unresolved singular
  normalizations. Lines 1951–1965 support a Gram-matrix decomposition and
  fixed-threshold retention in the transformation helper.
- **Integrator and bias state.** `stepver.F` 141–164 supports eleven possible
  correction iterations and continuation after either convergence or
  exhaustion. Lines 198–205 support the bounded wrapping operation.
  `dynconstr.F` 587–661 supports the sampled method dispatch; 1664–1749
  supports bias, stochastic increments, friction iteration, the velocity
  constraint solve and its explicit limit error. Lines 3880–3886 and
  3912–3964 support persistent deposition state, conditional width changes
  and summation of previous deposits. The shared include declarations expose
  pointer-based coordinate, topology and bias state. Their full ownership and
  serialization remain outside the review.
- **Random continuation.** `random.F` 75–78 separates ion and wave generator
  instances. Lines 215–267 support count/seed recording, draw replay and the
  other ionic helper's direct use of the underlying generator. Lines 118–153
  support build-dependent seeding and alternate selection. Lines 403–419
  support the normal-variate transform with rejection below a positive
  uniform-draw cutoff. The report does not claim statistical validation or
  complete reconstruction of every stochastic consumer.
- **Chain and replica workflows.** `chain.F` 127–156 supports periodic
  displacements and a tangent denominator requiring nonzero adjacent-image
  distances before the later normalization guard. Lines 167–260 support the
  spring/sign-dependent projection and energy handling. Lines 423–501 support
  gathered energies/temperatures, probabilistic exchanges and velocity
  rescaling. The report's unresolved geometry and coincident-image questions
  are appropriately conditional.
- **Dimer and damped trajectory.** `dimer_heyden.F` 92–119 supports the
  cell-motion restriction and force-based return before the subsequent
  curvature work. Lines 191–258 and 465–526 support the operation state,
  finite-difference curvature and capped translations. `dvvtrajectory.F`
  198–225 supports velocity normalization and discrepancy-based time-step
  adaptation; 242–263 confirms newest-first energy history and acceptance of
  nondecreasing energy toward the newest entry, including equality. The report
  correctly distinguishes this from force stationarity and leaves singular
  domains unresolved.
- **Tabulated pair correction.** `paircorrection.F` 621–688 supports scaled
  periodic-distance evaluations, the nonorthogonality warning and continued
  calculation. Lines 739–754 support zeroing the tail, lower-argument clamping
  and cubic interpolation. Complete force accumulation, pressure derivation
  and workflow reachability remain outside the report's established claims.

## Review limits

The inventory contains all 15 files listed in the report, totaling 18,470
lines. This verifies navigation coverage only. Material claims were checked
through selected bodies and nearby control flow; this was not a full reread of
every reported range or an analysis of every derivative, thermostat, constraint
solver, optimizer or classical field.

No energy-force-strain consistency, equilibrium measure, trajectory accuracy,
restart equivalence, saddle index or execution-target comparison was tested.
The local domain/status observations establish questions for later study,
not reproduced scientific failures. No proprietary code, comments, diagnostic
text or parameter tables were copied into this review artifact.
