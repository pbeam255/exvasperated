# Calculation model and scientific composition

Part of [design draft 0.2](README.md). This specifies the core's responsibilities
and proposed ownership. Scientific routine internals remain at outline depth.
The [reading study](../research/core-design-study.md) supplies the source basis.

## 1. From a request to a running calculation

Use a staged construction sequence with explicit outputs:

| Stage | Produces | Checks and effects |
| --- | --- | --- |
| Parse | Source-located syntax | Grammar, primitive values, duplicate/unknown input handling under the chosen dialect; no scientific execution |
| Resolve | Explicit calculation specification | File references, documented defaults/precedence, method variants and requested products; report effective values |
| Construct science | Model and initial representation descriptions | Species/data matching, geometry, units, selected boundary/spin/occupation choices; structural consistency |
| Plan execution | Distribution, placement, buffers and operations | Required kernel/library support, rank/device topology, shapes and estimated memory |
| Prepare | Driver with owned state and resources | Allocate, load/convert selected initial state, build operators/plans; numerical setup may occur here |
| Execute | Method outcome and coherent result views | Driver-owned numerical procedure, stopping and output boundaries |

Some defaults require parsed atomic data or geometry. Resolution is therefore a
small explicit dependency sequence, not a single parser table. Cycles in default
dependencies are errors in the adapter. Native configuration has no hidden
working-directory restart discovery; the compatibility adapter can deliberately
implement its profile's documented file-dependent defaults.

Distributed construction begins with a collective bootstrap described in
[execution](execution.md). The input owner reads small configuration once and
shares it. Large datasets are distributed deliberately. All ranks must resolve
identical method choices; independent rank-local filesystem discovery is avoided.

`inspect` stops after resolution and static construction. `prepare` may perform
numerical setup and allocation. The interface must state that difference; a
preparation command is not advertised as a harmless syntax check.

## 2. Principal data and ownership

These names describe data and ownership, not final language APIs or an OOP model.
Use algebraic data types and explicit operations. Consumers interact through
public interfaces; the [core structure](core-structure.md) defines those boundaries.

| Data | Meaning and owner |
| --- | --- |
| `CalculationSpec` | Immutable resolved physical choices, procedure, numerical controls, initialization and requested products; owned by the application |
| `AtomicDataSet` | Immutable imported atomic ingredients with functional/relativistic/generator information and units; shared when genuinely identical |
| `GeometryFrame` | Cell, ordered atoms, positions and prescribed constraints at one configuration; driver controls replacement |
| `PhysicalModel` | Selected equations/terms, external conditions and spin/boundary choices; changing it is an explicit new model construction |
| Family representation | Basis, reciprocal sample set, real/radial grids, projector/overlap spaces and normalization conventions appropriate to that family |
| Family state | Orbitals/densities/occupations, trajectories, fields, response vectors or learned state; owned by its driver or child session |
| Family history | Mixer, propagator, thermostat, optimizer, bias, acquisition or branch history; owner is the algorithm that interprets it |
| `ExecutionContext` | Rank group, CPU workers, device contexts, library handles, placement and memory pools |
| Family result | Quantities actually evaluated at a named scientific boundary and the method outcome; immutable to consumers |
| Recorded family state | Immutable decoded values/history from a selected archive entry; the method constructs a continuation session from it where supported |

A model does not own mutable global geometry merely because many routines need
positions. A constructed problem pairs a model with a specific geometry and
representation. An ionic or coupled-field driver owns the evolving sequence.
A family can retain references to immutable constituents and reuse large
allocations, without allowing unrelated code to mutate scientific dependencies.

Use compile-time distinctions where the number of cases is stable and small:
real/complex scalars, coordinate conventions, host/device access, input versus
mutable output views. Runtime sizes, cells and basis identities still need
checked construction. Two arrays with equal dimensions are not necessarily in
the same basis. Where lifetimes cannot express that relationship, operation entry
compares lightweight representation identity and dimensions. Identity is a
structural association, not evidence of scientific accuracy.

Atomic units are the proposed internal convention for electronic calculations;
external adapters convert explicitly. Domain quantities and named views document
energy/length/time/charge, coordinate and stress conventions. Inner numerical
loops operate on scalars after those boundaries. No generic symbolic units engine
is required. Stress sign, Voigt ordering and cell-vector orientation require one
documented internal convention and explicit adapters; settle exact conventions
with the geometry/derivative expedition before implementation.

## 3. Composition uses concrete scientific interfaces

A method driver is ordinary scientific code with access to an execution context,
its owned state, bounded output callbacks and stop requests. The application
selects a driver variant, then calls it. Drivers can invoke child methods and
retain child sessions where their histories are needed.

A method defines its recorded state alongside its working state. A snapshot
operation exposes named immutable serialization views at a supported stage;
restoration decodes those values, and continuation preparation reconstructs
execution resources and any explicitly permitted derived quantities. The archive
stores these records without driving the numerical algorithm through event replay.
The [history design](calculation-history.md) defines the application operations.

Examples of domain APIs to design in their respective expeditions:

- An electronic session constructed for a model/representation evaluates a
  specified geometry with a selected initialization and solver policy.
- A derivative evaluation obtains energy, forces and stress under a particular
  functional/occupation/basis convention. Availability is explicit.
- A response solve accepts a defined reference state and perturbation; it returns
  response quantities in the corresponding spaces.
- A propagator advances coupled state over a specified interval according to its
  own integrator and feedback rules.
- A force provider supplies the requested observables and its session behavior;
  a provider lacking stress cannot be substituted into a cell-evolution method
  that requires it.

Avoid one universal `step(state) -> state` interface: it would conceal the
meaning of a step, coupled evaluations and observable availability. Nor should
all methods pretend to be energy minimizers. Shared operation signatures can
express applying a linear operator to a block of vectors without an inheritance
hierarchy or an object-oriented framework.

A driver returns an outcome appropriate to its procedure: electronic stopping
criterion met, ionic convergence met, requested time interval completed,
iteration budget exhausted, controlled interruption or method failure. It also
returns diagnostics and any meaningful partial result. The application preserves
those distinctions and maps them to process behavior. An outcome enum does not
certify the chosen physical model or identify a globally preferred state.

### Example: cell relaxation

1. The relaxation driver constructs the selected electronic problem for its
   initial cell and basis policy.
2. Electronic evaluation and derivatives produce a result for that configuration.
3. The optimizer determines a trial geometry and retains the state its algorithm
   needs for accept/reject decisions.
4. A geometry/representation update reconstructs affected objects and applies
   the specifically selected orbital/density transfer, if any.
5. The optimizer accepts or rejects according to its method. A rejected trial's
   mutable history is not silently committed to the accepted state.
6. Completion includes any final electronic/basis evaluation specified by the
   method. Only then does the driver report its final quantities.

The driver may explicitly support an inexact electronic procedure. That choice
includes its derivative/error treatment. The app must not turn electronic
nonconvergence into “good enough for forces” on its own.

### Example: nuclear dynamics with an external force provider

The integrator owns momenta, substep position, thermostat/barostat variables,
constraints and random state. It requests force evaluations at its specified
stages. A force session owns electronic guesses/history where continuation is
intended. Independent replicas have distinct sessions unless the method explicitly
shares state. The coherent checkpoint boundary may be a whole step or a defined
substep with its stage marker; the integrator defines the saved state.

### Example: response, spectra and postprocessing

A postprocessing calculation opens a selected prior result and constructs the
reference it actually requires. Fixed-density bands, a response solve, GW and BSE
have different prerequisites. The requested spectrum/eigenpairs and physical
approximations remain explicit. Missing orbitals, augmentation data or occupied
subspaces are reported before proceeding; they cannot be replaced by a plausible
file of scalar energies.

## 4. Changes, caches and history

Each family identifies its actual dependency changes in code. Common operations
include `at_geometry`, `change_basis`, `redistribute`, `initialize_from` and
`resume`; these are descriptions of distinct operations, not a mandated generic
trait hierarchy.

| Change | Core responsibility | Scientific responsibility |
| --- | --- | --- |
| Atom displacement | Exclusive replacement; retire dependent views | Projectors, neighbor maps, extrapolation and symmetry policy |
| Cell or basis change | Rebuild dependent storage/plans; preserve old state during transfer | Basis membership, projection, normalization, stress convention |
| Rank/device layout | Allocate/redistribute without losing logical indexing | Identify any order-sensitive history/reduction implications |
| Functional/data/spin model | Construct a new problem explicitly | Determine meaningful initialization transformations |
| Algorithm controls/history | Pass an explicit request to the method | Define whether adaptation or reset changes the procedure |

A cached projector block belongs to a particular geometry/basis/data combination.
It is not a free-floating buffer with a “valid” bit maintained by the app. Prefer
construction scope, immutable parents and narrow update operations. Reuse workspace
allocations separately from cached numerical values. The backend may cache a plan
keyed by shape/layout/context because those are its actual dependencies.

Physical hysteresis, electronic branch preparation and numerical history may
interact. The core makes no universal classification that authorizes deletion.
Even a quantity called a cache can affect finite-precision continuation if its
recomputation differs. A method's checkpoint/reset study must decide whether
reconstruction meets the particular continuation claim.

Trial rollback also includes random streams, adaptive controls and external
state when the selected algorithm requires it. If an external provider cannot
restore or stage such state, the driver must use a scientifically justified
alternative or reject that requested composition. Copying coordinates back is
not a general rollback implementation.

## 5. Scientific routine families

This table outlines boundaries only. Each row links to its required focused
expedition under beads epic `exv-8lk`; it does not prescribe 15 crates.

| Family | Main responsibility | Critical boundary into the core |
| --- | --- | --- |
| 1. Numerics | Linear algebra, transforms, integration, roots, interpolation and random primitives | Shapes/layout, numerical modes, workspace, failure/completion |
| 2. Representations | Geometry, symmetry, reciprocal/spin spaces and transformations | Stable logical indexing; explicit frame/basis changes |
| 3. Atomic/PAW | Radial data, projectors, overlap and reconstruction | Data/model compatibility; complete persisted ingredients |
| 4. Electrostatics | Boundary kernels, charges, fields and corrections | Selected boundary model; coupled energy/derivative meaning |
| 5. XC/spin/orbital terms | Functionals, potentials and derivatives, constraints and orbital corrections | Supported arguments/derivatives and spin conventions |
| 6. Nonlocal terms | Exchange and dispersion | Nonlocal state, approximation and rebuild rules |
| 7. Stationary electrons | Occupations, eigensolvers, SCF and minimization | Iteration history, initialization and method outcomes |
| 8. Derivatives | Forces, stress and consistent response derivatives | Evaluated configuration and electronic approximation |
| 9. Motion/sampling/paths | Optimizers, integration, statistical sampling and path methods | Trial state, substeps, measures and continuation |
| 10. Response/spectroscopy | Perturbations, fields, optical/magnetic/core observables | Reference state and perturbation-specific spaces |
| 11. Vibrations/transport | Force constants, electron–phonon coupling and transport | Mesh/broadening/long-range conventions and limiting procedures |
| 12. Localized/embedding | Subspaces, interpolation, embedding and populations | Gauge/window/rank definitions and external exchange |
| 13. Correlated/excited states | Screening, correlation energies, self-energies and excitations | Frequency grids, roots and requested spectral quantities |
| 14. Electronic evolution | Coherent/coupled electronic propagation | Physical memory, time ordering and feedback stages |
| 15. Learned models | Environments, fitting, predictions and acquisition | Model/data terms, uncertainty meaning and learning history |

Shared numerical operations can be reused without conflating their physical
objects. Coupling two families requires a defined scientific procedure and
meaningful interaction tests. Adding a new method means adding its construction,
state/outcome, output/restart adapters and tests together; it does not require a
new central scientific policy table.
