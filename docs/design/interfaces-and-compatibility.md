# Interfaces, compatibility and delivery

Part of [design draft 0.2](README.md). Researchers should be able to switch without
changing how they prepare calculations, run jobs or use the results. Native and
compatibility interfaces call the same engine. The tests must cover the methods
and workflows people actually use.

## 1. Entry points

Proposed commands, subject to interface review:

```text
exvasperated inspect --input calculation.toml
exvasperated prepare --input calculation.toml --run-dir run
exvasperated run --input calculation.toml --run-dir run
exvasperated history list --archive run
exvasperated history inspect --archive run --at ENTRY
exvasperated resume --archive run --at ENTRY --branch trial-2
exvasperated run --compat vasp-6.5.1 --directory calculation
exvasperated capabilities
exvasperated version
```

History commands use stable entry identifiers; a step number or timestamp alone
does not select an unambiguous point. `resume` starts a new branch from that
point after method-specific preparation. `history inspect` reads recorded data
without running a calculation. Native initialization from selected prior
quantities is a distinct input operation. See the
[history operations](calculation-history.md#3-operations-available-to-callers).
The illustrative `--branch` value is a human label; a new stable branch identifier
is allocated for the session, with conflicting labels rejected.

Native input is a versioned declarative document, proposed as TOML. It expresses
a selected calculation and its explicit composition, not an inferred experimental
intent. Complex workflows can compose library calls or separate runs. Introduce
additional native composition syntax only for specific calculation procedures;
there is no initial general workflow DSL.

The CLI returns a concise human explanation plus stable machine-readable outcome
fields. Diagnostic prose is original. Native stdout/stderr responsibilities are
specified so pipelines need not scrape mixed progress and data. MPI launch stays
compatible with the site's scheduler/launcher; the executable does not become a
cluster scheduler.

Compatibility launchers can provide familiar executable basenames in a separate
installation directory, with a configured compatibility profile. They select the
corresponding represented mode through the same engine. Installation does not
overwrite an existing VASP binary. Basename support is announced only after that
mode's semantics are implemented and tested.

Native process outcomes use a proposed small stable mapping: `0` for completion
of the requested operation, `2` for invalid/unavailable input, `3` for a method
limit or failure to meet its requested stopping condition, `4` for a controlled
stop, `5` for execution failure, `6` for required output failure, and `7` for an
internal error. Signal termination retains the platform/launcher behavior. The
structured summary carries the actual method outcome, delivery status and cause;
an exit integer cannot carry all three. Compatibility profiles can map legacy
process behavior separately, with the native summary preserving those facts.

## 2. What configuration means

Native configuration separates:

- The physical model and atomic-data selection.
- Representation/discretization choices.
- The requested method, its numerical controls and explicit child methods.
- Initialization versus resume/import.
- Execution resources and supported placement choices.
- Requested results and operational stopping/checkpoint policy.

The parser preserves source locations. It rejects duplicate native keys and
unknown native options, rather than silently accepting a typo. Profile-specific
compatibility parsing follows its own observed/documented syntax and precedence;
those rules do not leak into the native grammar. No inherited global mutable
parameter map is exposed to calculation routines.

Resolution computes context-dependent defaults in a defined order and presents
the effective configuration, including the origin of values that users commonly
need to understand. Static defaults are versioned. A change in default calculation
method is a documented behavior change, not a backend upgrade side effect.

Environment variables affect only documented operational choices such as data
search paths and execution setup, unless a compatibility profile explicitly
requires otherwise. Resolve relative paths from the declared input/directory
context. Native execution takes structured arguments; input files are not shell
programs. Explicit foreign executable interfaces use documented argv/working-
directory behavior.

Changing an input while a run is in progress does not mutate the resolved native
calculation. Stop/control requests use separate channels. An interface that reads
changing external input must specify when it reads and how those updates affect
the method.

## 3. VASP compatibility profiles

A profile names the VASP version and build mode it aims to match, plus the
combinations of features it has demonstrated. The first research anchor is 6.5.1; newer public documentation is
not automatically evidence for that version. Release notes state the tested
consumers and workflows. A profile is an adapter implementation with tests.

The adapter parses input with source locations, resolves public defaults,
input-file precedence and initialization behavior, then constructs the calculation
using the same drivers as native mode. Where a native method
cannot express a requested behavior, the profile reports the unsupported request.
It does not silently substitute an unrelated approximation.

A compatibility mode may implement a documented fallback, such as a particular
restart initialization fallback, when that is part of the selected profile. It
must expose the resulting effective choice and diagnostic. Native resume remains
strict. This is an explicit dialect distinction, not a universal repair policy.
The current public [ISTART](https://vasp.at/wiki/ISTART) and
[ICHARG](https://vasp.at/wiki/ICHARG) pages illustrate why file discovery can change
a calculation's initialization and basis policy.

### Compatibility surface

| Surface | Design obligation | Needed demonstration |
| --- | --- | --- |
| Launch and directory | Profile/mode selection, MPI use, working-directory and image contexts | Existing job script with executable substitution |
| Input syntax and meaning | Public tokens, defaults, repetitions, units, order and inactive options | Independent minimal inputs plus paired oracle probes |
| Atomic data | User-supplied data interpreted through the chosen formulation | Matched calculations and transferability checks, not only parser success |
| Structure/trajectories | Atom order, cell/coordinate conventions, constraints and velocity/history data | Consumer round trips and comparisons of uninterrupted and resumed calculations |
| Electronic files | Basis/spin/normalization, augmentation and restart policy | Import/export with matched representation and explicit limitations |
| Text/XML/HDF5 results | Quantities, ordering, schema and partial/failure behavior | Actual downstream operations using pinned consumer versions |
| Completion/stopping | Process outcome, diagnostics, stop requests and available outputs | Scheduler and interrupted-run scenarios |
| Plugins/external coupling | Callback meanings, units, order, state and distribution | End-to-end tests of the interface and the coupled calculation |

A recognized but inactive option needs profile-specific handling. A recognized
active option whose meaning is unsupported must fail before the calculation runs.
Unknown options should produce a precise diagnostic; a permissive behavior is
allowed only if the named profile deliberately defines it. Merely consuming a
parameter does not establish implementation of its effect on the calculation.

### Public interfaces and independent implementation

Implement code and explanatory text independently. Use public documentation and
public OSS consumers to establish interface tokens and behavior; cite their
versions in the research. Proprietary VASP source/comments/diagnostic prose and
private fixtures are excluded from tracked code, tests, docs and releases.

Compatibility writers use publicly established field names and format syntax.
They produce original explanatory diagnostics. If a consumer depends on a
proprietary undocumented string that cannot be supported under this boundary,
record the precise compatibility gap and seek a public interface route; do not
quietly claim that workflow works. Numeric legacy binary formats require their
own format/variant research and independently implemented tests.

User-supplied atomic data and private oracle files remain runtime inputs. They
are not shipped with the engine or copied into public regression fixtures. The
OSS distribution needs independently usable atomic-data choices, assessed per
method. An element name alone cannot select an equivalent replacement dataset.

## 4. Consumer-driven interoperability

The focused reading found ASE's adapter using several output files, atom ordering
and convergence information; py4vasp uses quantity selections and schema-version
requirements. These facts motivate complete consumer tests rather than isolated
file validation. [ASE adapter](https://ase.gitlab.io/ase/_modules/ase/calculators/vasp/vasp.html),
[py4vasp adapter](https://github.com/vasp-dev/py4vasp/tree/35a29126baca57592e87ddd1afa0bc934073713d/src/py4vasp/_raw).

Initial compatibility test subjects should include an existing ASE VASP
calculation and restart, py4vasp result inspection, a shell/MPI job, a relaxation
followed by postprocessing, and a trajectory interruption/continuation. Add
phonon, localized-orbital and correlated workflows as those methods are implemented.
Distinguish disagreements about the model or numerical method from interface,
ordering or unit errors.

The actual producer remains Exvasperated. Compatibility format-version fields
can identify the emulated schema expected by a consumer; also expose the real
producer/version and profile without polluting fixed grammars. Define the exact
placement in the format expedition. Never use a VASP version number to imply
that the proprietary executable performed the calculation.

Compatibility writers read the same calculated results as native writers. Writers do not recompute a different energy or invent missing
observables to satisfy a consumer. Cross-format comparisons check meaning and
units as well as array ordering and file shape.

## 5. Embedding and extension boundaries

Provide a native library API in the selected implementation language. It creates
a context, constructs/prepares a calculation, executes a selected method, and
returns a structured outcome and
owned/borrowed results with explicit lifetimes. The CLI adds process exit policy.
Native APIs can evolve during alpha; persistence schemas evolve explicitly.

A C ABI where needed uses opaque handles, fixed-width primitive encodings and explicit
buffer shape/stride/ownership. Every allocation has a matching release operation;
errors are returned through documented codes and caller-owned messages. No private
language layout, panic or foreign exception crosses the ABI. Python bindings, if
provided, build on that boundary or the native API with array lifetimes enforced
by the binding.

Operation interfaces should accept and return owning handles to existing
allocations when that matches the computation. Foreign adapters preserve the
allocator/deallocation identity and completion lifetime; transferring control
does not require the foreign routine to acquire a right to free the storage.
Shared read-only inputs and scoped borrows remain available where concretely
needed. A language boundary is not an instruction to copy, repack or migrate data.

Extensions supply specific parts of a calculation, with interfaces such as:

| Interface | What must be specified |
| --- | --- |
| Energy/force/stress provider | Geometry, units, requested quantities, total versus contribution, state and derivative meaning |
| Potential/operator contribution | Its representation, energy relation, response/derivative support and update point |
| Occupation/embedding update | Subspace, iteration stage, replacement/addition rule and synchronization |
| Bias or learned model | Algorithm state, acquisition/continuation semantics, requested observables |
| External dynamics driver | Request/session identity, force-provider initialization and continuity assumptions |

The method applies each returned contribution according to its rules. Extensions
do not edit a shared mutable “additions” object. Missing derivatives are
reported, not filled with zero. Specify the order in which extensions act; the order of package discovery cannot
decide the calculation.

Baseline host callbacks receive read-only borrowed inputs valid for the call and
return owned results. They cannot retain raw borrowed pointers. Asynchronous or
device-resident extensions need a separate completion-aware interface. Foreign
callbacks execute either on a designated rank with explicit distribution, or on
all participating ranks under a specified collective protocol. Rank-local and
global contributions are distinct. Exceptions and partial outputs do not commit
half of a composed update.

External providers are trusted code, not automatically sandboxed by the host language. Their
state must participate in checkpoint/rollback if that calculation promises those
operations. An embedded host owns its fatal-runtime policy; it must agree to the
MPI failure behavior before distributed execution. A subcommunicator is not a
promise that abort cannot affect the rest of the host job.

## 6. Packaging and operational usability

### Run-directory ownership

The following is the earlier filesystem-based candidate. Deployment and storage
choices remain open under the [core storage boundary](core-structure.md#5-storage-responsibilities-without-premature-deployment-choices).
This sketch does not choose a custom locking or publication implementation.

Before opening outputs, the designated writer acquires exclusive run-directory
ownership through a filesystem primitive qualified on the supported target
(for example, exclusive creation of an ownership file). Peers receive its outcome
before proceeding. Record enough process/job identity to diagnose collisions,
without treating a timestamp or PID from another node as proof that an owner is
dead. A stale ownership record requires an explicit recovery operation that
preserves prior outputs; ordinary startup does not steal it automatically.

Native fresh runs use a new directory or refuse conflicting calculation outputs.
Resume appends a branch and new segments/generations under exclusive archive
writer ownership. Concurrent readers use immutable entries; simultaneous branch
writers in one archive need a separately qualified protocol. Compatibility mode
applies its declared overwrite/append behavior only after selected restart inputs have been read or
preserved; opening an output must not truncate a file still needed as input.
Temporary names are per-run and noncolliding. Cleanup removes only files owned
by that run and never erases prior committed checkpoints merely because startup
or a later calculation failed.

### Builds and distribution

Provide reproducible CPU and NVIDIA build configurations with recorded compiler,
native-library and CUDA requirements. CPU execution should not require a working
CUDA installation. The NVIDIA package includes the selected backend's necessary
compiler/runtime pieces under their terms; the mere presence of the NVIDIA mode
must not change native CPU numerical defaults.

Installable binaries, development/library packages and source releases share a
versioned feature description. `capabilities` lists compiled methods/backends and
observable support; preparing a concrete job additionally checks the actual
combination and resources. A feature list is not a substitute for workload tests.

Alpha qualification includes serial CPU, threaded CPU, MPI CPU, single NVIDIA
and distributed NVIDIA configurations selected for supported workloads. Exact
minimum hardware, MPI implementation, filesystem and toolkit versions follow
measurements. AMD's later backend should fit the same ownership and operation
boundaries, but no portability framework is chosen in advance to promise that.

Apache-2.0 covers original project contributions. Every adopted library, dataset
and model keeps its own terms. Source-available references do not become shipping
dependencies through acquisition. Public release fixtures are independently
constructed or separately redistributable. Private oracle comparisons remain
separate from the distributable regression suite.
