# Results, persistence and continuation

Part of [design draft 0.1](README.md). Persistence must preserve the meaning of
what was calculated and the state required by the chosen continuation procedure.
Container readability is only one requirement.

## 1. Result semantics

Drivers expose distinct views for iteration diagnostics, evaluated observables
and continuation. Their types describe actual scientific quantities and stage,
without attaching a generic “valid science” object.

A result identifies its geometry, representation, model choices and evaluation
point. Named energy components distinguish total energy, free energy and other
method-defined quantities; a bare `energy` field cannot quietly change meaning
between methods. Forces/stress identify the energy/occupation/basis convention
being differentiated. Units, tensor axes, atom order and reciprocal indexing are
explicit at serialization boundaries.

An SCF iteration may have an incoming mixed density, newly computed orbitals and
several energy estimates. Expose them as such in diagnostic output. Only the
method's final evaluation creates its final result view. Similarly, integrator
half-step velocities and full-step positions are not serialized as an ordinary
complete trajectory frame without their actual stage meaning.

The result API represents unavailable or unevaluated quantities explicitly. An
absent stress is not a zero tensor. A result from an exhausted iteration budget
can be useful and inspectable while retaining that method outcome. Scientific
completion and successful delivery of the requested files remain distinct in the
final run summary.

## 2. Native storage proposal

### Accepted restoration commitment

Following the user's append-only log proposal and clarification on 2026-09-25:
**selecting a recorded point recovers the state actually recorded there, including
its retained history.** Continuing from that point appends a branch and preserves
the previously recorded future. Restoration reads recorded state; it does not
depend on rerunning the numerical procedure to reproduce that state.

This operation does not establish physical reversibility or undo a thermodynamic
process. Deterministic numerical replay is not an established project goal. The
method must separately establish whether the recorded state suffices for the
requested continuation. A point containing only selected observables can support
inspection without supporting resume.

The logical history may reference immutable, distributed array payloads. Each
committed entry identifies its parent and its complete recorded contents, either
directly or through retained dependencies. Snapshot placement, exact encodings,
recording cadence and physical layout remain proposals to refine. A promised
restore point must retain every payload needed to recover its recorded state;
pruning cannot silently break those references.

### Proposed physical storage

Use a versioned native format with **HDF5 array containers** and a small readable
index for each published generation/segment. This is a proposal pending binding,
parallel-IO and filesystem experiments. Compatibility files use their own adapters.
The generation/segment layout below is a candidate payload organization for the
logical history; parent links and entry indexing still need specification.
Native persistence never serializes Rust object layout, pointers or enum memory.
Checkpoint payloads preserve the working scalar encoding by default, with only
lossless compression. Reduced-precision export is a distinct explicit operation;
it cannot silently narrow native continuation state.

A conceptual run layout is:

```text
run/
  resolved-input.toml
  run-summary.json
  progress.jsonl
  results/
    segment-000001.h5
    segment-000002.h5
  checkpoints/
    generation-000001/
      index.json
      state-000000.h5
      ...
    generation-000002/
      index.json
      state-000000.h5
      ...
```

Names are illustrative, not a final file-format specification. The summary is
atomically replaced where the filesystem supports the required behavior. Progress
is for observation; it is not replayed to reconstruct scientific state. A torn
last progress record does not invalidate an earlier committed checkpoint.

Each committed segment is immutable. Its index gives schema version, logical
array descriptions and file membership; checksums detect incomplete/corrupt
payloads. Small jobs can use one HDF5 file. Large jobs use explicitly indexed
shards or collective parallel HDF5, selected by measured IO behavior. MPI rank
number is not a scientific array index.
Result segments use the same temporary-write, successful-close and final-name
publication discipline as checkpoints. An actively written segment is not exposed
as committed native output.

Include the effective input, program/method/schema versions, atomic-data identity,
precision and relevant backend settings once at useful granularity. This is
ordinary reproducibility information and diagnostics. It does not create an
accounting system around every calculation operation.

Large output is streamed through bounded chunks. Writers must not gather every
wavefunction onto rank zero. HDF5 access modes and collective metadata operations
are chosen consistently among writers. Live readers consume completed native
segments by default. SWMR is a separate optional live-output mode to qualify;
its restrictions and flushing model do not implement a multi-file checkpoint
transaction. [HDF5 reference](https://portal.hdfgroup.org/documentation/hdf5/latest/_s_w_m_r_t_n.html).

## 3. What continuation means

VASP already provides method-dependent restart facilities. Its public documentation
describes electronic continuation through WAVECAR and CHGCAR, structural and MD
state in CONTCAR, and controlled stopping through STOPCAR. CONTCAR is written at
each ionic step; that does not establish that every restart file is refreshed at
the same cadence. Electronic-step stopping can leave unconverged electronic data.
For each compatibility workflow, study exactly which state is retained, which is
reconstructed, and the consequences for subsequent iterations or trajectories.
These facilities do not by themselves establish a universal all-history replay
guarantee. [WAVECAR](https://vasp.at/wiki/WAVECAR),
[CONTCAR](https://vasp.at/wiki/CONTCAR), [STOPCAR](https://vasp.at/wiki/STOPCAR).

| Operation | Meaning | Required behavior |
| --- | --- | --- |
| Native resume | Continue a specified procedure at one of its defined boundaries | Restore its required physical, algorithmic and external state; reject missing state |
| Initialize from prior result | Start a new procedure using selected previous quantities | State explicitly what is reused and what is newly initialized |
| Transform/import | Convert an external or differently represented result | Apply a method-defined mapping and report its limits |
| Inspect/postprocess | Read selected quantities without continuing the procedure | Require the actual prerequisites for the requested analysis |

The default native `resume` does not silently drop histories or substitute another
model. Changing only output cadence or a permitted resource arrangement can be
allowed by the method's resume rules. Changing time step, solver, dataset, basis
policy, occupations, physical field or learning model requires method-specific
interpretation. The core cannot classify all such changes as harmless settings.

A supported resume claim preserves the defined algorithmic state. Restoring the
recorded values and obtaining identical future numerical trajectories are separate
claims. The latter is not required by this design, even with unchanged execution
settings. Any future replay proposal must first establish its purpose, equality
criterion, scope and scientific relevance before feasibility is investigated.
Statistical agreement alone cannot demonstrate that all state required for a
particular continuation was saved.

### State each family must decide to retain

- Electronic iterates: orbitals, densities, occupations and any PAW on-site,
  kinetic-density, subspace or constraint state used by the selected procedure.
- Solver history: mixing vectors, residuals, adaptive thresholds, preconditioner
  state or extrapolation history where required for the resume claim.
- Nuclear motion: positions, momenta, cell variables, stage, constraints,
  thermostat/barostat variables and optimizer history as appropriate.
- Stochastic sampling: generator algorithm/version, full state or counter mapping,
  stream assignment and any cached variates; a seed alone is not generally enough.
- Fields/response: coupled fields, time/phase/branch data and propagator memory.
- Learned methods: fitted model, acquisition/fitting history and state required
  for future learning decisions; frozen inference and resumed learning differ.
- External components: serialized session state or an explicit supported reset
  procedure. An external side effect that cannot be restored limits resume.

This list is a prompt for each scientific expedition, not a completed universal
checkpoint schema. A family defines its checkpoint payload at a named boundary
and its decoder/migrations alongside the algorithm. Derived data may be omitted
only after establishing what reconstruction means for that resume claim.

## 4. Snapshot and publication protocol

Baseline checkpointing pauses the relevant driver at a **method-defined coherent
boundary**. It need not copy all scientific state at every step. Until another
checkpoint is safely published, the previous committed generation is the
recoverable state. An unexpected failure can lose work since that generation.

1. The driver establishes a boundary common to all participating subsystems and
   ranks, including required external state. It completes device/MPI operations
   that affect the payload.
2. It exposes an immutable snapshot view. Synchronous serialization holds that
   view until completion. Future asynchronous serialization must either own a
   separate snapshot or retain/freeze the referenced allocations until copied.
3. Writers create a fresh temporary generation on the destination filesystem.
   Array shapes, scalar encoding, logical layout and method stage are written
   with the payload. No previously committed file is overwritten.
4. Every writer closes successfully and performs the supported persistence steps.
   Live-rank agreement confirms all required files succeeded; a partial generation
   remains unpublished on failure.
5. The coordinator writes and persists the index describing the complete files,
   closes it, and persists directory entries inside the temporary generation
   (including any nested directories). It then renames the temporary generation
   to its final name and persists the parent directory where supported.
   Publication is the final name plus a
   complete readable index and matching payloads.
6. Only after publication may a branch-head hint be updated. Existing entries and
   branches remain intact. Any later explicit pruning policy must retain all
   dependencies of retained restore points and state which points it removes.

The generation sequence is allocated once by the calculation's output owner;
writers must not collide. Same-filesystem rename and successful writes do not
alone establish power-loss durability on every HPC filesystem. Qualify file/
directory synchronization, filesystem semantics and failure behavior on release
targets. [Linux rename](https://man7.org/linux/man-pages/man2/rename.2.html),
[Linux fsync](https://man7.org/linux/man-pages/man2/fsync.2.html).

No post-failure collective is assumed to work after rank death. In that case the
last published generation remains the recovery candidate. A complete but not yet
published temporary generation is not automatically promoted by the reader.

A checkpoint deadline requests the next available scientific boundary. It cannot
force a mathematically incomplete substep to masquerade as a complete state.
Methods with extremely long steps should investigate substep checkpoints with
explicit saved stage/history; the app cannot invent them.

## 5. Reading, migration and resource changes

On read, validate schema versions, required files, dimensions, checksums and
logical indexing before exposing scientific state. Enforce allocation-size limits
and checked size arithmetic. Unknown mandatory method state is an error; optional
fields have explicit schema rules. Never deserialize executable host objects.

Decode persistent data into versioned records, then use the method constructor
and migration code. A migration is an explicit transformation with tests; it does
not merely relabel the version. If the physical/numerical meaning cannot be
preserved, offer a documented initialization/import route instead of calling it
resume. Native checkpoint schema and public result schema evolve separately.

Rank/device changes reconstruct execution resources and redistribute canonical
logical arrays. Saved basis ordering, phases and method state must survive. A
fresh geometry-based reconstruction that chooses a different order or branch
is not equivalent by default. Histories tied to a decomposition need a defined
mapping or a declared restriction on resume. The file format should support
repartitioning; particular scientific methods may initially restrict it.

Atomic-data references include content identity and interpretation metadata.
Portable runs can include an explicitly requested data package under its own
terms; default output should not silently duplicate entire private data libraries.
A resume must locate the same required data or a scientifically defined conversion,
not pick the newest file with a matching element name.

## 6. Outputs, restart segments and external side effects

Native resumed runs append a branch linked to the selected recorded state, with
new result segments linked to that branch and checkpoint.
They do not append behind a trajectory tail that may have advanced beyond that
checkpoint. Accepted-step/frame identifiers expose any intentional repeated
portion; the reader follows the selected continuation, preserving the original
segment. Compatibility append/overwrite behavior is implemented per profile with
explicit treatment of old files.

Output stages have separate completion. A result may have been computed but fail
to reach disk; a checkpoint may succeed while an optional plot export fails.
The summary reports those actual outcomes. Required outputs are fixed by the
request; the program does not downgrade them to optional after an IO failure.

Scientific callbacks with external mutations complicate rollback. Prefer staged
returns that are applied once at a method boundary. A protocol that provides only
“send request, receive response” cannot promise exactly-once external effects
after a crash. Do not automatically retry an ambiguous request. Stable request
identifiers and component-supported deduplication can improve this, but must be
specified and tested for that interface.

### Failure walkthrough

| Interruption | Reader-visible state | Recovery behavior |
| --- | --- | --- |
| Halfway through a shard | Temporary generation only | Use prior committed generation |
| One writer fails while others finish | No new published index/generation | Report failure; retain prior generation |
| After all files close, before publication | Complete temporary directory | Still uncommitted; no automatic resume from it |
| After publication, before latest hint | New final generation exists | Discover by index validation; hint is only an optimization |
| Stale result tail after resuming older checkpoint | Prior segment remains intact | New continuation segment, no misleading append |
| Corruption in explicitly requested checkpoint | Hash/schema failure | Fail that request; never silently resume a different checkpoint |
| New backend changes roundoff | Same decoded logical state, potentially different path | Apply the method's declared resume scope; no bitwise claim |

These cases have been reasoned through on paper. Filesystem crash tests and
method-specific split-run experiments remain required before implementation is
accepted.
