# INERTIA

## Exvasperated: current project direction

Established with the user on 2026-09-24. This section governs this project.
The Forge notes below were supplied as background on working preferences;
their product decisions, implementation claims, milestones, links and prior
approvals belong to another project.

### Mission and scope

Study VASP deeply and independently design, implement and release an open-source
replacement that researchers can adopt with the least possible disruption and
without losing capabilities they depend on. Full VASP capability coverage, and
potential improvements beyond it, is the ambition. Ground-state DFT is a possible
starting calculation, not a boundary on the design or eventual product.

Understand parity before choosing architecture, implementation order or detailed
performance tradeoffs. Parity includes scientific methods, combinations of
features, numerical behavior, file and program interfaces, continuation of jobs,
downstream tools, operational behavior and supported computing environments.
Define versioned reference behavior; the locally available version is a research
anchor, not a permanent ceiling. Develop real scientific workloads across the
whole capability surface. A count of tags or passing examples is not coverage.

The intended engineering standard combines scientific depth, careful numerical
work, strong systems engineering and practical adoption. Make concrete tradeoffs
after understanding the reference and researchers' workflows.

The user requires an eventual analysis of every file recursively under VASP's
`src/`, including supporting libraries, tests, generated material and build files.
On 2026-09-24 they clarified the immediate scope: finish an overall orientation
that partitions the entire tree and proposes a sensible order for deep study.
Do not try to understand everything in one pass. The
[source partition and study order](docs/research/vasp-source-partition.md) is this
orientation's deliverable. An inventory entry is not a completed file analysis.
Keep later reviews bounded, follow interactions across partitions, and distinguish
unread, partially examined and deeply analyzed material. The partition is revisable
and does not prescribe our replacement's component boundaries.

### Scientific routines and composition

On 2026-09-25 the user clarified the boundary: prioritize deep scientific and
numerical correctness of calculation routines, including resilience to subtle
errors and faithful behavior when composed. Choosing and composing calculations
is part of the researcher's skill in using the program. Preserve their control
over methods, parameters and sequences of calculations.

Experiment parsing, interpretation of experimental intent and suggestions are
separate potential capabilities. Ordinary input parsing and compatibility remain
part of the execution interface and must faithfully express explicit choices.

Encode established scientific relationships in representations, constructors,
ownership and permitted operations. Avoid an additional accounting apparatus for
policing meaning. Treat hysteresis, physical path dependence, numerical history
and their interactions as substantive scientific questions. Justify assumptions
about equivalent states, reconstruction and discarded history before encoding
them. An expected outcome or a cleaner abstraction does not establish scientific
validity. Test routines and their specified interactions with independent checks
that can expose subtle errors.

On 2026-09-25, while discussing an append-only calculation log, the user accepted
the narrower persistence commitment: selecting a recorded point recovers the
state actually recorded there, including its retained history. Continuing from
that point can append a new branch while preserving the existing history.
Computational restoration does not establish physical reversibility or undo a
thermodynamic process. Deterministic numerical replay is not an established
project goal or a premise of this storage design. Whether the recorded state is
sufficient for a particular continuation remains a method-specific scientific
question. Recording cadence, payload layout and retention still require design.

### Order of operations

The reviewed first pass through all 20 source-study areas was completed on
2026-09-24, with one independent subagent review at depth one per report and
warranted corrections incorporated. It left the broader every-file analysis open.

On 2026-09-25 the user requested an outline of the core program and scientific
routine buckets to guide the next literature and reference expedition. The
[working outline](docs/research/core-program-outline.md) defines that research
scope from the studies and the composition boundary above. It is a provisional
division of responsibilities; detailed architecture and implementation remain
subsequent work. The user then authorized the broad literature and reference
acquisition expedition, recorded in the
[campaign reports](docs/research/reference-campaign/README.md).

The user further clarified on 2026-09-25: this broad pass can inform the overall
design, but **each individual subsystem requires a focused, deep expedition and
scientific re-grounding before its detailed design and implementation**. Revisit
the equations and their assumptions, corrections to the literature, numerical
methods, reference implementations, interactions and difficult cases for the
specific subsystem being undertaken. Acquiring references or mentioning a
subsystem in the broad survey does not discharge this work. Re-grounding remains
iterative: related studies and experiments may expose reasons to return.

The user subsequently requested actually reading and studying the acquired
resources, then drafting an overarching Exvasperated design with a thoroughly
considered application core and less detailed computational routine families.
The [focused core reading](docs/research/core-design-study.md) and
[design draft](docs/design/README.md) deliver that pass. The architecture and
operating protocols are proposals for review; no engine implementation or backend
selection follows automatically. The focused scientific expeditions remain
required before detailed subsystem design and implementation.

On 2026-09-24 the user established the following project sequence after the
orientation. The source-study order organizes the first stage of this sequence.

1. **Deep VASP studies and detailed reports.** Work through the source partitions
   in bounded passes, eventually analyzing every file. Bring back detailed
   reports explaining the science, implementation behavior, interactions,
   assumptions, limitations and unresolved questions. Report findings at the
   end of useful passes, including partial studies, so they can inform subsequent
   work and identify what to revisit.
2. **Synthesize parity and improvement opportunities.** Use the reports to
   establish what researchers need from a replacement and where we see ways to
   improve it. Develop the capability and workflow picture across partitions,
   including CPU/NVIDIA alpha execution and the later AMD objective. Keep proposed
   improvements distinguishable from established findings and evaluate their tradeoffs.
3. **Conduct the major research and reference campaign.** Let that synthesis
   determine the questions and breadth of an extensive investigation of primary
   literature, independent implementations, numerical methods, scientific data,
   benchmarks and execution approaches. Acquire and assess references with
   provenance and license terms; develop comparisons and bounded experiments
   that resolve the identified questions. Bring back a scientific and engineering
   synthesis that can support design choices.
4. **Design the system.** Develop the extensive architecture and scientific
   design from the parity requirements, improvement ideas and research findings.
   Resolve component responsibilities, representations, numerical choices,
   interfaces, failure behavior and CPU/NVIDIA execution, with AMD as a second wave.
5. **Specify and plan.** Make the design precise through equations, domain
   representations, permitted operations and suitable quasi-formal specifications.
   Derive a concrete implementation sequence with scientific acceptance criteria
   and paired implementation/tests.
6. **Execute.** Implement, test and validate against those specifications and
   criteria, then release. Correctness work advances with each capability.

Focused reference lookups can clarify individual source claims during studies;
the broad acquisition campaign follows the reports and parity/improvement
synthesis. Bounded research experiments serve named questions. Findings may send
us back to an earlier question or revise a design; preserve that reasoning.
Product implementation follows the research, design, specification and planning
work. The source partition and VASP's own organization do not select our design.

The user explicitly expects iterative understanding across studies. Some areas
will become clear in one pass; others yield more when we establish most of the
picture, work on related areas, and return with the missing context. The user's
rough 80-85 percent example describes this judgment, not a measurable completion
target. A productive pass does not require closing every question in its area.

When moving on, report what is understood, what remains uncertain, which later
work may resolve it, and what should prompt a return. Record actionable follow-up
in beads and preserve the reasoning in the report. Choose the next study for
the understanding it can add. The overall sequence allows these revisits and
progress with explicit open questions; it does not require every study to be
exhausted before synthesis or the reference campaign. Claims depending on open
questions remain provisional. Eventual per-file analysis and the scientific
acceptance requirements still apply.

### Execution targets and backend evaluation

On 2026-09-25 the user revised the target sequence: **CPU and NVIDIA GPU execution
are required in v1-alpha; AMD GPU execution is a second-wave objective.** This
supersedes the 2026-09-24 requirement for all three targets in alpha, retained as
historical context in the first-pass reports. Prioritize CPU/NVIDIA capabilities
and record the implications of choices for later AMD support.

The alpha acceptance plan must identify the supported hardware and toolchains,
the scientific workloads covered on each target, and evidence of actual execution
on that hardware. Define scientific accuracy and comparisons across targets in
terms of the observables and numerical methods. Hardware generations, CPU
architectures, portability mechanisms and performance targets remain design
questions. This requirement selects execution targets, not a GPU programming
framework or numerical backend.

On 2026-09-25 the user proposed developing on Linux first and deriving macOS
support from that foundation. Adopt Linux as the primary development and
qualification direction, with macOS as a secondary port of the same core.
Keep platform-specific services localized and consider inexpensive macOS CPU
build checks early to expose portability assumptions. The Mac can remain an
editing client for Linux execution. This direction selects no distribution,
server, CPU architecture or deployment setup. Apple GPU support is a separate
backend question and is not implied by a macOS CPU port.

The user explicitly requests evaluating cuda-oxide as a candidate on its merits.
Assess its actual capabilities, numerical behavior, performance, compiler and
toolchain behavior, and integration using relevant scientific workloads. Its
"alpha" designation is neither a reason to favor it nor a reason to reject it.
Concrete limitations and engineering costs matter; a release label alone does
not settle them. NVIDIA-specific approaches remain candidates while AMD is
scheduled for the second wave. No backend has been selected.

### Quarantine and independent reconstruction

The user explicitly permits deep reading of VASP source and running VASP locally,
on their server or elsewhere available to the project. Reading implementation is
part of the research. Execution will support comparisons once our own functionality
exists; deliberately chosen reference experiments may also answer research questions.

The user forbids copying VASP code or proprietary implementation text into our
system. Write our implementation independently. Do not copy source, comments,
diagnostic prose or other protected strings into code, tests, documentation,
issues or release artifacts. Renaming or mechanically translating copied code
does not produce an independent implementation. Keep reference files and private
execution artifacts in quarantine. Do not adopt their test fixtures or datasets
merely because we can inspect or execute them.

Publicly documented interface names, parameter names and required format tokens
are explicitly allowed. Record the public documentation supporting a compatibility
contract. This permission concerns interoperability; it is not a direction to
copy entire manuals. Explain research findings in our own words, with source
locations and hashes where useful, without embedding proprietary excerpts.

VASP is an authorized comparison oracle. Agreement establishes agreement under
the recorded conditions; scientific correctness also needs independent reasoning
and evidence. Investigate disagreements, version differences and known reference
defects rather than treating every reference output as scientific truth.

### Working preferences carried into this project

Develop an extensive, quasi-formal design, using Quint or another suitable tool
where it resolves a concrete question, and derive an implementation plan from it.
Preserve assumptions, equations, alternatives, corrections and unresolved claims.
Research and bounded experiments inform that design; an experiment does not set
the architecture by accident or substitute for the overall design.

Correctness belongs in domain types, constructors, ownership, equations and
permitted operations. Tests must challenge the actual behavior and reject meaningful
errors. Do not introduce certification architecture, receipts or a generic evidence
layer as a substitute for understanding. Keep useful numerical diagnostics and
calculation details inspectable. Distinguish numerical error, uncertain inputs
and physical model limitations. Derive tolerances from the observable and claim.

The user emphatically reinforced this on 2026-09-25: no certification,
evidentiary, authority or ADR theater anywhere in the product or development
process. Do not introduce certificate/evidence objects, authority hierarchies,
approval rituals, ADR machinery or compliance-style scaffolding. Keep reasoning
in ordinary, revisable technical notes and correctness in equations, types,
representations, algorithms and tests. Preserve useful sources, assumptions,
counterexamples, measurements and failure diagnostics for doing the work;
documentation and tool output acquire no special authority. The scale of the
verification effort does not justify an administrative architecture around it.

The user defines **teeth tests** as the replacement for ADR prescriptions. For
anything an ADR would have said "thou shalt" or "thou shalt not", establish a
substantive check that can be demonstrated red, then make it green through
adherence. The mechanism may be a code test, compiler guard or another executable
check. Demonstrate failure for the relevant violation and success because the
implementation adheres; keep it capable of catching regression. A missing
document or unrelated build failure supplies no teeth. If meaningful
red cannot be demonstrated, the statement is at best a good intention. Preserve
useful reasoning in ordinary notes without treating prose as enforcement. This
is a working technique, not a new registry, reporting layer or approval ritual.

On 2026-09-25 the user requested plain, concrete design prose. Name the data,
operations and effects instead of leaning on labels such as “scientific state.”
Explain who stores, updates or releases something when discussing ownership.
Use technical terms where they add precision; avoid wording aimed at sounding
credible. This is a writing preference, not a new enforcement process.

### Engineering tenets established 2026-09-25

The user requires the following throughout this project:

1. Systems interact at interfaces only; never inspect another system's private
   state, implementation or storage as an integration mechanism. This permits
   in-process interfaces and resident-data ownership handoff.
2. Let the database perform work it handles better. Investigate its constraints,
   transactions and query operations before rebuilding them in application code.
   This principle does not itself select a database or settle numerical-array
   storage; those remain design questions.
3. No object-oriented programming, at all. Organize our implementation around
   algebraic data types, explicit data structures and operations.
4. No JVM or JVM things. A narrowly allowed exception is a needed verification
   program we lack time to reimplement, such as Apalache. Use an extremely
   lightweight container and programmatic teardown on completion, failure and
   interruption. This creates no JVM application/runtime dependency.
5. Depending on a human or model remembering something is inadequate engineering.
   Use structure and automation, tested against meaningful violations.
6. Never hot patch: study the system, analyze the problem, plan the fix, implement
   it through the testing/review cycle.
7. Automate triggers instead of setting reminders for the same work. The user's
   "test init" is an example of executable workflow intent, not a claim that a
   command by that name exists here.
8. Always work from a plan. Treat "easiest", "quickest done" and similar reasoning
   as signals to reconsider the approach. Revise plans as understanding changes.
9. For every implementation section/tranche: tests red with actual errors;
   code; tests green; adversarial tribunal code review; resolve findings within
   the bounded cycle in tenet 10. Reject tautological
   tests. Review targets the actual work and adds no certification bureaucracy.
10. NEVER undertake a second round of review, checking or equivalent work without
    explicit operator approval. The user gives this allowed sequence: code review
    -> fix all -> subagent validates -> fix stragglers -> NOW STOP. One validation
    after the first fixes is included; another check after fixing stragglers is
    not. Stop and report what remains, even if substantial; talk to the operator
    before continuing. Do not evade the cap with another agent, a renamed pass or
    a nominal new tranche. Automation must respect the same stopping point. The
    purpose is to prevent unbounded checking and certification hallucination.

This supersedes the earlier preference for merely periodic adversarial reviews.
These written instructions do not establish automated enforcement; that requires
demonstrated teeth. Ordinary technical notes remain revisable aids to reasoning.

The user clarified the reuse tenet during the design continuation: avoid
reimplementing strong existing infrastructure merely from habit, but do not
presume a database, storage arrangement or deployment environment yet. Numerical
libraries are all on trial before adoption. Existing packages, independently
written routines and generated/specialized kernels face the operation's scientific
specification, tests and performance requirements. We may implement some or all
numerics ourselves; library reputation does not decide the comparison.

### Stack and implementation preferences

The user clarified the core draft on 2026-09-25: layout needs a testing strategy
that exploits its logical-index mapping, including independent checks. Open
storage choices must not block callers built against a well-defined interface;
interim implementations can satisfy that interface for their supported use.
A short contract stating inputs, results, effects and completion/failure is welcome.
Distinguish physical time, solver progress, integrator stages and execution order,
and explain what positions and electronic values each calculation actually updates.

Preserve declared physics and explicit failures. Do not silently smooth, clip,
extrapolate, choose a root or change a physical model to make a calculation finish.
Verification, comparisons with independent implementations and physical validation
answer different questions. Tests advance with each implementation increment.

On 2026-09-25 the user explicitly reopened stack selection. Rust remains a
plausible choice, not a settled decision. Compare C, C++, Rust and OxCaml for the
whole program, with additional candidates justified on their merits. Go, JVM
languages and Zig are excluded by current user direction. Examine modern Fortran
and APL for calculation routines, and symbolic derivation, simplification and
specialization before numeric execution. Performance and scientific correctness
both constrain selection. Existing Rust-specific design sketches are conditional.
Evaluate outside libraries and larger components case by case, including scientific
suitability, measured behavior and license compatibility. Dependency code, code
generators and foreign interfaces remain part of what we must trust and assess.

The user prefers keeping scientific data in place and handing off ownership.
Their briefly used word "lease" was explicitly withdrawn: it does not authorize
a lease-management subsystem. Prefer moving owning handles through operations;
retain allocations through actual asynchronous completion. Introduce sharing,
borrowing or coordination only for a concrete requirement. Language boundaries
should not cause copies or repacking by default; necessary representation or
placement changes must be explicit and measured.

On 2026-09-25 the user further emphasized algebraic data types and structures,
memory layout as a first-class concern alongside logic flow, and restricting and
bounding resources and operations wherever justified. Their demoscene analogy
expresses a discipline of understanding the machine and avoiding waste even on
powerful hardware. "Not one byte/cycle wasted" is a spirit, not a literal local
optimization mandate. Ring buffers with cursors are an example, not a prescribed
architecture or a reason to over-index on that structure. No system determinism
promise is introduced. Controlled simulation is a testing technique and does not
change the scientific or persistence commitments above.

The user requested identifying a broad C++ rigor stack, including property tests,
state-space exploration, bounded verification, mutation testing and controlled
simulation in addition to compiler diagnostics and analysis. The
[candidate tooling map](docs/research/cpp-rigor-stack.md) records tools, limits and
proposed qualification cases. It does not select C++ or establish executed checks.

Generally keep an effort to two passes before discussing a larger unresolved
redesign. Each implementation tranche follows the red/code/green/adversarial-review
cycle above. No local mutation campaigns; cloud mutation testing requires
explicit user intent. Keep downloaded programs inert until deliberately selecting
a bounded execution. VASP execution itself has already been authorized.

The user delegates selection of a permissive license that supports adoption.
Apache-2.0 is the selected project license; third-party material retains its own
terms. This license does not cover quarantined VASP material. The
[initial parity reconnaissance](docs/research/vasp-parity-orientation.md) records
the present, limited state of understanding. Use beads for work tracking.

## Imported Forge background

The remainder is preserved from the supplied INERTIA.md. References and statements
of current implementation below describe Forge, not Exvasperated.

Working sketch, 2026-09-20. Forge starts with industrial furnace modeling and is
expected to seed or participate in a constellation that becomes a substantial
in-house physics and chemical kinetics engine. Rust is at the core. How that
constellation divides into libraries, applications and repositories is open.
The first furnace family, intended decision, accuracy target, and deployment
setting also remain open; they do not bound the long-term engine ambition.

The user has selected a concrete thermal focus: refractory and shell temperature
histories through a ramp and cooldown, exemplified by firebrick, Kaowool and a
304 stainless shell. The [layered-wall proposal](docs/design/layered-wall.md)
defines through-thickness and interface observables. Product grades, dimensions,
contacts and operating conditions remain explicit inputs, not assumed values.

Future visualizations must keep calculation details, error evidence and statistical
meaning within easy reach. Preserve observable identity, calculation lineage and
scoped evidence in results from the process stage onward; plots and exports should
consume that information directly. Unknown uncertainty is not zero, and numerical
error, input uncertainty and model adequacy remain distinct. See the
[result-evidence proposal](docs/design/result-evidence.md).

## Work gives the structure its shape

Develop an extensive design before implementing the engine. Use research and
inspectable experiments to resolve design questions. Keep reasoning that would
otherwise need rediscovering, including assumptions, alternatives, and corrections.
These practices are adapted from `../gageblock/`, not its product assumptions.
The first acquisition wave is material for the design. Its proposed thermal
experiment is one possible probe, not an incremental implementation roadmap.
The current [overall design v1](docs/design/engine-v1.md),
[worked assemblies](docs/design/composition-cases.md),
[system contracts](docs/design/system-contracts.md) and
[derived plan](docs/design/implementation-plan-v1.md) consolidate v0 and subsequent
evidence. The user endorsed that direction and asked to proceed. The
[foundation decisions](docs/design/foundation-decisions.md) record the working
baseline and [I1a packet](docs/design/foundation-packet.md) defines the first bounded
implementation: semantic layouts and checked reordering. Further model, backend
and application capabilities retain their specific design/data/evidence gates.
After E2-B the user explicitly corrected the priority: bring back the overall
system design for convergence, rather than making another experiment the default
next move. Targeted experiments answer named choices or dependent claims; they
must not indefinitely defer the design and plan that gate engine implementation.

The [I1a implementation](crates/model/src/lib.rs) now provides semantic scalar
slots, immutable layouts, finite bound arrays and checked lossless reordering.
Its [evidence](docs/verification/foundation-i1a/README.md) establishes structural
binding/rejection behavior, not truth of source declarations or physical state
admissibility. No solver, property evaluation or importer is implemented by I1a.

## Design becomes a plan

The user requires an extensive design developed in a quasi-formal way, with
Quint or a suitable alternative, and then developed into a concrete implementation
plan. Engine/product implementation follows that work. An outline, a passing
experiment, or a specification file by itself does not satisfy this requirement.

The design must address the physics/chemistry model, state and property semantics,
kinetic mechanisms, numerical methods, composition and coupling, data provenance,
failure behavior, validation, performance, and the boundaries between components.
Specify which claims are mathematical, abstractly model-checked, experimentally
supported, or still unresolved. Map the eventual implementation plan back to
those claims and their acceptance evidence. The current
[design brief](docs/design/README.md) defines this work; it is not the design itself.

Experiments may include small disposable implementations or reference runs when
they answer an explicit design question. Their results can change the design;
their interfaces and dependency choices do not become the architecture by default.
Broad design scope and bounded experiments are compatible. Keep chemistry and
kinetics in the design from the start, alongside transport and thermal physics.

On 2026-09-22 the user requested a literature/reference reset to avoid gradually
reimplementing a general computer algebra system. Own the physical meaning and
model composition while evaluating established numerical machinery for reuse.
Precision, differentiation and symbolic tools serve concrete scientific questions;
they are not automatically new in-house subsystems. See the
[reference review](docs/research/numerical-grounding.md) and proposed
[ownership refinement](docs/design/numerical-ownership.md).

The subsequent [E2-A experiment](docs/verification/e2-thermal/README.md) couples
the existing reacting gas to a prescribed finite-capacity load. It demonstrates
that conservative transfer and a converged coupling residual can still mispredict
the heating history. The proposed [coupling refinement](docs/design/thermal-coupling.md)
keeps physical validity, bookkeeping, discrete convergence and consumer accuracy
as separate obligations. It reuses existing numerical tools and leaves the
broader spatial/radiation/storage design and implementation gate intact.

The subsequent [E2-B wall experiment](docs/verification/e2-wall/README.md) exercises
layered spatial storage and contacts against primary equations, exact controls
and the author's reference implementation. It rejects wrong conductivity/capacity
and state reset at cooldown, and preserves delayed sampled interface maxima.
Temporal error obscured spatial order and dense reference sampling timed out;
neither a closed energy ledger nor successful reference execution establishes
consumer accuracy. Actual materials/exposure and those numerical claims remain
open independently of the agreed foundation implementation.

## Modeling claims need their own evidence

Separate governing equations, constitutive correlations, numerical methods,
boundary conditions, parameter fitting, and experimental validation. State units,
sign conventions, reference enthalpies, applicability ranges, and material states.
An energy balance that closes is necessary but cannot establish physical accuracy.
Agreement with a second solver may reproduce shared assumptions and shared errors.

Distinguish numerical verification from validation against furnace measurements.
Useful checks include conservation, analytic limiting cases, mesh/time refinement,
independent implementations, and held-out operating histories with measurement
uncertainty. Scientific acceptance criteria must trace to primary literature,
including any explicitly derived specialization. Solver settings do not constitute accuracy
criteria. Choose tolerances from the claim. Demonstrate meaningful rejection
before accepting an oracle; do not pad an empty solver with passing toy tests.

Preserve the declared physics even when it is inconvenient numerically. The user
prefers a represented discontinuity or an explicit undefined-state failure to
arbitrary smoothing, clipping, extrapolation, root selection or fallback physics.
A source-defined one-sided value and an undefined derivative are distinct results.
Numerical tolerances are algorithm controls, not permission to invent a constitutive
law or repair conservation silently. A model revision needs scientific justification
and a distinct identity; no such repair is authorized merely to make a solver run.

The following is firm design guidance, not a property of the whole system that
we claim to verify. Concrete behavior needs its own meaningful failing test.
The user forbids certification architecture, including the proposed next step of
scientific-package resolution and pervasive evidence declarations. Correctness must be
encoded structurally through domain types, constructors, ownership, equations and
permitted operations, never through receipts or evidence objects. Tests challenge
that structure; attached metadata cannot make an invalid value or operation valid.
Ambiguity calls for scientific understanding and justified model choices, with
undefined results preserved where appropriate. Do not substitute an administrative
metadata layer for that work or reintroduce it under a different name. Useful
calculation details, numerical diagnostics and statistical meaning still serve
the previously requested result inspection; they do not mandate a generic evidence
system. The package/evidence-schema-first recommendation is withdrawn; see the
[correction](docs/journal/2026-09-22-no-certification.md).

The user explicitly rejects unsupported claims and procedural theater. Use derivations, experiments and
formal tools when they answer a concrete question or expose a meaningful error;
report what they establish and what they do not. A certificate, checklist,
passing test count or authoritative citation cannot substitute for understanding
the model and observing the behavior being claimed.

## Iteration preference

The user asks for generally no more than two passes in an effort without prior
discussion. Complete the currently authorized state-machine follow-on, then
backburner that topic. Designs remain revisable: recorded execution baselines
identify evidence and do not freeze future choices.

On 2026-09-24 the user clarified that independent adversarial reviews should be
periodic rather than attached to every capability: fix, check, fix, stop. Treat
that as working guidance, not a system property or certification step. One
initial independent review and one bounded recheck may drive corrections; larger
unresolved redesigns return for discussion rather than another automatic wave.

Testing must advance with the system: each implementation increment includes its
meaningful tests and runnable trigger. The user explicitly rejects large catch-up
testing efforts. The [thermal kernel design](docs/design/thermal-kernel.md) and
[paired implementation/test sequence](docs/design/thermal-kernel-plan.md) are the
current authorized design work following withdrawal of the I1b proposal.

## Engineering

Safe Rust and minimal FFI are the defaults. A foreign-language reference can be
an offline comparison without becoming a production dependency. Choose numerical
libraries by a concrete problem and measured behavior, not by name recognition.
Unsafe dependencies and FFI remain within the trust boundary.

Automate useful checks: pinned compiler and tools, shared lints, a local commit
gate, an explicit watcher, and CI configuration. State which triggers actually ran.
No local mutation campaigns; cloud mutation testing requires explicit user intent.
Keep acquired programs inert until a bounded reproduction is deliberately chosen.

## Research bench

`papers/` holds local literature; `quarantine/` holds local reference source.
Both are ignored by Git. Version the source catalog, hashes, revision IDs,
inspection notes, failures, and synthesis. References remain subject to their own
licenses; no project license has been selected and no reference code is adopted
merely by downloading it.

The initial acquisition covers process energy balances, radiation in participating
gases and enclosures, load/refractory transients, combustion and properties,
numerical solvers, and validation. It is weighted toward thermal/furnace modeling
and is not yet an adequate research base for the intended general engine.
Thermodynamics, finite-rate chemical kinetics, reacting/multiphase transport,
mechanism and property databases, coupling methods, and specification practice
need substantial design-oriented research. Reheating and heat treatment remain
initial examples, not a user-selected product boundary.

## Current execution milestone

The runnable wall, finite-capacity heat delivery and affine temperature-dependent
wall storage and conductivity are implemented. The [conduction specialization](docs/design/affine-conduction-execution.md)
adds nonlinear IDAS initialization and transport diagnostics. The [storage specialization](docs/design/affine-storage-execution.md)
records the latest equations, plan and numerical limits. The [coupled execution specialization](docs/design/coupled-wall-execution.md)
records the source/wall equations and concrete plan; the [scenario guide](scenarios/README.md)
provides the user commands. The source has evolving stored energy and explicit
external power, with one shared transfer to the wall and ordinary inspectable
calculation output. Wall capacity and conductivity may be affine in temperature;
attached-body capacities remain explicitly constant. Synthetic examples do
not supply real refractory properties or gas chemistry. Design, implementation
and testing continue together inside each capability delivery; they are not
separate journey nodes.

The user requested the next detour be design and implementation of a rich,
physically grounded localhost visualization alpha for following these calculations.

That visualization detour is implemented as a local result viewer in
`apps/thermal-viewer`, launched with `scripts/forge-view`. The [viewer design](docs/design/visualization-alpha.md)
and [guide](apps/thermal-viewer/README.md) record the actual supported views and
limits. It consumes Rust output without introducing another solver or a generic
evidence layer. UI changes run `npm run check --prefix apps/thermal-viewer`
alongside the existing Rust gate; browser tests target the production build.
The next bounded increment adds [two-run comparison](docs/design/run-comparison.md):
identical geometry/mesh and exact saved time/side mapping, profile overlays,
selected-location differences and changed inputs. Missing matches remain absent;
differences make no numerical-accuracy or statistical claim.

The [radiative-boundary execution](docs/design/radiative-boundary.md) adds opaque
gray surface exchange with prescribed black surroundings and supplied emissivity.
The actual material surface is solved with half-cell conduction; it is not pinned
to the environment temperature. The runnable example and comparison are available
in the viewer. This is a bounded exterior model, not participating-gas radiation,
a finite enclosure or a real 304 emissivity assignment.

The [combined exterior](docs/design/combined-exterior.md) now adds simultaneous
convection and radiation at that same solved surface, with independent air and
black-surroundings schedules. Component powers, their sum and solved total remain
inspectable. The extended synthetic example runs through 240 s and exposes
delayed sampled interface maxima followed by cooling. Its supplied h and material
properties are not empirical furnace inputs. The subsequent capability is the
finite furnace thermal assembly design described in the milestone discussion.
