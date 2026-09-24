# Nonlocal exchange and dispersion first-pass review

Reviewed 2026-09-24 against the quarantined VASP 6.5.1 source and the
[first-pass report](../nonlocal-interactions.md). This is the single independent
review at depth one requested for this study. No child review, build, execution
or numerical experiment was performed.

## Corrections required

1. **Distinguish an inactive branch from an available selection.** The report
   says the many-body preparation “selects real-space or reciprocal-space
   evaluation.” In `vdwforcefield.F` 5287, the local real-space selector is
   initialized false. Its only other occurrence in the file is the branch at
   5356; it is neither an argument nor assigned from input. The inspected wrapper
   consequently takes the reciprocal-space branch at 5360–5362. State that the
   source contains both calls but that the inspected wrapper uses the reciprocal
   route. Availability through other callers remains outside this finding.

2. **Name the occupation condition for clearing compressed exchange.** The
   report says, “An empty construction space is handled by clearing the
   corresponding representation.” `fock_ace.F` 123–128 actually tests whether
   any state is considered occupied for the current reciprocal point and spin.
   It does not test whether the allocated construction basis has zero size.
   Replace this with an explicit statement that absence of occupied states
   triggers clearing. The distinction matters when following occupation changes
   and the separate choice of construction states.

3. **Describe the coefficient fallback as a threshold.** The report says the
   interpolation “falls back to the closest reference when weights underflow.”
   `subdftd3.F` 2549–2573 tracks the closest valid reference and falls back
   whenever the accumulated weight does not exceed a specified positive
   threshold. Floating-point underflow is not required. State that the fallback
   occurs when the accumulated weight is at or below that threshold.

4. **Describe the occupied-band bound precisely.** The report says, “The
   exchange-force entry counts relevant occupied states.” `fock_frc.F` 138–148
   finds the largest band index whose occupation magnitude exceeds the cutoff
   across reciprocal points and spins, then bounds the batch size with that
   index. Describe this as locating the highest retained band index rather than
   counting occupied states. This preserves the distinction for occupations that
   do not form a contiguous prefix.

## Material claims checked

- **Exchange setup and reciprocal interaction.** `fock.F` 1199–1244 supports
  the response/density-matrix dependency, dataset restriction, initial grid
  alias and precision-dependent allocation. Lines 1650–1774 support sampling
  and volume factors, the separately supplied near-origin contribution,
  screened/truncated/model branches, cutoffs and final normalization.
  Lines 2098–2170 support the report's bounded account of the singular
  contribution. The report correctly leaves the later reciprocal sum unread.
- **Orbital reconstruction and pair action.** `fock_dbl.F` 1189–1242
  supports full-point selection, representative mapping, spin reversal,
  symmetry reconstruction, occupation filtering and pair-charge construction.
  Lines 1244–1355 support transforms, interaction application, orbital-action
  accumulation and distinct accelerator batching. The report does not claim
  to have derived the partial-occupation energy expression.
- **Compressed operator algebra and force scope.** `fock_ace.F` 145–240
  supports the projected matrix, sign change, Cholesky/triangular work and
  transformation of action vectors. Lines 352–395 support the overlap,
  reduction, second product, negative action and weighted energy contribution.
  The report appropriately avoids claiming equivalence outside a demonstrated
  construction space. `fock_frc.F` 105–148 supports the conditional early
  returns and derivative-direction allocation, subject to correction 4 above.
  `fock_multipole.F` 1291–1327 contains the ten-component projected correction.
- **Atomic exchange and cache scope.** `pawfock.F` 34–114 supports the
  screened radial cache key and absence of an explicit radial-grid comparison
  in that key. Lines 437–506 support partial-wave products, angular selection,
  quadrature and additive accumulation. The called radial calculation at
  648–741 confirms the conditional screened and unscreened contributions.
  This extra inspection supports the interaction dependency without resolving
  normalization or caller invariants. `wpbe.F` 63–148 supports the functional
  restrictions, screening-dependent reuse and table construction.
- **Local potential concerns.** `pwlhf.F` 1539–1548 supports the collinear
  density guard. Lines 1572–1598 contain the unguarded division by magnetization
  magnitude and a spin-channel value assigned only above a density threshold,
  then used outside that condition. The report correctly calls these local
  source concerns and leaves caller restrictions and reachable inputs open.
- **Density-based correlation.** `vdw_nl.F` 231–286 and 519–590 support
  the windowed kernel tables, reciprocal truncation, spline work and finite
  differences. Lines 1169–1338 and 1375–1450 support density floors,
  interpolation, negative-density treatment, convolution, reduced-storage
  weighting, derivative accumulation and reciprocal-kernel stress terms.
  Accelerator atomics and reductions are present in these bodies.
- **Alternative-kernel zero-density domain.** `vdw_nl.F` 2655–2668 floors
  density for the auxiliary variable, but 2712–2716 uses the original
  nonnegative density in a separate ratio. At exactly zero, both numerator and
  denominator vanish locally. The report's conditional concern is supported;
  input reachability and compiled behavior have not been established.
  Lines 2825–2837 and 2883 support the additional local energy and potential
  contributions described.
- **Dispersion data, iteration and accumulation.** `vdwforcefield.F`
  2456–2524 supports the method dispatch and separate accumulation;
  5325–5400 supports parameter/volume checks and conditional derivative
  addition, subject to correction 1 above. `vdwforcefield_glb.F` 670–701
  supports charge-dependent interpolation and volume scaling without proving
  bounded interpolation weights. `vdwforcefield.F` 11230–11365 supports the
  sampled charge integration, neutrality adjustment, convergence threshold,
  charge update and reference-state rebuilding. `subdftd3.F` 119–161 and
  4079–4098 support unit adaptation and symmetric unpacking of the included
  parameter asset; its values were not assessed.
- **External adapters and derivative conventions.** `subdftd4.F` 73–115
  and 146–153 support the build boundary, geometry conversion, external
  evaluation and energy/force/lattice conversions. `libmbd.F` 293–312
  supports initialization error handling, relative-volume update, evaluation
  and conditional derivative retrieval. Neither sampled conversion divides
  immediately by cell volume. The report appropriately leaves downstream
  stress conventions and full external-library behavior unresolved.

## Review limits

The inventory has 17 partition entries totaling 73,489 lines, matching the
report and its file table. That establishes navigation coverage only. This
review sampled material claims rather than repeating every scoped source read.
Most of the larger bodies and the numerical parameter asset remain unread or
partially read, as the report states.

No complete exchange or dispersion derivation, force/stress consistency check,
singular-limit study, cache-lifetime trace, external API/version assessment or
CPU/NVIDIA/AMD comparison was performed. The corrections above concern the
report's interpretation of source conditions; they establish no reproduced
scientific or runtime defect. No proprietary source, comments, diagnostics or
parameter values were copied into this review artifact.
