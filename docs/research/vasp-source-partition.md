# Source partition and study order

2026-09-24. Scope: the complete recursive contents of the local VASP 6.5.1 `src/`
tree. The user wants deep analysis of every file over the course of the project.
This orientation establishes manageable study areas and an order for that work;
it does not claim those analyses are finished.

This map organizes the first stage of the
[project sequence](../../INERTIA.md#order-of-operations): deep studies with
detailed reports. Those reports inform the parity and improvement synthesis
that scopes the major research and reference campaign. System design,
specification, planning and implementation follow that research.

Target sequencing updated 2026-09-25: the user requires **CPU and NVIDIA GPU
execution in v1-alpha**, with **AMD GPU execution as a second-wave objective**.
Each study should identify the assumptions it makes about data placement,
precision, numerical libraries, parallel operations and target-specific behavior,
prioritizing CPU/NVIDIA and recording implications for later AMD support.

## What is partitioned

The [file inventory](vasp-source-inventory.csv) assigns **588 files to 20 study
areas**, exactly once per file. It records relative paths, sizes, physical line
counts and SHA-256 hashes, with no source excerpts. The tree contains **871,421
lines**, counting a final unterminated line where present. The earlier count of
871,419 counted newline characters only. There are no symlinks in this snapshot.

Hidden files, empty files, build configuration, documentation, test fixtures,
generated parser files, coefficients and bundled libraries are included. The
separate top-level VASP test suite, architecture templates, tools and PAW datasets
are outside this particular manifest; they remain relevant reference material.

Every file has one primary study owner. Cross-partition interactions remain
explicit questions for both owners. Keeping a subtree together is a navigation
choice, not a judgment that all its files implement the same kind of logic.
For example, the C++ machine-learning area includes its tests and packaging,
while the numerical area contains several bundled algebra implementations.

The inventory is reproducible with:

```sh
python3 scripts/inventory-vasp.py --check
```

Regenerating without `--check` updates the two CSV files after source or partition
changes have been examined. Unknown top-level files, missing assigned files,
duplicate assignments and symlinks cause rejection. Subtree additions inherit
their subtree's provisional owner and still change the checked inventory.

## The partition

The identifiers match the CSV. The last column defines what a deep study should
explain, not a claim that those questions have already been answered.

| Area | Files | Lines | Central question |
| --- | ---: | ---: | --- |
| `execution` | 16 | 13,780 | Which program is built, what runs when, and how does it finish or fail? |
| `foundations` | 5 | 1,199 | What do shared state, scalar precision and units mean? |
| `io` | 16 | 18,352 | How do inputs, defaults, results and continuation preserve meaning? |
| `geometry` | 14 | 25,214 | How do cells, symmetries and reciprocal samples transform quantities? |
| `representation` | 41 | 29,854 | How are wavefunctions, fields, grids and transforms represented? |
| `paw` | 20 | 44,641 | How do atomic datasets, projectors and augmentation define operators? |
| `electrostatics` | 16 | 15,224 | How are charge, boundaries and potentials assembled into the Hamiltonian? |
| `xc` | 10 | 25,898 | Which functional and spin conventions define local contributions and corrections? |
| `nonlocal_interactions` | 17 | 73,489 | How are exact exchange and dispersion evaluated consistently? |
| `electronic_solution` | 26 | 25,557 | What is minimized, what is mixed, and what establishes convergence? |
| `ions` | 15 | 18,470 | How do forces drive relaxation, trajectories, constraints and sampling? |
| `response` | 20 | 38,584 | What perturbation is applied and which response is actually calculated? |
| `many_body` | 42 | 157,269 | What screening, frequency, correlation and excitation approximations are made? |
| `vibrations` | 16 | 31,404 | How do displacements and electronic responses become phonons and transport? |
| `localized` | 35 | 46,934 | What do projections, localized orbitals, embedding and interchange preserve? |
| `ml_fortran` | 26 | 52,255 | How are learned forces trained, selected, evaluated and coupled to dynamics? |
| `ml_cpp` | 162 | 64,795 | Which contracts connect the C++ library, model files, applications and tests? |
| `plugins` | 26 | 2,993 | What may external code change, and how are shapes, units and failures handled? |
| `parallel` | 34 | 24,478 | Who owns each value, device allocation and collective decision? |
| `numerics` | 31 | 161,031 | Which numerical contracts and library variants support the scientific algorithms? |

This deliberately gives small but influential files their own attention. Size is
not a measure of scientific importance. The large correlation area should itself
be traversed through screening, frequency/quadrature machinery, GW/RPA, MP2 and
BSE investigations. The learned-force-field areas likewise need smaller passes
through data meaning, descriptors, fitting/prediction, derivatives and execution.
Their parent partition does not prescribe a single large review.

## Why this ordering

A coarse scan of 345 Fortran/include files found 4,069 candidate file-to-file
module-import links. The [aggregate links](vasp-partition-links.csv) record
consumer-to-provider direction. Examples of highly shared providers are
`base.F` (274 importing files), `constant.F` (167), `lattice.F` (145), `mpi.F`
(141), `wave.F` (122), `poscar.F` (118) and `mgrid.F` (112). These numbers describe
syntactic imports, not execution counts or the amount of behavior reused.

The scan includes alternative preprocessor branches, permits multiple candidate
providers, and does not expand includes or resolve calls. It does not analyze
C++ or Python imports. It cannot establish reachability, supported builds or a
complete dependency graph. It does show that interpreting advanced routines
before shared representations would leave many assumptions unexplained.

`main.F` imports providers in all 20 study areas in this scan. It is therefore a
good initial route map and a poor candidate for an exhaustive first deep dive.
The opening pass should identify its phases and branch conditions, then follow
the corresponding areas in bounded studies.

The proposed order is:

1. **Establish the run contract.** Study `execution`, `foundations` and `io`:
   build variants, lifecycle, state identity, units, input interpretation,
   stopping and continuation. At this stage identify the entry contracts for
   parallel execution, numerical libraries and plugins, accounting for the
   required CPU and NVIDIA GPU alpha targets and the later AMD objective. Identify
   reference build branches, missing implementations and external dependencies
   separately for each target. Produce a map of a job from invocation through final output,
   with unsupported and failure paths.
2. **Understand representations and atomic data.** Study `geometry`,
   `representation` and `paw`. Follow `parallel` and `numerics` in the context of
   the data they distribute and operate on. Explain normalization, indexing,
   symmetries, projector meaning and transfers between representations. Inspect
   bundled library provenance and variants before deciding what deserves
   independent reuse; every bundled file still receives analysis. Investigate
   data layouts, host/device ownership and numerical-library availability for
   CPU/NVIDIA, recording implications of those choices for later AMD support.
3. **Close the electronic energy calculation.** Study `electrostatics`, `xc`
   and `electronic_solution`, then `nonlocal_interactions` and revisit their
   effects on the solve. Connect the operator, density, energy terms,
   occupations, updates and termination. Understand a whole calculation before
   choosing our engine boundaries or implementation sequence.
4. **Follow derivatives and physical evolution.** Study `ions` and `response`
   against the already understood energy calculation. Relate energies to
   forces, stress and perturbation responses; follow constraints and dynamics.
   Include derivative contributions owned by earlier areas, such as exact
   exchange. This is where independently derived consistency checks become
   concrete scientific experiments rather than generic testing advice.
5. **Study the advanced branches with their prerequisites visible.** Deepen
   `localized`, then examine `many_body` and `vibrations` in separate bounded
   sequences. Localized representations also feed earlier initialization and
   analysis paths, so inspect their required contracts when first encountered.
   Do not assume a total ordering between all advanced methods: follow the
   actual representation and response prerequisites of each calculation.
6. **Study learned forces and close the integration loop.** Examine
   `ml_fortran` and `ml_cpp` with force, stress, dynamics and model-data semantics
   established. Complete the full `plugins`, `parallel` and `numerics` reviews
   alongside their remaining consumers. Revisit whole jobs, restarts, external
   consumers and feature combinations. Define alpha workloads and scientific
   acceptance on CPU and NVIDIA GPU, including evidence of execution on each
   target, with AMD validation in the second wave. These areas are surveyed in the
   opening pass and followed throughout; their constraints cannot be deferred
   until here.

This is a study order, not an implementation roadmap. Dependencies are cyclic;
we will revisit an earlier contract when a later consumer exposes a missing
assumption. Reassign a file when its behavior warrants it, preserving complete
coverage. A promising DFT example must not narrow the eventual parity scope.

## Findings that shape the partition

These are observations from selected source sections. They are not verified
behavior from an executable and not completed per-file reviews.

- **Build choices change representation.** The opening part of `makefile`,
  especially lines 28-86, selects optional libraries and different reduced-grid
  choices according to the executable and parallel build. Build analysis and
  grid analysis therefore need to meet early.
- **Stopping is shared state with several meanings.** `electron_common.F`
  lines 15-65 handle numerical thresholds, startup/minimum iterations, maximum
  steps and explicit stop requests. The main driver handles the consequences
  around lines 5875-5896. Termination and scientific convergence need separate
  examination, including the single-step case and subsequent ionic evolution.
- **Collective control flow needs attention.** The explicit stop-file path in
  `electron_common.F` lines 90-108 performs a collective reduction, while an
  earlier branch may return first. Whether all ranks take compatible paths
  depends on the surrounding algorithm and communicator. This is a concrete
  dependency to trace, not a demonstrated deadlock in this snapshot.
- **Constants and conversions are part of compatibility.** `constant.F`
  contains a mix of stored and derived conversions and constants. Their
  precision, provenance and consistency with callers need study; numerical
  disagreement cannot immediately be attributed to a solver algorithm.
- **A feature-shaped file can be an extension hook.** `solvation.F` contains
  inactive interface behavior in this distribution, while `afqmc.F` rejects
  selection of the corresponding method and has an empty propagation body.
  Neither filename alone establishes an implemented solver.
- **Large files need different research approaches.** `minimax_dependence.F`
  begins with fitted-coefficient tables; `lib/` contains several long algebra
  sources. Coefficient origin, generation, numerical domains and library
  provenance may matter more than traversing every repeated assignment in
  order. This does not authorize copying tables or skipping file analysis.
- **There are multiple learned-force-field implementation surfaces.** The
  flat Fortran family and the separate C++ subtree have different source,
  build and test structures. Determine their actual relationship, activation
  and data interchange before treating them as interchangeable implementations.
- **Compatibility crosses the process boundary.** The plugin subtree contains
  Fortran/C++/Python interfaces, packaging and tests; the localization parser
  contains grammar and generated parsing files. Study the originating contract
  and generated artifacts together, including units, errors and memory lifetime.

## How deep study will use this map

Maintain a per-file reading record with the examined ranges and source hash.
Distinguish unexamined material, partial inspection and a completed analysis;
an inventory hash or an import count is never the completed analysis. A file
review should explain its role, scientific or operational contract, dependencies,
assumptions, numerical choices, mutation/ownership, failures and relevant build
conditions. Identify meaningful counterexamples or experiments where appropriate.
Preserve unresolved cross-file questions rather than filling them with guesses.

Each useful study pass should produce a detailed report brought back to the user,
synthesizing the behavior and interactions understood so far. A
collection of isolated file summaries would miss the complexity this exercise is
intended to uncover. Mathematical claims, source observations and results from
experiments remain distinguishable. Write all analyses in original prose; source
locations and public interface documentation provide the references.

An area may take several visits. Move to another study when it is likely to
supply missing context or make better progress, and return as those connections
become clearer. Each partial report should identify the remaining questions,
their effects on current conclusions, and the findings or related work that
should prompt a revisit. Keep actionable follow-up in beads. Completing a bounded
pass and settling an entire area are distinct outcomes; no percentage estimate
substitutes for explaining what is understood and what remains open.

Reports should also identify the parity obligations, possible improvements and
open scientific or engineering questions that the later research campaign must
address. Keep proposed improvements distinguishable from observations of VASP.
Use focused references when needed to understand a source claim; the full
literature and reference-acquisition campaign is scoped from the study reports
and their synthesis.

The present orientation does not mark any file as deeply analyzed. It records
selected findings and complete partition membership. Beads holds the ongoing
research work under `exv-6l0`; this document is the rationale for its organization.
The first proposed deep study is the executable lifecycle and build-selection
contract, beginning with the build description, object list, conditional
configuration, main driver and parallel startup, consulting shared state and
input entry points as needed. CPU and NVIDIA GPU paths and dependencies have
first-wave priority; AMD remains a later execution objective and source-study
subject. Hardware generations, toolchains and backend implementation choices
require subsequent design and evidence.
