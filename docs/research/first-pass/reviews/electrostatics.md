# Independent review: electrostatics first pass

Reviewed 2026-09-24 against quarantined VASP 6.5.1. This is one review at
depth one, with no delegated review, compilation, execution or dataset copying.
The descriptions below are independently written from the inspected source.

## Findings

No substantive correction is required by this bounded review. The report
accounts for the 16 assigned files, distinguishes selected body reading from
complete analysis, and preserves concrete questions for related studies. Its
energy-sign interpretation, boundary-condition scope and treatment of inactive
extension bodies agree with the inspected source.

## Assessed claims

The periodic kernel uses the physical reciprocal vector and assigns its origin
separately. The potential contraction includes the inverse cell volume. The
energy helper applies storage weights, sums the density–potential contraction,
changes its sign and halves it, then performs the communicator reduction
(`coulomb_cutoff.F` 23–50; `pot_electrostat.F` 129–218). The main potential
driver stores that result in the energy record, and the electronic driver adds
it to the band-energy sum (`pot.F` 495–500; `electron.F` 639–641). The report
correctly identifies an energy-accounting correction and avoids interpreting
its sign as a negative physical Hartree self-energy. It also leaves the full
cancellation with other energy contributions unresolved.

The spherical and slab kernels have different finite origin values, including
different signs. The optional origin indicator defaults to false; the sampled
grid caller supplies it from the reciprocal indices (`coulomb_cutoff.F`
71–93, 151–258; `pot_electrostat.F` 157–169). The broad dimensionality
validator does not establish support for every accepted integer: the padding
setup selects only isolated and slab truncation cases. Its defaults and the
simplified-slab restriction support the report's narrower capability statement
(`coulomb_cutoff.F` 556–681).

The coarsened Hartree branch constructs a truncated coarse potential, subtracts
the periodic coarse result, transfers the difference and adds the periodic
fine-grid result (`pot_electrostat.F` 464–536). The derivative setup independently
allocates padded state and reconstructs geometry and structure factors
(`coulomb_cutoff_gradients.F` 29–99). In the Ewald reciprocal dispatcher, stress
is initialized to zero and passed to the bulk routine but not the slab routine;
the final driver assembles reciprocal, real-space and background contributions
(`ebs.F` 1143–1197, 1590–1662). Treating low-dimensional stress as an unresolved
derivative question is warranted. The report does not overstate this local
observation as a demonstrated failure of a complete calculation.

The smooth-density driver contains occupation, sampling and spin weights,
band redistribution, communicator reductions and the stated host transform
boundary (`charge.F` 46–173). Kinetic-density formation uses displaced
reciprocal vectors, transformed gradients, volume/grid normalization and spinor
products, followed by grid transfer (`tau_mu.F` 708–864). The Hamiltonian
record carries separate fine and soft derivative fields. Selected operator
paths and subspace subtraction agree with the report's distinction between
Hamiltonian application and updates that require caller context (`hamil.F`
921–964, 1115–1175; `hamil_rot.F` 194–260).

Potential assembly contains distinct density/potential transform scaling,
host/device handoffs and an in-place fine-grid transform during soft-potential
setup (`pot.F` 405–478, 614–624, 719–757). The self-consistent correction receives
the local periodic Coulomb configuration at the cited driver call (574). Its
compile guards, saved call count, delayed application, diagonal-cell spacing
and single-process multigrid communicator support the report's combination and
cell-shape questions (`scpc.F` 1–168, 199–240, 1210–1279).

The sampled dipole procedure retains history and combines previous and current
center information; it also applies special weighting near the periodic cut
(`dipol.F` 579–604, 674–735). The magnetic-field reader distinguishes input
shapes and the addition routine targets spin-potential zero components
(`bext.F` 45–69, 91–136). The inactive bodies in `extpot.F` and `solvation.F`
are correctly scoped to this snapshot. Other external-potential calls are
present in `pot.F` 439–444 and 518, so neither placeholder supports a blanket
claim that the program lacks external fields or every possible solvation
extension.

## Review limits

This review checked selected substantive claims and source locations, not every
routine or the author's complete reading history. It did not derive all energy
terms, verify reciprocal ownership for every distributed layout, prove padding
maps or cell-domain restrictions, trace complete force/stress derivatives,
validate correction convergence or restart behavior, or test CPU/NVIDIA/AMD
execution. These remain return conditions rather than requirements to exhaust
this first pass. No additional review round is requested.
