# Machine-learned force fields: Fortran first-pass review

Reviewed 2026-09-24 against quarantined VASP 6.5.1 and the
[first-pass report](../ml-fortran.md). This is the requested single independent
review at depth one. No child review, compilation, training, dynamics or other
scientific experiment was performed.

## Corrections required

**Qualify energy centering by the selected scaling mode.** The report currently
describes subtraction of species reference energies followed by centering as
unconditional. The cited `ml_ff_ff.F` 7082–7147 computes means, but target
construction at 7210–7244 distinguishes two modes. One subtracts species
reference energies only; the other additionally subtracts the corresponding
training mean. Both have total-energy and per-atom branches. The reader defaults
to the centered mode at `ml_reader.F` 630. State this distinction and add the
target-construction location to the evidence. This matters for reconstructing
the target convention and its inverse transformation; it does not establish a
defect in either mode.

**Correct the map-only summary.** The closing paragraph says five files are
map-only, but the scope table identifies six: `ml_reader.inc` plus the five
files in its final row. Use six or omit the count. All 26 assigned files are
already represented in the table.

Two small source-precision edits would also help. Extend the evidence-route
reference from `ml_ff_math.F` 8220–8308 through 8324, where the residual and its
squared norm are actually formed. In the acquisition paragraph, describe the
root-generated, broadcast quantity as the next sampling interval: that is the
value broadcast at `ml_ff_ff.F` 8251–8256. The local threshold logic then makes
the evaluation decision.

## Material claims checked

- **Enablement, modes and workflow.** `ml_interface.F` 39–100 supports
  conditional enablement and the unavailable-build diagnostic. `ml_reader.F`
  150–199 supports changes to start state, step count, regression defaults and
  selection criteria. `ml_ff_mlff.F` 257–342 supports geometry staging,
  prediction, conditional threshold updates, return of predictions and the
  callback decision. In particular, the prediction start state suppresses the
  training callback. Lines 554–635 support the conditional environment,
  design-matrix, scale and sparsification updates and environment distribution.
  The report appropriately leaves full sequencing and recovery unresolved.
- **Configuration history.** `ml_ff_abinitio.F` 779–815 stores lattice,
  volume, positions, velocities and timestep. Lines 861–867 retain labels,
  step index and acquisition threshold. Lines 1118–1142 append configuration
  geometry, species mappings and labels, with conditional threshold retention.
  These bodies support the distinction between a parameter vector and a
  learning trajectory without proving complete restart serialization.
- **Neighbors and normalization.** `ml_ff_neighbor.F` 123–182 supports
  lattice-dependent image bounds when the optional inverse lattice is present,
  the three-position range per lattice direction otherwise, and filtering on
  squared distance. The filter does exclude sufficiently close distinct atoms.
  `ml_ff_math.F` 4454–4499 supports norm-thresholded scaling and subsequent
  removal of the coupled derivative's parallel component; below threshold,
  scaling is skipped while the later processing remains. The report does not
  claim that this proves a reachable physical discontinuity.
- **Kernels and derivative execution.** `ml_ff_math.F` 6890–6945 supports
  different ordering of aggregation and polynomial powers for separate and
  combined contributions. `ml_ff_ff3.F` 1753–1787 supports force contractions
  and displacement/volume factors for stress. `ml_ff_ff2.F` 1–14 and 138–242
  supports its MPI-conditioned presence, atom distribution, descriptor and
  normalization sequence, energy/derivative calls and final force/stress
  reduction. Mathematical equivalence of all paths remains unproved.
- **Regression and numerical domains.** `ml_ff_math.F` 7659–7700 supports
  relative singular-value truncation in one branch and a smooth regularized
  inverse in another. `ml_ff_ff.F` 3384–3435 supports the extremal absolute
  eigenvalue ratio without a local zero-maximum guard. The Gram construction
  is visible at `ml_ff_math.F` 7898–7915; 8225–8324 scales it, adds a diagonal
  prior term, solves for weights and forms residuals. Lines 8345–8461 support
  the evidence expressions, effective parameter count and divisions by
  residual/weight-norm quantities in the parameter updates. The lower bound
  on the prior parameter is present. These are valid local domain questions,
  not evidence that supported training cases fail.
- **Solver status and diagnostics.** The factorization and solve at
  `ml_ff_math.F` 8253–8274 consume results without a local status check; the
  inversion body at 8474–8498 likewise has no explicit local check.
  `ml_ff_helper.F` 20–73 performs workspace preparation and cleanup without
  inspecting solver status. `ml_ff_tutor.F` 224–266 delegates stopping to its
  policy routine. The report correctly leaves the complete error policy open.
- **Uncertainty and acquisition.** `ml_ff_ff.F` 10976–10979 supports the
  omitted-uncertainty zero output; 11201–11284 supports covariance-related
  contractions, reductions and variance rescaling. Lines 8183–8225 support
  distinct energy, force and stress summaries and acquisition criteria.
  Lines 8247–8311 support sampling eligibility, immediate triggering at the
  larger threshold, forced/test overrides and the final refit-state reset.
  Calibration and scientific accuracy are correctly kept separate from these
  computations.
- **Output, model reading and shared memory.** `ml_interface_writer.F`
  72–110 supports field additions, conditional force-drift removal and kinetic
  pressure output. `ml_ff_iohandle.F` 216–295 supports version comparison and
  the initial format probe. `ml_ff_mpi.F` 53–82 supports shared-node grouping;
  `ml_ff_mpi_help.F` 42–80 supports the broadcast/wait alternatives.
  `ml_ff_mpi_shmem.F` 578–606 supports the two allocation paths, barriers,
  pointer setup and conditional status return. `ml_ff_c2f_interface.F`
  113–182 exposes shared-memory and profiling operations. No full lifetime,
  round-trip or target execution result follows from these reads.

## Review limits

The inventory contains 26 files totaling 52,255 lines, and every assigned path
appears in the report's reading-scope table. That is navigation coverage. This
review sampled substantive bodies and immediate control flow; it did not repeat
all reads, analyze the six map-only files, derive every descriptor or prove the
complete regression, acquisition, persistence or unit-conversion contracts.

No source claim here substitutes for held-out scientific validation or actual
CPU, NVIDIA and AMD execution. The report's return questions remain open. No
proprietary source, comments, diagnostic text or datasets were copied into this
review artifact.
