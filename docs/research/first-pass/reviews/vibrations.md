# Vibrations, electron–phonon coupling and transport first-pass review

Reviewed 2026-09-24 against quarantined VASP 6.5.1 and the
[first-pass report](../vibrations.md). This is the requested single independent
review at depth one. No child review, build or scientific experiment was run.

## Corrections required

1. **Correct the older phonon path's source locations.** The reading-scope
   table and Gamma-direction paragraph interchange the directional correction
   and Fourier construction. The default direction and optional replacement
   are in `phonon.F` 934–937; its use at Gamma is at 953–958; the reciprocal
   basis transformation and directional polar tensor are at 1029–1070.
   Fourier construction from force constants is at 1164–1204. The reported
   scientific behavior is supported; update the scope labels and the
   directional-limit citation.
2. **State where the export path obtains its primitive cell.**
   `elphon_derivative.F` 147–225 receives an existing primitive-cell object.
   At 186–196 it either constructs a related object from a user-supplied
   primitive lattice or uses the supplied object directly. Replace the claim
   that this sampled export path finds a primitive cell with this description.
   Automatic primitive-cell determination elsewhere was not established by
   these cited lines. Automatic FFT-grid selection is supported at 199–208.

## Material claims checked

- **Finite differences and restricted inverse.** `finite_diff.F` 158–223
  supports the displacement/stencil controls and retained reference state.
  Lines 269–348 support the force Jacobian, sign change for returned force
  constants and mass weighting. Lines 350–365 and 982–995 support continuation
  after nonzero diagonalization status. Lines 1774–1801 confirm that the
  inverse helper skips the first three eigenmodes and retains only later
  eigenvalues above its fixed positive threshold. Lines 1865–1876 confirm
  contraction with Born charges on both sides. These are local source
  properties; their suitability for constrained or unstable systems remains
  unresolved as stated.
- **Symmetry, translational correction and modes.** `sydmat.F` 68–125 and
  540–617 support rotations and atom mappings. `phonon.F` 812–859 supports
  extraction of supercell blocks and replacement of the on-site block.
  `elphon_potential.F` 339–387 supports the distinct iterative row/column and
  transpose correction, followed by its final symmetric on-site correction.
  `phonon.F` 966–1011 supports mass weighting, explicit Hermitian averaging,
  eigensolver-status handling and signed square roots. The Gamma statements
  hold with the corrected references above.
- **Angular frequency and error propagation.** `elphon_potential.F` 573–642
  supports averaging over equivalent images, mass factors and atomic basis
  phases. Lines 752–780 convert signed roots to angular frequency in inverse
  picoseconds; the lack of a local status check after the eigensolver is
  visible at 771–780. `elphon_accumulators.F` 165–166 uses Planck's constant
  divided by two pi for the corresponding energy conversion. The report's
  distinction from cyclic frequency is supported.
- **Import and derivative preparation.** `elphon_potential.F` 94–143 supports
  alternative structural records and the optional primitive-matrix fallback;
  278–315 supports comparison of supplied shortest-image multiplicities and
  vectors with reconstructed maps. `elphon_derivative.F` 147–167 exposes
  potential, atomic-matrix, overlap, force-constant and polar inputs.
  Lines 621–658 support the different aligned and general grid preparations.
  Primitive-cell provenance needs the clarification above.
- **Long-range and PAW matrix elements.** `elphon_potential.F` 3581–3634
  supports the Born-charge/quadrupole terms, dielectric denominator, Ewald
  suppression, optional radial truncation and atomic phases. The excluded
  origin is where the combined reciprocal transfer and reciprocal-lattice
  vector vanish. `elphon_mels.F` 2692–2798 supports the band-energy difference
  term and the projector-derivative terms involving Hamiltonian and overlap
  matrices. Lines 2062–2092 support transfer-dependent caching, phase changes,
  communicator reduction and mode contraction; `elphon_base.F` 1668–1687
  confirms the contraction. `elphon_mels.F` 2358–2388 supports the explicit
  unity replacement and direct/matrix-product dispatch.
- **Unstable-mode policies.** `elphon_potential.F` 4067–4079 normalizes positive
  modes, zeros nonpositive modes and returns an error flag. Its immediate
  wrapper at 793–795 does not inspect that flag. `elphon_common.F` 1242–1250
  supports the earlier sufficiently-negative-frequency rejection and override.
  `elphon.F` 4236–4248 instead uses a complex square root for negative modes
  and zeros modes below an absolute near-zero threshold. The report correctly
  distinguishes these policies without claiming a reproduced discrepancy.
- **Electronic self-energy and Debye–Waller term.**
  `elphon_accumulators.F` 1006–1072 supports the occupation factors, static
  denominator choice, omitted small modes, squared couplings and separately
  accumulated frequency derivative. Lines 1722–1749 and 1810–1856 support the
  sampled mode factors, Gamma couplings, electronic denominators and nonzero
  broadening substitution. The unproved cancellation and approximation scope
  remain appropriately deferred.
- **Cumulative phonon-mode concern.** `elphon_selfen_ph.F` 1302–1317 confirms
  that the temporary is cleared before the mode loop, incremented for each
  retained mode and then added to that mode's stored result. Contributions
  from preceding retained modes therefore remain in the local temporary.
  Lines 1184–1220 show a caller chain to this body under tetrahedron selection;
  complete workflow reachability and intended accumulation semantics were not
  traced. The report's conditional concern is warranted, including its refusal
  to claim an observed scientific failure.
- **Transport.** `transport.F` 1029–1083, 1408–1416 and 1661–1687 support
  the mean-free-path, symmetrized-product, transport-function and moment chain.
  Lines 1367–1382 support the Fermi-variable quadrature transformation and
  collapsed zero-temperature grid. Lines 1594–1602 confirm zero initialization
  and reciprocal assignment only above the imaginary-self-energy threshold.
  Lines 1700–1740 support conductivity inversion and carrier-density division.
  The report does not overstate unit or domain verification.
- **Driver and reciprocal grids.** `elphon_driver.F` 102–172 supports dense
  electronic preparation and the constant-relaxation-time transport return
  before force-constant/derivative loading. Lines 176–193 support the selected
  dispersion returns. Lines 302–343 confirm the later dry-run return and the
  active integer-triplet loop. `elphon_triplets.F` 54–62 supports periodic
  integer folding. `elphon_kgrid.F` 219–234 supports build-dependent symmetry
  acquisition, and 470–512 supports external triplet generation and counting
  of representative multiplicities.

## Review limits

The inventory lists the same 16 files as the report, totaling 31,404 lines.
This confirms navigation coverage, not completed per-file analysis. The review
checked the substantive claims through selected bodies and nearby control flow;
it did not reread every reported range or audit all interpolation, transport,
serialization, symmetry, parallel-memory or integration code.

No force-derivative convergence, dispersion, self-energy, transport coefficient,
phase/gauge equivalence or CPU/NVIDIA/AMD execution was tested. The reported
status, mode-indexing and domain observations remain source findings with
explicit follow-up limits. No proprietary source, comments, diagnostics or
datasets were copied into this review artifact.
