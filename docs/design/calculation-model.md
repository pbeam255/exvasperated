# Calculation model and composition

Part of [design draft 0.2](README.md). This describes how to prepare a calculation,
what data it keeps, and how its routines work together. The routines themselves
remain outlines. See the sources in the [reading study](../research/core-design-study.md).

## 1. From a request to a running calculation

Use a staged construction sequence with explicit outputs:

| Stage | Produces | Checks and effects |
| --- | --- | --- |
| Parse | Parsed input with source locations | Grammar, primitive values, duplicate/unknown input handling under the chosen dialect; no calculation is run |
| Resolve | Explicit calculation specification | File references, documented defaults/precedence, method variants and requested products; report effective values |
| Construct the problem | Model and initial representation descriptions | Species/data matching, geometry, units, selected boundary/spin/occupation choices; structural consistency |
| Plan execution | Distribution, placement, buffers and operations | Required kernel/library support, rank/device topology, shapes and estimated memory |
| Prepare | Driver with its working arrays, history and resources | Allocate, load/convert selected initial state, build operators/plans; numerical setup may occur here |
| Execute | Results from a defined calculation stage, and a reason for stopping | Run the selected procedure; stop and expose output at supported stages |

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

These are proposed data structures, not final APIs or classes. Use algebraic data
types and explicit operations. Callers use the public interfaces described in
[core structure](core-structure.md). Here “family” means a group of related
routines, such as electronic solvers or nuclear integrators.

| Data | Meaning and owner |
| --- | --- |
| `CalculationSpec` | Immutable resolved physical choices, procedure, numerical controls, initialization and requested products; owned by the application |
| `AtomicDataSet` | Immutable imported atomic ingredients with functional/relativistic/generator information and units; shared when genuinely identical |
| `GeometryFrame` | Cell, ordered atoms, positions and prescribed constraints at one configuration; driver controls replacement |
| `PhysicalModel` | Selected equations/terms, external conditions and spin/boundary choices; changing it is an explicit new model construction |
| Family representation | Basis, reciprocal sample set, real/radial grids, projector/overlap spaces and normalization conventions appropriate to that family |
| Family state | Orbitals/densities/occupations, trajectories, fields, response vectors or learned state; kept and updated by its driver or child session |
| Family history | Mixer, propagator, thermostat, optimizer, bias, acquisition or branch history; kept and updated by the routine that uses it |
| `ExecutionContext` | Rank group, CPU workers, device contexts, library handles, placement and memory pools |
| Family result | Quantities actually evaluated at a specified calculation stage and the method outcome; immutable to consumers |
| Recorded family state | Immutable decoded values/history from a selected archive entry; the method constructs a continuation session from it where supported |

A constructed problem pairs the model with a specific geometry and representation.
The driver supplies updated geometries or fields through explicit operations.
Routines may share unchanged data and reuse large allocations, but callers cannot
alter their inputs behind their backs. Positions are not mutable globals merely
because many routines need them.

Use compile-time distinctions where the number of cases is stable and small:
real/complex scalars, coordinate conventions, host/device access, input versus
mutable output views. Runtime sizes, cells and basis identities still need
checked construction. Two arrays with equal dimensions are not necessarily in
the same basis. Where lifetimes cannot express that relationship, operation entry
compares a representation identifier and dimensions. This catches mismatched
arrays; it does not establish that the calculation is accurate.

Atomic units are the proposed internal convention for electronic calculations;
external adapters convert explicitly. Named quantities and array views specify
energy/length/time/charge, coordinate and stress conventions. Inner numerical
loops operate on scalars after those boundaries. No generic symbolic units engine
is required. Stress sign, Voigt ordering and cell-vector orientation require one
documented internal convention and explicit adapters; settle exact conventions
with the geometry/derivative expedition before implementation.

## 3. How drivers call routines

A method driver is ordinary code: loops and calls to routines. It receives an
execution context, working data, output callbacks with bounded buffering, and
stop requests. The application selects a driver and calls it. A driver may keep
a child session between calls when later calls need that child's history.

Each method defines what must be saved alongside the code that uses it. At a
supported stage, a snapshot operation exposes named arrays and values that stay
unchanged while they are written. Restoration decodes them. Preparing to continue
recreates execution resources and any derived quantities the method permits us
to rebuild. The archive does not rerun earlier iterations to recover saved values.
The [history design](calculation-history.md) defines the application operations.

Examples of interfaces to design during each subsystem study:

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
returns diagnostics and any useful partial result. The application preserves
those distinctions in its summary and exit behavior. Meeting a stopping rule does
not establish that the physical model is appropriate or that a preferred state
has been found.

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

The integrator keeps and updates momenta, positions within a step,
thermostat/barostat variables, constraints and random-generator state. It requests
forces at specified stages. The force session retains electronic guesses and
history where later evaluations should use them. Independent replicas use separate
sessions unless the method explicitly shares data. A checkpoint may capture a
whole step or a defined substep; it includes the stage marker and the matching
values the integrator needs to continue.

### Example: response, spectra and postprocessing

A postprocessing calculation opens a selected prior result and constructs the
reference it actually requires. Fixed-density bands, a response solve, GW and BSE
have different prerequisites. The requested spectrum/eigenpairs and physical
approximations remain explicit. Missing orbitals, augmentation data or occupied
subspaces are reported before proceeding; they cannot be replaced by a plausible
file of scalar energies.

## 4. Changes, caches and history

Each group of routines defines operations for changes that affect its data.
Examples include `at_geometry`, `change_basis`, `redistribute`, `initialize_from` and
`resume`; these are descriptions of distinct operations, not a required
trait hierarchy.

| Change | Core responsibility | What the calculation routines must decide |
| --- | --- | --- |
| Atom displacement | Exclusive replacement; retire dependent views | Projectors, neighbor maps, extrapolation and symmetry policy |
| Cell or basis change | Rebuild dependent storage/plans; preserve old state during transfer | Basis membership, projection, normalization, stress convention |
| Rank/device layout | Allocate/redistribute without losing logical indexing | Identify any order-sensitive history/reduction implications |
| Functional/data/spin model | Construct a new problem explicitly | Determine meaningful initialization transformations |
| Algorithm controls/history | Pass an explicit request to the method | Define whether adaptation or reset changes the procedure |

A cached projector block belongs to a particular geometry/basis/data combination.
It should be stored with that association. Construct it from immutable inputs and
replace it through specific update operations, instead of asking the app to
maintain a “valid” bit. Reuse workspace allocations separately from cached
numerical values. The backend may cache a plan
keyed by shape/layout/context because those are its actual dependencies.

Physical hysteresis, electronic branch preparation and numerical history may
interact. The core makes no universal classification that authorizes deletion.
Even a quantity called a cache can affect finite-precision continuation if its
recomputation differs. A method's checkpoint/reset study must decide whether
reconstruction meets the particular continuation claim.

Trial rollback also includes random streams, adaptive controls and external
state when the selected algorithm requires it. If an external provider cannot
restore or stage that data, the driver needs an alternative whose effect on the
method is understood and justified, or it must reject the requested combination.
Copying coordinates back is not a general rollback implementation.

## 5. Groups of calculation routines

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

Different calculations may reuse a numerical operation while interpreting its
inputs differently. Specify how two methods interact and test them together.
Adding a method includes its setup, working data, outcomes, output/restart
adapters and tests. These belong with the method, without a central policy table.
