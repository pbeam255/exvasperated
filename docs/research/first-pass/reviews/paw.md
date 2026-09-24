# Independent review: PAW first pass

Reviewed 2026-09-24 against quarantined VASP 6.5.1. One review at depth
one, with no delegated review, compilation, execution or dataset copying.
Findings below are independently written descriptions of inspected behavior.

## Findings

No substantive correction is required by this bounded review. The report
accounts for all 20 files assigned to the area and describes its body-reading
limits. It does not equate source inspection, file coverage or reference
agreement with scientific validation.

## Assessed claims

The dataset records and reader support the distinction between supplied
atomic data and derived calculation state. The inspected reader initializes
missing kinetic-density blocks to zero, preserves selected original potential
arrays and derives radial spacing from the mesh endpoints (`pseudo.F`
544-673). Postprocessing checks species and reference-functional consistency
and conditionally optimizes real-space projectors using calculation settings
(1209-1370). The report correctly leaves scientific admissibility of missing
information unresolved. Its ordered-species and incomplete-data claims are
also supported by the [public POTCAR description](https://vasp.at/wiki/index.php/POTCAR),
consulted on the review date.

The moment routine temporarily changes the radial integration extent for
all-electron overlap quantities, restores the original extent and integration
weights, then recomputes the difference moments (`radial.F` 79-152). The
report's statement that this preprocessing changes data is supported. The
augmentation setup aligns the sphere boundary, constructs compensation
functions and spline tables, and processes consecutive groups of equal
angular momentum with a fixed channel bound (`paw.F` 29-219). The sampled
angular transform doubles contributions for distinct channel pairs while
visiting a triangle of those pairs (`paw_base.F` 259-322); the report does
not incorrectly extend this real-case observation to every complex transform.

The high-level projection dispatch, borrowing of coordinates and dataset
tables, phase-cache early return and projection-index check agree with the
report (`nonl_high.F` 29-184; `nonlr.F` 116-172; `nonl.F` 635-683,
878-954). The residual contraction contains the eigenvalue-dependent overlap
correction described in the report (`nonl.F` 696-716; `wave_high.F`
4812-4900). Cache validity under moving ions remains a caller obligation to
trace, rather than an established runtime defect.

The occupation accumulation includes band occupations, reciprocal weights
and spin multiplicity. Its accelerator path transfers the result back and
waits before the sampled host reductions (`us.F` 324-414). The different
symmetry stages in the charge driver are present at the cited locations
(1154-1279). The reconstructed-density path conditionally subtracts
compensation and combines the resulting contribution with smooth density
(`aedens.F` 550-629). The report's distinction between compensation and
reconstructed density is consistent with the
[public PAW formalism description](https://vasp.at/wiki/Projector-augmented-wave_formalism),
consulted on the review date.

The sampled on-site driver disables offload, reconstructs radial quantities
from mixed state, conditionally recovers imaginary occupation information,
assembles several method-dependent matrix contributions, and reduces energy
corrections before assigning the final energy fields (`paw.F` 1412-1525,
1660-1740, 1990-2135). The potential-weighting and later contraction bodies
support the warning about counting radial quadrature twice (`radial.F`
593-647, 1651-1672). The local spin-orbit angular bound and active-path
spin-spiral restriction are appropriately scoped (`relativistic.F` 13-149;
`fast_aug.F` 143-152).

Per-ion dataset selection and the atomic recalculation driver support the
report's limited statement that dataset state need not remain immutable
(`core_rel.F` 325-383; `rhfatm.F` 298-365). These observations do not establish
the accuracy or supported workflow combinations of core relaxation.

## Review limits

This review checked selected claims and citations, not every routine or the
author's entire reading history. It did not derive the full PAW energy
functional, prove projector duality or angular conventions, trace force and
stress derivatives, validate atomic datasets, establish parser completeness,
or test CPU/NVIDIA/AMD behavior. Those remain suitable return conditions
already identified by the report. No additional review round is requested.
