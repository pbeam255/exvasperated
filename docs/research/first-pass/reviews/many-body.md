# Screening, quasiparticles and many-body response first-pass review

Reviewed 2026-09-24 against quarantined VASP 6.5.1 and the
[first-pass report](../many-body.md). This is the requested single independent
review at depth one. No child review, build or scientific experiment was run.

## Findings

No correction is required for the substantive claims checked. The report
consistently distinguishes sampled implementation behavior from complete
method coverage and observed scientific failures. Its local concerns are
supported without establishing their effects on a reachable calculation.

## Material claims checked

- **Method and state preparation.** `chi_glb.F` 911–1043 supports the separate
  method flags and method-dependent settings. `chi.F` 477–543 supports
  conditional occupation and chemical-potential updates, wave synchronization,
  symmetry-dependent merging of nearby eigenvalues and the preparation of
  Hartree/kinetic and exchange components. Lines 2045–2128 support the distinct
  self-energy paths and later layout/wave reconstruction. The report does not
  infer a complete iteration contract from those fragments.
- **Response construction and inversion.** `chi_base.F` 335–403 supports the
  occupation or imaginary-time filters, optional one-center pair density,
  phase application and reciprocal extraction. Lines 706–719 confirm that
  the later purely imaginary-frequency condition is already covered by the
  first branch. `chi.F` 3885–3917 supports the signed, Coulomb-scaled response
  plus identity and separate head/wing handling. Lines 4394–4437 support
  directional inversions and averaging at Gamma, with checked factorization
  and inversion status. The thresholded Hermitian inverse instead suppresses
  eigenvalues whose magnitudes fall below the supplied threshold
  (`chi_base.F` 2866–2888). These are distinct operations, as reported.
- **Head-index concern.** The six assignments in `chi.F` 4417–4418 repeat
  one off-diagonal position and leave its transpose unassigned by that group.
  The report correctly leaves initialization, later use and observable impact
  unresolved. This review did not establish an anisotropic-response failure.
- **Screened storage and reconstruction.** `screened_2e.F` 382–434 supports
  mapped reciprocal/band storage and accumulation from a higher-precision
  input into a lower-precision complex array. `wpot.F` 311–425 supports lazy
  loading, reciprocal-coordinate and size checks, grid/long-wave scaling,
  phase-dependent symmetry reconstruction and the shared-memory barrier.
  Full restart and cache-lifetime contracts remain outside the checked scope.
- **Real-space restrictions and imaginary grids.** `chi_GG.F` 262–282 and
  `chi_super.F` 251–282 support the route-specific reciprocal-group,
  noncollinear, finite-temperature smearing and spin-population restrictions.
  The first route has exceptions to its reciprocal-group restriction; the
  report's method-specific wording preserves that distinction.
  `greens_real_space.F` 205–261 supports the one-electron dispatch, separate
  correlated-target selection and self-consistent constrained-screening
  rejection. The following matrix-transform route at 267–310 was also
  inspected as immediate control context. `GG_base.F` 581–600 supports
  divisibility/layout-based process selection. `minimax.F` 91–180 supports
  separate quadratures, transformations and recorded transform errors.
  Both near-origin reciprocal helpers return zero in the sampled interval
  (`minimax_functions1D.F` 42–70).
- **Continuation and root policy.** `pade_fit.F` 1543–1610 supports the fixed
  displacement, three stencil choices and derivative-based renormalization.
  Lines 1716–1775 support a bracket search that expands only until candidates
  are found or its bound is reached, Brent solves, selection by proximity to
  the supplied reference and sentinel returns on the sampled failure paths.
  The selected result is then used for continued-self-energy and slope
  evaluation. The report appropriately leaves multiple-root physics,
  continuation artifacts and downstream sentinel handling unresolved.
- **Trace-log terms and constrained weights.** `acfdt.F` 510–522 and
  `esf.F` 710–722 support omission of inadmissible terms in the sampled
  non-second-order branch. The guard tests an unscaled eigenvalue while the
  logarithm includes coupling scaling; the report preserves this question.
  The companion linear or second-order contribution is also inside that
  branch. `crpa.F` 1535–1577 supports diagonal projector weights,
  threshold-selected band bounds and a near-zero trace diagnostic rather
  than an explicit target-rank equality check. `gw_model.F` 488–510 supports
  the density magnitude and floor used by its local model.
- **Electron–hole solvers.** `chi.F` 1206–1270 supports old/new solver and
  spin dispatch. The device-memory decision is conditional on an accelerator
  build, available devices and the selected diagonalization route
  (`bse_driver.F` 567–584). Its coupled-block transformations and two
  diagonalizations followed by square roots are present at 1418–1454.
  `bse.inc` 6–55 supports the precision selection. `bse_lanczos.F` 277–298
  supports resetting the beyond-resonant request; 481–522 supports
  consecutive-vector orthogonality checks and periodic stopping based on the
  first three spectral-change measures. Lines 627–684 confirm broadening
  and the RMS imaginary-spectrum measure. The report correctly distinguishes
  this stopping rule from an eigenpair residual or all-component error bound.
- **Electronic time evolution.** `time_propagation.F` 208–245 supports
  rebuilding charge/potential and enabling both Hartree and XC feedback when
  either is selected. The report makes no unsupported statement about the
  unread propagation integrator or its equivalence to BSE time evolution.
- **Second-order methods and statistics.** `mp2.F` 535–569 and
  `ump2kpar.F` 650–684 support the virtual-state filters, negative-denominator
  branch and long-wave derivative corrections. The differing occupation
  indices are present; the report correctly asks for reciprocal/spin mapping
  analysis before judging equivalence or failure. `ump2no.F` 721–750
  supports the additional virtual-state filters. `lt_mp2.F` 1545–1573
  supports the inverse-cutoff-power linear fit and intercept.
  `rnd_orb_mp2.F` 172–202 supports sums over time/transfer indices and
  quadrature addition of the reported errors, including direct/exchange
  totals. Independence and covariance are not established by those sums.
- **Conditional stubs and derivative preparation.** `rpax.F` 75–107
  supports the empty entry for Gamma-real builds or missing MPI/ScaLAPACK.
  `rpa_force.F` 73–156 supports the empty interfaces without ScaLAPACK.
  `rpa_high.F` 508–547 supports guarded band-count restoration, descriptor
  setup, wave copying and exchange-data reset. `auger.F` 2564–2588 supports
  the stated carrier-density selection, occupation factors, reciprocal
  weights, spin factor and volume normalization. It does not establish the
  four-state rate kernel, as the report explicitly acknowledges.

## Review limits

The reading-scope table lists exactly the inventory's 42 assigned files,
totaling 157,269 lines. The two large minimax initialization/dependence files
account for the reported 46,260 lines. These checks establish navigation
coverage only. This review checked representative substantive claims and
immediate control/build context; it did not repeat every declaration read,
derive every method, inspect all coefficient records or establish every caller.

No energy, quasiparticle, spectrum, force, instability, stochastic estimator
or CPU/NVIDIA/AMD workload was tested. Full kernels, numerical domains,
continuation failure propagation, constrained-space rank, Krylov breakdown,
occupation mappings and statistical covariance remain follow-up questions.
No proprietary source, comments, diagnostics or datasets were copied into this
review artifact.
