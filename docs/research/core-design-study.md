# Focused reading for the application-core design

2026-09-25. Study supporting the [overarching design draft](../design/README.md),
requested after the broad acquisition campaign. This is a substantive reading
pass over selected resources, **not a claim to have read all 110 references**.
It focuses on composition, state, interfaces, execution and continuation.
Scientific subroutine derivations remain with their focused expeditions.

The acquired revisions below are fixed by the [campaign catalogs](reference-campaign/catalogs/).
Additional public documentation snapshots are described in
[core-design-sources.json](core-design-sources.json); they supplement the original
campaign counts. Downloaded material and reading copies remain ignored. No
reference program was built or run, no numerical benchmark was performed, and
no proprietary implementation text is reproduced here.

## Reading and the conclusions it supports

### 1. A physical model, its discretization and its current iterate differ

Read DFTK's pinned `src/Model.jl` declarations and constructor documentation,
`src/PlaneWaveBasis.jl` declarations, and
`src/scf/self_consistent_field.jl` initialization/checkpoint helper and iteration
body, especially lines 165–290. The model/basis division is useful; the basis
contains both mathematical and execution-specific information. The SCF body
also distinguishes the incoming mixed density from the density of the current
orbitals and can recompute energy using the new state. Its finalization has a
separate operator/energy evaluation. [Pinned DFTK source](https://github.com/JuliaMolSim/DFTK.jl/tree/5a94a1407fa6fa47033e347bd65d7e3dbf163ac4/src).

**Design consequence:** input settings, model, representation and evolving method
state have distinct owners. An arbitrary iteration callback must not supply the
final energy/forces interface. Family-specific iteration data can expose the
actual quantities without claiming they describe one stationary state. Geometry
updates must reconstruct dependent representations through explicit operations.
DFTK's selected source does not establish PAW or every spin/response variant.

### 2. Iteration history is part of a selected solver

Read Woods–Payne–Hasnip's Kohn–Sham-map/convergence discussion, history-storage
argument, and Pulay/multisecant discussion. A density residual, energy difference
and convergence of a physical observable ask different questions. Limited-memory
updates use past density/residual pairs. Their omission can change the numerical
path even if the starting density is unchanged. Detailed convergence proofs and
the complete benchmark suite remain unread. [SCF study](https://arxiv.org/abs/1905.02332).

**Design consequence:** the solver owns stopping rules and its history. The app
transports outcomes and diagnostics; it cannot infer that a low scalar residual
selects the desired physical state. Restarting from a useful density and resuming
the same algorithmic procedure are separate operations.

### 3. Scientific drivers have their own lifecycle

Read QE `PW/src/run_pwscf.f90` startup, main-loop control and geometry/basis
reinitialization branches, plus `PW/src/stop_run.f90`. The sampled path separates
electronic, ionic and process outcomes; some geometry completion paths still
require a final electronic calculation with the final basis. Shell exit handling
also depends on a build option. [Pinned QE driver](https://github.com/QEF/q-e/blob/61569eb480231b649c47f631df9c5c83537df461/PW/src/run_pwscf.f90).

**Design consequence:** method completion is decided by the method driver.
Application cleanup cannot declare convergence or omit final method evaluations.
The CLI has an explicit process-status mapping; scientific outcomes are returned
by library calls independently. We have not audited all QE branches.

### 4. Checkpoint boundaries are scientifically meaningful

Read i-PI 3.0's architecture/interface discussion; pinned
`ipi/engine/outputs.py` 662–end (`CheckpointOutput`),
`ipi/engine/simulation.py` soft exit and main-loop sections, and
`ipi/inputs/simulation.py` storage of generator, step and motion state. It saves
a consistent prior state for interruption rather than assuming an arbitrary
mid-step object is restartable. Its force-client interface also does not promise
nearby successive configurations.
[i-PI paper](https://doi.org/10.1063/5.0215869),
[pinned checkpoint implementation](https://github.com/i-PI/i-pi/blob/1a93493d23c819fc0078ce1d9a85c83c37c846ee/ipi/engine/outputs.py).

**Design consequence:** method drivers expose coherent stopping/checkpoint
boundaries. External force requests need explicit session/continuation semantics;
arrival order is insufficient justification for extrapolation. Actual integrator,
thermostat and bias serializers still need their own deep studies.

### 5. Coupling and placement both affect application shape

Read the Octopus paper's software sections on the multi-system framework, memory
layout and GPUs (printed pp. 62–64), with preceding SCF context. Coupled fields
motivate multiple interacting subsystem states. Batched orbital layout and
persistent device storage motivate studying transformations and scratch memory
alongside kernel calls. This is historical implementation evidence, not a current
performance result. [Octopus paper](https://doi.org/10.1063/1.5142502).

Read heFFTe's pinned `include/heffte_fft3d.h` interface sections on scaling,
batching, workspace and plan construction. Plans depend on distribution and
execution resources, while batching changes workspace demand.
[Pinned heFFTe interface](https://github.com/icl-utk-edu/heffte/blob/4d8d4597b479d1e4709a2b1b4cd7d8922600045f/include/heffte_fft3d.h).

**Design consequence:** coupled scientific drivers own coupling equations and
subsystem states. The core supplies execution resources and explicit layout
changes. Scratch and in-flight work count toward memory planning. A universal
single-Hamiltonian object or scalar-task graph would hide necessary distinctions.

### 6. A Rust borrow ending does not mean a GPU operation finished

Read cudarc's pinned `src/driver/safe/core.rs` stream/event discussion,
`CudaSlice` destruction, `SyncOnDrop`, `DevicePtr`/`DevicePtrMut` implementations
(roughly 840–880 and 1200–1370), and launch argument construction in
`src/driver/safe/launch.rs`. Events connect device accesses and reclamation;
configuration can disable automatic synchronization. This is selected inspection,
not a soundness audit. [Pinned cudarc driver](https://github.com/coreylowman/cudarc/tree/ec1cac71dab29498240704a9e4a264fbbec19495/src/driver/safe).

**Design consequence:** our safe execution boundary must retain allocations and
plans until asynchronous use ends, including vendor FFI and MPI. It cannot
assume an upstream wrapper observes accesses performed through raw pointers.
The implementation must analyze every access and completion path before claiming
safe cross-stream borrowing. cuda-oxide remains a candidate, with the compiler
and numerical evaluation still open.

### 7. Collective control flow needs deliberate structure

Read MPI 4.1 §7.14 ordering/deadlock examples and §10.3 error handling; MPI 5.0
§12.2.1 initialization/thread-support definitions. Communicator ordering and
actual thread support constrain execution. A returned error does not supply a
portable recovery guarantee. These sections do not establish a requirement for
an MPI 5.0 deployment. [Collectives](https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report/node172.htm),
[errors](https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report/node252.htm),
[threads](https://www.mpi-forum.org/docs/mpi-5.0/mpi50-report/node269.htm).

**Design consequence:** the proposed baseline funnels MPI through the initializing
thread and structures communication phases in drivers. Local failures are
exchanged at known live-rank boundaries; rank death or a wedged backend requires
job termination, not an invented reliable all-reduce recovery scheme.

### 8. File integrity and scientific continuation are different obligations

Read HDF5's SWMR programming model/restrictions and selected H5F flush/close
entries. SWMR has a particular writer model and object-creation restrictions;
it is not an application-wide multi-file commit. Read Linux `rename` and `fsync`
semantics, including the distinction between synchronizing file contents and
the containing directory. [HDF5 SWMR](https://portal.hdfgroup.org/documentation/hdf5/latest/_s_w_m_r_t_n.html),
[H5F](https://portal.hdfgroup.org/documentation/hdf5/latest/group___h5_f.html),
[rename](https://man7.org/linux/man-pages/man2/rename.2.html),
[fsync](https://man7.org/linux/man-pages/man2/fsync.2.html).

**Design consequence:** publish immutable native checkpoint generations after
all required payloads have closed successfully. Qualify durability on actual
filesystems; use explicit format/state migration. A readable container does not
establish that integrator or solver history is complete. Parallel HDF5 tuning,
filesystem failure behavior and Rust bindings remain experiments before coding.

### 9. Compatibility is observed by consumers

Read ASE's VASP command/restart documentation and rendered source methods
`make_command`, `read`, `read_results`, `_read_xml`. The adapter combines XML,
text and structure data, including atom-order restoration and convergence
information. Read pinned py4vasp `_raw/access.py` selection/file/version paths
and `_raw/schema.py` construction interfaces. A schema's version fields affect
which quantities are accessible.
[ASE documentation](https://ase.gitlab.io/ase/ase/calculators/vasp.html),
[ASE source](https://ase.gitlab.io/ase/_modules/ase/calculators/vasp/vasp.html),
[py4vasp source](https://github.com/vasp-dev/py4vasp/tree/35a29126baca57592e87ddd1afa0bc934073713d/src/py4vasp/_raw).

**Design consequence:** verify whole consumer operations with versioned adapters.
Record a compatibility schema version separately from the actual producer. Do
not claim a parser or an HDF5 filename alone supplies replacement compatibility.
A source-text snapshot is not an executed consumer test.

### 10. Existing restart interfaces already select scientific operations

Read the public ISTART, ICHARG, WAVECAR and CHGCAR documentation. Their restart
choices distinguish basis policies, prediction history, density initialization
and augmentation content. Current public pages can describe behavior beyond the
locally studied 6.5.1 source. [ISTART](https://vasp.at/wiki/ISTART),
[ICHARG](https://vasp.at/wiki/ICHARG), [WAVECAR](https://vasp.at/wiki/WAVECAR),
[CHGCAR](https://vasp.at/wiki/CHGCAR).

**Design consequence:** import/export belongs at scientific adapters with explicit
representation changes. Native resume cannot be implemented as “read coordinates
and wavefunctions.” Compatibility defaults and documented fallbacks belong to
the selected profile and must be visible in effective settings. Full format and
method coverage remains open.

## Limits of the draft this supports

The design selects an application structure and proposes concrete operating
protocols. It does not prove numerical correctness, select a CUDA compiler,
establish every format, finish the every-file source study, or settle every
scientific history policy. The numerical families remain outlines. Core protocol
failure cases are worked through in the design; executable model checking,
fault injection, target measurements and consumer runs have not occurred.
