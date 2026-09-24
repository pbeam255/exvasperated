# Machine-learned force fields: Fortran workflow and regression

Reference: quarantined VASP 6.5.1, inspected 2026-09-24. This partition contains
26 files and 52,255 lines, identified in the [inventory](../vasp-source-inventory.csv).
This is a bounded source study. No training, dynamics, regression solve or
CPU/GPU comparison was executed. Source locations below identify the inspected
snapshot; the prose is independently written.

## Reading scope

Every assigned file has a place in this pass; most bodies remain partially
read. A procedure map establishes navigation, not algorithmic coverage.

| File | Reading in this pass |
| --- | --- |
| `ml_interface.F` | Enablement and unavailable-build handling, 39–106. |
| `ml_interface_writer.F` | Force/energy modifications and output selection, 56–139. |
| `ml_reader.F` | Mode defaults, 150–199; map of subsequent regression and mode restrictions. |
| `ml_reader.inc` | Declaration/entry map only. |
| `ml_ff_mlff.F` | Host handshake, prediction and acquisition/update sequences, 246–424 and 534–635; compatibility checks, 2030–2070. |
| `ml_ff_ff.F` | Selected reference-energy centering, descriptor selection, acquisition, uncertainty and unit-conversion bodies; most of this large file remains unread. |
| `ml_ff_ff2.F` | MPI-conditioned entry, local atom distribution and prediction sequence, 1–242; inner optimized kernels remain partial. |
| `ml_ff_ff3.F` | Normalization dispatch, 511–648; force/stress contractions, 1740–1816. |
| `ml_ff_math.F` | Selected descriptor normalization, polynomial kernels, SVD filters and evidence/covariance regression bodies. Full descriptor and solver derivations remain open. |
| `ml_ff_abinitio.F` | Geometry and label storage, 779–870; configuration append, 1108–1143; remaining entries mapped. |
| `ml_ff_neighbor.F` | Direct image enumeration and distance filtering, 81–184; other neighbor algorithms mapped. |
| `ml_ff_iohandle.F` | Model-version recognition, 216–295; remaining file operations mapped. |
| `ml_ff_constant.F` | Constants and unit definitions, 1–81. |
| `ml_ff_prec.F` | Precision-kind selection, 1–27. |
| `ml_ff_helper.F` | Representative eigensolver workspace helpers, 20–73. |
| `ml_ff_mpi.F` | Shared-node communicator and grouping setup, 28–85; remaining collectives mapped. |
| `ml_ff_mpi_help.F` | Broadcast/wait alternatives, 42–80. |
| `ml_ff_mpi_shmem.F` | Representative allocation and pointer binding, 559–609; remaining overloads mapped. |
| `ml_ff_c2f_interface.F` | Selected shared-memory, process and profiling declarations, 110–186. |
| `ml_ff_taglist.F` | Tag-state lookup/update, 422–457; broader parsing mapped. |
| `ml_ff_tutor.F` | Diagnostic dispatch and stop-policy delegation, 224–266. |
| `ml_asa2.F`, `ml_ff_logfile.F`, `ml_ff_memory.F`, `ml_ff_string.F`, `ml_ff_struct.F` | Module/procedure or declaration maps only. Angular machinery, full state layout, accounting and text behavior need body reads. |

## A force-field calculation has a history

The host interface first decides whether this subsystem is enabled and reports
an error when enabled in a build lacking the facility (`ml_interface.F`
39–106). The reader's operational choices alter several defaults together:
training may resume existing reference data, refitting changes step count and
regression settings, selection changes the acquisition criterion, and prediction
selects a distinct start state (`ml_reader.F` 150–199). These observations are
not yet a publicly documented input contract.

At each sampled host step, geometry is staged, the force-field evaluator is
called, thresholds may be updated, and predictions are returned. Whether the
electronic calculation is then needed depends on acquisition decisions and
the surrounding step/second-call/final-step state. Prediction mode suppresses
the training callback (`ml_ff_mlff.F` 246–424). After reference results arrive,
selected branches update environments, kernels, design matrices, noise scales
and sparse reference sets, then distribute the resulting environments
(534–635). Full ordering and failure recovery remain to be traced.

The storage helpers retain geometry, labels, species mappings, step indices
and the acquisition threshold associated with a configuration
(`ml_ff_abinitio.F` 779–870, 1108–1143). Thus reproducing a learning trajectory
requires more than a final parameter vector. The useful future comparison is
the sequence of predicted states, electronic evaluations, retained data and
model changes under a stated starting state. This pass does not establish
restart completeness or identical training outcomes across rank counts.

## Local environments, derivatives and normalization

The sampled direct neighbor routine enumerates atom/image candidates, uses
lattice-dependent image bounds when an inverse lattice is supplied, and
otherwise uses one image in each direction around the central cell. It retains
distances inside the cutoff but excludes sufficiently small squared distances
(`ml_ff_neighbor.F` 81–184). The latter excludes nearly coincident distinct
atoms as well as self pairs. This is one routine, not a finding that all
neighbor construction is limited to 27 cells. Skew cells, small cells, cutoff
boundaries and duplicate positions require caller-specific analysis.

The descriptor path distinguishes radial and angular contributions, optional
combined normalization and derivative coupling (`ml_ff_ff3.F` 511–648).
In a sampled separate-normalization branch, a vector above a small norm
threshold is scaled to unit length; its coupled derivative is scaled and its
parallel component removed (`ml_ff_math.F` 4454–4499). Below that threshold,
the scaling is skipped while later derivative processing remains. Continuity
and the actual reachable zero-environment cases are open questions.

The sampled kernels form weighted powers of descriptor overlaps, with different
aggregation depending on whether contributions are combined
(`ml_ff_math.F` 6890–6945). These choices change the model, not merely storage.
The derivative contraction uses displacement and inverse volume to form stress
as well as forces (`ml_ff_ff3.F` 1740–1816). The optimized MPI entry distributes
atoms, builds descriptors, normalizes them, predicts energies and derivatives,
then reduces forces and stress (`ml_ff_ff2.F` 138–242). Equivalence of the
optimized and other paths is unproved. Force conservativity, strain derivatives,
species permutations, translation and rotation behavior need a joint derivation
across the descriptor, normalization and contraction layers.

## Targets, regression and numerical domains

Training target preparation subtracts species reference energies. One scaling
mode uses that result directly; another also subtracts the training mean, with
total and per-atom branches in both modes (`ml_ff_ff.F` 7231–7244). The reader
defaults to the centered mode (`ml_reader.F` 630). Force and stress statistics
are handled separately (`ml_ff_ff.F` 7082–7147). Target weights, empirical scales
and configuration/atom counts also enter later normalization
(11164–11312). A numerical regularizer only has meaning relative to this
scaling. Comparisons must retain energy convention, force/stress units, label
weights and the treatment of small empirical variance.

The sampled SVD regression branches use either a relative singular-value cutoff
or a smooth regularized inverse with a prior/noise ratio in the denominator
(`ml_ff_math.F` 7659–7700). They therefore need not agree for the same nominal
training data. Rank zero, a zero largest singular value, and permissible
regularization parameters require caller checks that this pass did not prove.
The descriptor-selection helper similarly obtains an extremal-eigenvalue ratio
without a local zero-maximum guard (`ml_ff_ff.F` 3384–3435).

In the evidence-based route, a scaled Gram matrix receives a diagonal prior
term, is factored, and is used to obtain weights and residuals
(`ml_ff_math.F` 8220–8324). Later evidence expressions and an effective
parameter count control noise/prior updates; the update divides by residual
and weight-norm quantities and applies a lower bound to the prior parameter
(8340–8461). Zero residuals, zero weights and parameter-domain preservation
need explicit analysis. These are local numerical concerns, not demonstrated
training failures.

Several sampled LAPACK calls pass status through workspace helpers but do not
check it locally before consuming results (`ml_ff_math.F` 8220–8308,
8474–8498; `ml_ff_helper.F` 20–73). The complete caller/error policy remains
open. The diagnostic helper itself delegates stopping to another policy
routine (`ml_ff_tutor.F` 224–266); a diagnostic's severity label alone does
not establish termination.

## Uncertainty and acquisition are different contracts

The sampled uncertainty path contracts design vectors with a covariance-related
matrix and rescales the resulting variances. Its prediction-only branch can
instead set uncertainty outputs to zero when uncertainty evaluation is disabled
(`ml_ff_ff.F` 10970–11058, 11164–11312). Zero in that branch means an omitted
calculation; it cannot establish confidence in the prediction.

Acquisition reduces these quantities differently for energy, force and stress.
Forces have both an average component-based measure and a maximum atom-based
measure. The selected criterion may use a force uncertainty or another local
descriptor measure. Ordinary threshold exceedance interacts with sampling
eligibility; a larger threshold can trigger an electronic evaluation immediately.
Forced updates and testing alter those decisions, and the refit start state
later clears the sampling/evaluation flags (`ml_ff_ff.F` 8171–8315).

One sampling option draws the next sampling interval on a root rank and
broadcasts that interval (`ml_ff_ff.F` 8251–8256). Therefore
seed/history, ordering, threshold updates and rank behavior can affect which
reference calculations enter the model. A regression uncertainty is conditional
on its descriptor, reference set, noise/prior choices and approximation. No
calibration against held-out chemistry, phase transitions or rare environments
was established here. A low training residual or low uncertainty is not an
independent scientific accuracy result.

## Host output, persistence and execution

The output adapter modifies forces and energy for an external field, conditionally
removes force drift, and constructs pressure-related output using volume and
kinetic terms (`ml_interface_writer.F` 56–139). It is not a passive formatter.
Internal unit definitions and return conversion are visible in
`ml_ff_constant.F` and `ml_ff_ff.F` 11393–11422; the full conversion chain from
host geometry through learned stress and back to host extensive stress remains
a return task. Predicted energy does not by itself define every electronic
free-energy quantity that an output consumer might expect.

The model reader distinguishes format generations and compares version
components against a supported maximum (`ml_ff_iohandle.F` 216–295).
Its initial format probe reads before establishing the full model contents.
Truncated input, architecture dependence, complete round trips and older-model
semantics were not established. No private model or training fixture was adopted.

Shared-node grouping and collective choices are separate from regression
mathematics (`ml_ff_mpi.F` 28–85; `ml_ff_mpi_help.F` 42–80). A sampled shared
allocation brackets pointer setup with barriers, uses shared storage for
multi-rank groups and ordinary allocation for one rank, and returns an
allocation status only when the optional status argument is supplied
(`ml_ff_mpi_shmem.F` 559–609). Full lifetime, failure and visibility contracts
remain unproved. C bindings also expose system shared-memory and profiling
operations (`ml_ff_c2f_interface.F` 110–186).

CPU, NVIDIA and AMD alpha acceptance must cover both prediction and the
training/acquisition workflow actually offered. Descriptor derivatives,
distributed reductions, regression factorization, shared ownership and host
callbacks need target-specific execution evidence. None is supplied by this
source inspection, and these implementation choices do not select our backend.

## Returns

Return after the C++ descriptor and numerical-library studies to trace the full
descriptor/derivative equations, data ownership and solver failure propagation.
Other returns are the acquisition state machine and restart history; unit and
energy-label semantics; conditioning and zero-domain cases; model persistence;
uncertainty calibration; and optimized-path equivalence. The six map-only
files and unread bodies remain part of eventual per-file analysis. Public
compatibility contracts and independent scientific references follow in the
later campaign. No replacement design is chosen by this report.

## Review disposition

The [single independent review](reviews/ml-fortran.md) identified conditional
energy centering and a scope-summary count correction. Both are corrected.
It also prompted a more precise residual-construction reference and wording
that identifies the broadcast quantity as a sampling interval. Those edits
were checked against the cited source. No second review or experiment ran;
the remaining scientific and implementation questions stay open.
