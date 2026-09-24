# Independent review: geometry first pass

Reviewed 2026-09-24 against the quarantined VASP 6.5.1 snapshot. One review
round at depth one; no delegated review, build or execution. Source discussion
is original prose.

## Findings

No substantive correction is required by this bounded review. The report
distinguishes inspected behavior, mathematical deductions and unresolved
consumer obligations. It does not claim a proof of the lattice algorithms,
complete magnetic symmetry coverage or demonstrated accelerator correctness.

## Assessed claims

The lattice basis convention and signed volume are supported by `lattice.F`
28-45. The real and complex coordinate conversions match the stated matrix
convention. The constructor does divide before an explicit singular-cell check
in its own body; the report correctly leaves caller validation unresolved.
The wrapping helper's finite offset does not establish arbitrary-coordinate
wrapping. The separate minimum-image search has both a bounded translation
search and fixed temporary storage (`symmetry.F` 133-190), supporting the
report's questions about admissible cells and image degeneracy.

The selective-motion, magnetic and response filtering examples are supported.
The external symmetry-library entry explicitly transposes the lattice and
adapts returned operations. The debug caller does repeat final symmetry
initialization after the tolerance scan (`main.F` 1140-1153); the report's
limited conclusion about that call site is justified. This does not establish
that every input mutation or alternate caller has been audited.

Explicit reciprocal weights are checked and normalized. Generated sampling
uses integer mesh transformations and has a real allocation-growth path;
initial capacities are consequently not universal hard bounds. The full-zone
sample performs distributed destination and count checks while constructing
indices and phases. Those checks do not verify the complete transformation,
as the report states. The spinor eigenproblem, adjoint application and direct
failure stop are also accurately described.

The sampling pointer stack and descriptor regeneration establish the reported
ownership questions. In the inspected accelerator branch, full-grid mapping
is deleted and recreated; structure factors have a host computation followed
by a conditional device update. The source does not establish that all these
paths work on the three required execution targets. The supercell records
and build condition support the reported method coupling, while atom
replication preserves parent indices and selective-motion flags.

The electronic role assigned to `rot.F` is supported by its arguments,
imports and wavefunction state. Deferring its detailed study to electronic
solution while retaining its inventory membership is appropriate. The
structure-factor invariants are mathematical deductions from the phase sum,
not assertions of bitwise invariance or executed results.

No copied proprietary implementation text was identified in the report.
The remaining lattice, magnetic and reconstruction questions are suitable
return conditions rather than reasons to hold this first pass open.

## Review scope

Read current project guidance and the complete report. Independently inspected:

- `lattice.F` 18-73 and 133-249.
- `symmetry.F` 120-190, 1545-1615, 1735-1790, 1808-1845,
  1880-1935, 2030-2166, 2190-2280 and 3300-3388;
  `main.F` 1125-1172.
- `mkpoints.F` 480-520, 1078-1140, 1270-1325 and 1480-1516;
  `mkpoints_struct.F` 1-166; `mkpoints_full.F` 1020-1228 and
  targeted inversion/conjugation references.
- `mkpoints_change.F` 25-96 and 328-397; `spinsym.F` 225-278
  and 307-380; `stufak.F` 1-166.
- `supercell.F` 9-292; `sym_grad.F` 45-135; `rot.F` 60-140;
  `symlib.F` 1-14; `lattlib.F` 2619-2675.

This review did not independently audit every scope-table file or verify the
author's historical reading activity. It did not prove integer lattice
algorithms, trace every symmetry consumer or test compiler and hardware
behavior. No additional review round is requested.
