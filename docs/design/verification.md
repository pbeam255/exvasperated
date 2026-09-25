# Verification and completion of the design

Part of [design draft 0.1](README.md). These are proposed obligations and tests,
not tests already passed by an engine. Source reading, architecture reasoning,
executable verification and physical validation establish different things.

Verification consists of concrete mathematical reasoning, executable checks,
counterexamples and measurements. Keep the supporting notes directly useful and
revisable. Do not add certification/evidence objects, authority hierarchies,
approval rituals or ADR machinery to the application or development process.

## 1. Core properties worth specifying precisely

Use small executable protocol models where they can expose an error. Quint is a
candidate for the lifecycle/checkpoint/collective protocols; select tooling when
implementing the model. Most protocols currently have plain notation and
transition tables. The [history refinement](calculation-history.md#7-bounded-protocol-exploration)
adds a small exhaustive Python transition-system exploration for publication and
recovery. MPI/lifecycle models remain unimplemented; Quint has not been run.

| Property | Precise intended statement | Necessary scope/assumptions |
| --- | --- | --- |
| Resource lifetime | An allocation cannot be reclaimed while any submitted operation can access it | Include foreign accesses, failure paths and event-recording failures |
| Scientific association | An operation cannot accept data associated with a different required representation | Static lifetime/type associations where possible; checked runtime identity elsewhere |
| Collective ordering | Participating ranks initiate matching operations in the same order on a communicator | Include subgroups/overlap and earlier local failure; exclude an invented recovery guarantee after rank loss |
| Checkpoint coherence | Every published payload belongs to the same defined method boundary | Driver supplies a coherent snapshot; external state participates where required |
| Recorded-state restoration | Selecting a retained log point recovers its recorded state and retained history | Include parent/shared-payload dependencies; future trajectory equality is a separate, unestablished claim |
| Branch preservation | Continuing from an earlier point leaves the previously recorded future unchanged | Branch identity and parent links persist; explicit pruning must preserve dependencies of retained points |
| Publication | No final generation is visible as committed before all its required files succeed | Actual filesystem publication/durability assumptions are qualified |
| Preservation | Failure while creating a new generation leaves an older committed generation unchanged | No automatic deletion in the proposed baseline; storage may itself fail |
| Save acknowledgement | A successful save acknowledgement follows durable publication of its entry and dependencies | Visibility alone is insufficient; uncertain outcomes are recovered by entry identity |
| Outcome fidelity | Process completion never changes the reported method outcome | Output/cleanup failure is represented separately |
| Result ownership | A writer/observer cannot see a field mutated while it reads it | Applies to host borrows and asynchronous device work |

For a checkpoint model, let `g` identify a generation; track each writer as
`not_started`, `writing`, `closed` or `failed`, plus `index_closed` and `published`.
The publication transition requires every required writer to be `closed` and the
index to be complete. Crash transitions can occur between any two steps. The
model must distinguish namespace visibility from durable persistence. A second
model explores preparation/readiness and collective phases over two or three
ranks, with errors before/after a phase. It must reject unilateral return followed
by peers entering an unmatched collective.

These are small operational protocols. They do not attempt to model-check DFT,
prove that an SCF branch is physically desired, or attach certificates to results.

## 2. Scenarios used to challenge this draft

| Scenario | Required design behavior | Remaining check |
| --- | --- | --- |
| One rank cannot read input/data | Owner/readiness phase communicates failure before peers enter dependent work | Multi-rank injected failures during resolution/preparation |
| GPU launch succeeds, later synchronization fails | No final result from the affected operation; no early free of buffers | Device error injection and sanitizer runs |
| Trial geometry rejected after RNG/extension use | Driver restores or deliberately accounts for all method state | Method-specific rollback comparison |
| Wall-time signal during half-step | Stop request waits for supported boundary, or prior checkpoint remains | Signals at every integrator stage |
| One checkpoint shard fails | New generation stays unpublished; prior generation is preserved | Filesystem write/close/space failures |
| Checkpoint published but hint update fails | Reader can discover valid final generation independently | Crash-point tests around publication |
| Resume with different MPI layout | Restore logical arrays and method state under a defined mapping | Rank-count permutation tests plus numerical-path study |
| Resume with missing history | Strict native resume fails; explicit initialization remains possible | Schema/migration and scientific split-run tests |
| Restore an older log point and continue | Recover recorded values/history and append a branch without changing the original future | Lossless storage round trips, parent/dependency checks and branch preservation tests |
| Same coordinates reached through different histories | Distinct state remains possible; no position-only cache equivalence | Hysteretic/bias/branch-sensitive workloads |
| External client sends unrelated next configuration | No unearned trajectory-continuity assumption | i-PI/session request tests |
| Consumer expects additional outputs | Compatibility preparation checks support; writers expose real quantities | ASE/py4vasp full operations and partial-run cases |
| Two runs use the same output directory | One owns the directory or both use distinct names; no file collision | Concurrent launch and stale-owner recovery tests |
| Required output fails after science completes | Overall delivery failure with scientific result status retained | IO failure propagation through CLI/library |
| Rank disappears in a collective | Job failure; no promise of checkpointing the current state | Launcher timeout/abort tests and prior-checkpoint recovery |

This is a bounded paper review of the architecture. These scenarios are not
claimed as executed implementation tests. A later bounded history protocol model
checks publication/recovery under its stated abstractions. Add concrete tests with
the corresponding implementation increment; avoid a late catch-up testing campaign.

## 3. Scientific acceptance

Each subsystem expedition derives equations, domains, conventions, approximation
choices and discriminating cases before detailed design. Its implementation plan
pairs each operation with tests capable of rejecting a plausible scientific error.
Test composition as well as individual routines.

The comparison set should combine:

- Independently derived finite problems and analytic limiting cases.
- Discretization, solver and time-step convergence assessed separately.
- Derivative comparisons that hold model, branch, occupation and basis convention
  fixed where the derivative exists.
- Independent implementations with identified shared libraries/data/approximations.
- VASP oracle agreement under a recorded version/build/input configuration.
- Experimental comparisons where validating the physical model is the question.

No single scalar tolerance or universal “converged” flag spans these claims.
Phase/gauge freedom, eigenvector degeneracy, metastable branches and stochastic
trajectories require the appropriate observable or distribution comparison.
Hysteresis is not a defect to be removed by forcing histories to agree.

The broad campaign offers useful initial cases: insulator/metal/slab SCF,
PAW metric and dataset limits, force/stress derivatives, finite-field paths,
canonical sampling and biased continuation, polar phonons/transport, GW roots,
Wannier subspaces and learned-model derivative/acquisition behavior. Turn them
into specified workloads through the focused studies; do not label this list
complete capability coverage.

## 4. Execution and interface acceptance

Qualify CPU serial/threaded/MPI and NVIDIA single/distributed execution for the
scientific combinations offered. Record hardware, toolkit, compiler, MPI and
native libraries. Compare scientific results before timing. Include data layout,
transfers, reductions, memory pressure and persistence, not just GEMM or a toy
kernel. CPU/GPU differences are investigated rather than normalized away.

For cuda-oxide (`exv-x34`), use representative FP64/complex contractions,
reductions and operator/FFT-library interactions. Inspect generated code and
measure numerical error, compilation/toolchain constraints, memory/stream
behavior and end-to-end performance. Its release label provides no decision.
Compare the role of custom kernels separately from vendor BLAS/FFT/solver calls.

Compatibility acceptance uses independently authored public inputs and acquired
OSS consumers under their terms. Test complete operations including atom order,
units, restart mode, unsupported quantities and nonconverged/interrupted runs.
Private VASP oracle outputs do not become public fixtures. Document exactly which
versioned combinations work and what remains unsupported.

Parser and persistence code deserve malformed-input tests: excessive dimensions,
integer overflow, truncated files, unknown versions, inconsistent shapes and
bad checksums. Protocol/lifetime tests should exercise dropped observers,
exceptions, interrupted transfers and shutdown. Run such checks where they
challenge real implementation behavior; don't create tests that merely mirror
configuration or assert a diagram exists.

## 5. Proposed implementation sequence after design refinement

This is a dependency order, not authorization to begin implementation in this
turn or a scientific scope reduction.

1. Complete core protocol/API details and select bounded execution/storage
   experiments. Resolve actual Rust/FFI, MPI-thread and filesystem behavior.
2. Deeply study representations, required numerics and atomic data for the first
   scientifically meaningful calculation. Specify it and its difficult tests.
3. Deliver a vertical native CPU calculation with its real scientific routines,
   structured outcome, output and meaningful tests. Avoid a large empty framework.
4. Implement native continuation and interruption for that method, together with
   split-run and failure tests. Add MPI/NVIDIA execution and the numerical
   comparisons needed to qualify them; these are alpha work, not optional later
   optimizations.
5. Deliver the corresponding compatibility workflow through real consumers,
   including initialization/continuation and failure cases.
6. Expand scientific families/compositions through their focused expeditions and
   paired design/implementation/tests; broaden both backend and workflow coverage.

The first vertical calculation and alpha capability set still require explicit
scientific selection. Neither this sequence nor a limited first calculation
redefines the ambition of broad VASP parity without researcher downgrades.

## 6. Open decisions and tradeoffs

| Decision still requiring evidence | Current proposal | What could change it |
| --- | --- | --- |
| Native array/container binding | HDF5, explicit native schema | Rust binding quality, collective IO, target filesystem measurements |
| Large checkpoints | Immutable indexed generation; sharded or collective payload | File-count costs, throughput and portability experiments |
| MPI concurrency | Initializing-thread communication | Proven need for additional progress/concurrency and a safe supported MPI mode |
| Numerical/GPU implementations | Narrow adapters, FP64 baseline, no chosen compiler/library | Scientific error and end-to-end performance comparisons |
| Cache reconstruction on resume | Family-specific decision | Demonstrated effects on finite-precision or physical continuation |
| Native input/API details | Versioned TOML and typed Rust entry points | Concrete user workflows and composed method requirements |
| Compatibility baseline | Versioned 6.5.1 research anchor | User workflows, current public behavior and versioned oracle evidence |
| OS/hardware floor | Linux HPC qualification first; exact matrix open | Available targets and adoption needs |
| External state protocol | Explicit synchronous sessions and staged contributions | A concrete coupled method needing richer asynchronous behavior |

Actionable follow-ups are in beads. The design work is tracked as `exv-61f`;
`exv-8lk` retains focused subsystem expeditions, including deeper core execution/
compatibility work, and `exv-6l0` retains eventual every-file VASP analysis.
The concrete core follow-ups are `exv-0ex` (protocol specifications and executable
models), `exv-bl1` (Rust/CPU/NVIDIA/MPI integration experiments), `exv-w0s`
(persistence and output ownership qualification), and `exv-mqh` (versioned
compatibility workflows and core API details).

## 7. What has actually been checked for this draft

Selected source/paper/documentation reading is recorded in the
[study](../research/core-design-study.md), including its limits. The application
proposal was checked against the failure scenarios above and revised where a
coherent boundary, output ownership or cleanup path needed to be explicit.
Local Markdown links/anchors, supplementary acquisition hashes and Git whitespace
were checked for the initial draft. A subsequent history refinement ran the
original finite protocol explorer: 60 reachable states, 73 transitions and 66
crash-recovery cases, with its stated checks passing. See its explicit assumptions
and exclusions before interpreting that result. No engine, backend, numerical
workload, consumer workflow or physical filesystem crash experiment has been run.
