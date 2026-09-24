# Independent review: perturbations, polarization and response observables

Reviewed 2026-09-24 against quarantined VASP 6.5.1. This is the single
independent review of the first-pass response report. The reviewer inspected
source separately, did not modify the report and used no further agents.
No program build, response calculation or numerical experiment ran.

## Outcome

One correction is warranted in the electric-field-gradient discussion. The
other substantive claims checked below are supported within the report's
stated scope. The conditional source concerns remain questions for later
investigation; this review establishes no observed numerical defect.

## Correction: distinguish the radial helper from the assembled EFG contribution

The report calls the extrapolation at `egrad.F` 527–577 a radial alternative
to the Fourier reconstruction. That description can suggest a second route
that supplies the reported tensor. Reading through the end of that helper
(527–607) shows extrapolation and printed local values, but no assignment of
the radial tensor contribution. A call search found no caller of this helper
in the inspected Fortran source.

The PAW caller instead invokes the other radial body at `paw.F` 1762. Its
implementation at `egrad.F` 417–521 constructs radial Hartree potentials from
the all-electron and pseudo densities, extrapolates their angular components
divided by radius squared, and stores their difference as the radial tensor
contribution. The output assembly adds that contribution to the Fourier
tensor at `egrad.F` 142 and then reverses the sign at 144.

Correct the paragraph to identify the inspected helper as a separate,
untraced helper, or extend the bounded reading to explain this actual
assembly. In the latter case, extend the scope table to reflect the additional
source ranges. This is a correction to the report's account of composition,
not a finding that the EFG implementation is numerically wrong.

## Claims checked

- **Prepared reference state and restrictions:** `linear_response.F`
  210–324 and 1238–1271 support the method restrictions, rebuilt potential
  and PAW terms, and capped orbital refinement. The remapping and restoration
  steps at 576–639 support the dependence on sampling and wave layouts.
  The Born-charge mean removal and tensor symmetrization are explicit at
  906–939.
- **Normal numerical differentiation:** the potential-helper dispatch at
  `ilinear_response.F` 438–452 is outside the nearby diagnostic branches.
  The occupation differences at 663–680 follow the end of the diagnostic
  branch at 653. `lr_helper.F` 683–739 and 850–920 support the two-point
  and higher-order stencil descriptions. The report correctly distinguishes
  these operations from the separately gated wave and charge diagnostics.
- **Response operators and gauge choices:** `hamil_lr.F` 655–714,
  `subrot_lr.F` 170–229 and 670–735 support the differentiated PAW terms,
  shifted energy denominators and selected occupied-space projection.
  `hamil_lr.F` 299–302 and `hamil_lrf.F` 812–816 do use different bounds
  and diagnostic mechanisms.
- **Stopping and solver failure:** `ilinear_response.F` 857–877 and
  `elinear_response.F` 579–600 support energy, stagnation, density and
  minimum-iteration tests. The optional error-count behavior is present in
  `rmm-diis_lr.F` 549–565; calls at `ilinear_response.F` 540–541 and
  `elinear_response.F` 435–436 omit that optional argument. The magnetic
  solver fragment at `rmm-diis_mlr.F` 688–733 supports the separate
  variational and residual measures. No conclusion about final observable
  accuracy follows from these local exits.
- **Polarization:** setup and occupation restrictions match `pead.F`
  365–438 and 962–975. Determinant products, phase centering and history
  match `elpol.F` 1469–1599 and `pead.F` 3751–3864. The fixed first-spin
  index really is used inside the history's spin loop at 3831–3832.
  Both the helper cited at 3936–3965 and the determinant helper actually
  called by the sampled polarization loop at 3992–4002 reject nonpositive
  estimated conditioning. This does not settle small-gap or branch-continuity
  behavior.
- **Optical conventions:** `linear_optics.F` 242–275, 850–950 and
  1404–1459 support the early returns, frequency grid, transition weights,
  integration choices and current-response conversion. The zero-frequency
  replacement precedes the optional intraband addition. The report scopes
  the separate reciprocal-point parallel restriction correctly to the older
  path in `optics.F` 49–58; its smooth and augmentation contributions are
  visible at 260–351.
- **Magnetic and near-nucleus reconstruction:** selected reads in
  `linear_response_NMR.F` 147–218, 322–357, 826–914 and 3401–3485,
  `nmr.F` 2804–2840, `hyperfine.F` 277–352 and 607–625,
  `cl_shift.F` 214–272 and 1337–1423, and `core_con_mat.F` 244–325
  support the reported local operations. In particular, the hyperfine
  all-electron contact value is overwritten by the later relativistic helper.
- **Spin-tensor domains:** `dmatrix.F` 128–143 admits exactly one half
  before dividing by a factor that vanishes there. At 702–710, the
  near-origin branch assigns only the diagonal components of the six-component
  reciprocal kernel. The report correctly leaves upstream restrictions,
  initialization and consequences unresolved.

## Scope and limitations

The inventory independently confirms 20 response files and 38,584 lines,
with every assigned filename represented in the report's scope table. This
review sampled the substantive claims above, rather than completing every
file or deriving all response equations. It did not audit the entire phase
history lifecycle, prove initialization at all kernel callers, validate PAW
or magnetic reconstruction, or establish hardware capability on CPU, NVIDIA
GPU or AMD GPU. Those limitations are consistent with a bounded first pass.
