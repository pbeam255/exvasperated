# Electronic solution first-pass review

Reviewed 2026-09-24 against the quarantined VASP 6.5.1 source and the
[first-pass report](../electronic-solution.md). This is the single independent
review at depth one requested for this study. No child review, build, execution
or numerical experiment was performed.

## Finding

No correction is required to the material claims checked in this review.
The report distinguishes outer termination, inner solver progress and scientific
accuracy; its source-level failure concern is supported without claiming that
a numerical failure has been reproduced.

## Claims checked

- **Outer convergence and termination.** `electron_common.F` 15–65 compares
  two supplied energy measures, applies mixing and iteration constraints, and
  distinguishes an iteration-cap exit from satisfying the threshold. The
  one-step exception and external stop are present. `electron.F` 639–650 and
  719 pass the total-energy difference and band-solver measure; charge formation
  and mixing follow under separate conditions at 777–850. These bodies support
  the report's warning against interpreting the common exit flag as density
  convergence.
- **Solver scheduling and exchange.** `electron.F` 414–449 and 485–596 support
  the solver dispatch, combined-method delay, compatibility-dependent argument
  and compressed-exchange observations. `david_full.F` 209–215 checks the
  relevant active exchange combination at entry. The report correctly leaves
  these as implementation constraints rather than universal properties of the
  algorithms.
- **PAW metric and residual construction.** `davidson.F` 494–620 builds
  overlap and Hamiltonian subspace quantities with projector contributions and
  reductions. `steep.F` 225–280 shows the additional eigenvalue subtraction
  before preconditioning. `david_full.F` 2145–2250 supports the local
  generalized-solver status check and conditional result broadcast.
  `subrot.F` 600–763 and 1917–1958 support the distinct diagonalization routes
  and limited approximate rotation.
- **Different inner stopping and failure behavior.** `davidson.F` 569–573
  and 741–780 support occupation-weighted residual reporting and the selected
  eigenvalue-change stopping rules. `david_full.F` 220–282 and 569–592
  distinguish strict and loose state groups and additional residual/history
  checks. `rmm-diis.F` 486–520 and 673–717 show the affected-band response to
  an eigensolver failure and the optional-bound dependence of stopping.
  `david_inner.F` 699–738 supports the smaller-subspace retry. The report does
  not imply a shared recovery contract across these methods.
- **Mixer state.** `mix.F` 23–191 and `broyden.F` 100–238, 335–421,
  465–513, 554–670 and 1210–1274 support the smooth, PAW and optional kinetic
  state, the reciprocal weighting, persistent history, reset/capacity handling
  and distinct origin treatment described. The short storage include was also
  inspected. Full Broyden update algebra remains outside this review.
- **Atomic DIIS concern.** `diis.F` 166–257 can return from the constrained
  solve before defining a new result. The enclosing step does not consume its
  error status. Call searches in `rhfatm.F` locate atomic density and orbital
  users. This supports the report's narrowly stated failure-propagation concern;
  it does not establish occurrence or quantify consequences for atomic inputs.
- **Occupations and integration.** `dos.F` 637–845 supports the selected
  occupation/DOS dispatch and entropy accumulation. `electron.F` 639–641
  includes that contribution in the assembled energy. `fermi_energy.F`
  139–303 and 412–509 support the band-edge midpoint, bisection, attainable
  counting tolerance, communicator compensation, tail handling and distinct
  host/device error-function calls. `tet.F` 406–453 and 505–537 supports
  degeneracy correction and spin/sampling normalization. The report preserves
  zero-weight input handling and integration accuracy as open questions.
- **Separate electronic loops.** `electron_all.F` 438–473 and 600–661
  support its corrector and separate convergence logic. `rot.F` 269–323,
  1180–1258 and 1283–1375 support the bounded step adjustment, subspace and
  projector transformations, orthogonalization and auxiliary-state update.
  `electron_OEP.F` 597–689 and `electron_lhf.F` 433–480 support the distinct
  response-based and local-exchange work. `subrot_scf.F` 430–465 has the
  additional relative density-norm exit described in the report.
- **Ancillary scope and execution limits.** `bandgap_tools.F` 37–80 and
  221–279 supports the sorting requirement and occupation/local-Fermi
  classifications. `elf.F` 245–294 contains the density division before the
  separate final scale floor. `stm.F` 110–115 supports the stated parallel
  restriction. Selected `pardens.F` and `ini.F` bodies match their limited
  scope descriptions. The offload-dependent branch changes in `david_full.F`
  1096–1099 and 2190–2191 are present; they establish no hardware execution
  or performance result.

## Review limits

The inventory has 26 entries assigned to this partition, matching the report's
file coverage table. That cross-check establishes navigation coverage only.
This review sampled the material claims above; it did not independently repeat
every declaration scan or examine every body listed in the report.

No full derivation of the minimizers, generalized metric transformations,
integration formulas or density-mixing update was attempted. Complete failure
propagation through outer callers, distributed status consistency, restart
behavior, zero-density and zero-weight domains, and CPU/NVIDIA/AMD numerical
agreement remain unresolved. No proprietary source, comments or diagnostics
were reproduced in this review artifact.
