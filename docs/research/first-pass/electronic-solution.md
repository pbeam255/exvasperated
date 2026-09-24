# Electronic solution, occupations and mixing: first pass

Studied 2026-09-24 against quarantined VASP 6.5.1. The `electronic_solution`
partition contains 26 files and 25,557 lines. This pass connects selected
outer loops, band solvers, occupation integration and density mixing. It also
returns to `rot.F`, assigned to geometry but used for electronic optimization.
No executable was built or run. Source identity is recorded in the
[inventory](../vasp-source-inventory.csv).

## Reading scope

Declaration/procedure maps were inspected for all assigned files. Body reading
and its limits are recorded below; unlisted bodies remain open.

| Files | Body scope |
| --- | --- |
| `electron.F` | Call/condition scan throughout; bodies 414–451, 485–596, 623–655, 713–719, 777–850. Full initialization and finalization remain partial. |
| `electron_common.F` | Entire 127-line file, including convergence, iteration limits and external stop handling. |
| `electron_all.F` | 438–473, 600–661 and selected call searches: direct optimization and distinct termination. |
| `electron_OEP.F`, `electron_lhf.F` | 597–689 and 433–480 respectively, with call searches: response-based potential optimization and local-exchange assembly. Full equations remain open. |
| `davidson.F` | 494–620, 741–780 and stopping/call searches. |
| `david_full.F` | 208–282, 565–592, 1030–1110, 1250–1330, 2145–2250 plus residual/solver searches. Full restart and preconditioner algebra remain open. |
| `david_inner.F` | 650–740 and operator/stop searches: selected interior-state ordering and failure recovery. |
| `rmm-diis.F` | 337–380, 463–523, 660–717 and stopping searches. |
| `steep.F` | 225–280 and stopping searches. Detailed line minimization remains unread. |
| `subrot.F` | 600–763, 1917–1972: selected diagonalization dispatch and approximate rotation helper. |
| `subrot_cluster.F` | 76–164: energy/occupation-dependent cluster construction. |
| `subrot_scf.F` | Call/condition map and 430–465: a separate inner self-consistency loop. |
| `mix.F`, `broyden.inc` | 23–191 and entire short include: simple mixing and persistent storage. |
| `broyden.F` | 100–238, 335–421, 465–513, 554–670, 1210–1292: state packing, history, reset and preconditioning. Full matrix update remains unread. |
| `diis.F` | 69–145, 166–267: history, constrained solve and caller-facing step. |
| `dos.F` | 97–153, 637–730, 747–845: selected occupation/DOS dispatch; elementary integration remains partial. |
| `fermi_energy.F` | 139–274, 285–337, 412–509: midpoint/bisection path, distributed counting and smearing kernel. Legacy root search remains unread. |
| `tet.F` | 406–455, 505–537: tetrahedron weight assembly, degeneracy correction and normalization. Most formulas remain unread. |
| `bandgap_struct.F`, `bandgap_tools.F` | Entire record file; tools 37–80, 221–279: sorting and classification paths. |
| `elf.F` | 245–298: final localization-function expression; density preparation remains unread. |
| `pardens.F`, `stm.F` | 37–98, 155–205 and 40–128 respectively: interfaces, selection/output branches and an explicit parallel restriction. Scientific reconstruction bodies remain largely unread. |
| `ini.F` | Procedure map and 358–429: spline helper shared with XC. Timing/allocation and other numerical helpers remain partial. |

Cross-partition body reading: `rot.F` 269–323, 1180–1258, 1283–1375,
plus call searches; `rhfatm.F` call-site searches located users of `diis.F`.
These are bounded returns, not completed deep analyses of those files.

## The outer iteration is a coupled state transition

The principal driver can rebuild local and PAW potentials, update a functional's
auxiliary state, select a band solver, orthogonalize or rotate states, recalculate
occupations, form an energy, then rebuild and mix charge. Delay settings and
validity flags suppress or reorder parts of this sequence (`electron.F` call
map and cited body ranges). The electronic state includes smooth density,
on-site occupations, kinetic density when used, potentials, orbitals,
eigenvalues and mixing history.

The selected band-solver dispatch covers full diagonalization, residual
minimization, blocked Davidson, interior-state Davidson, an unblocked/full
Davidson variant and older bandwise steps. A combined Davidson/residual mode
uses Davidson during a delay interval. Compatibility settings change whether
the residual solver receives a historical stopping estimate (`electron.F`
414–596). A solver name is insufficient to reconstruct its actual schedule.

Exact exchange adds another state dependency. The sampled main loop constructs
an adaptively compressed exchange operator for selected solvers under a build
guard. The full Davidson entry rejects active exact exchange without that
compression (`david_full.F` 208–215). These are specific implementation
combination constraints, not mathematical limitations of Davidson itself.

## Generalized eigenvectors require a consistent metric

PAW introduces the generalized problem \(Hc=\epsilon Sc\). The sampled Davidson
body forms both projected Hamiltonian and overlap quantities, including
projector contributions and communicator reductions (`davidson.F` 494–620).
The full variant maintains Hamiltonian and overlap actions separately, then
solves a generalized subspace problem (`david_full.F` selected ranges).

The subspace solver selects real or complex wrappers and a local or distributed
path. Its sampled local route checks the library status and broadcasts results
only on success (`david_full.F` 2145–2250). The ordinary subspace rotation has
separate generalized, ordinary and approximate branches (`subrot.F` 600–763).
Its approximate helper suppresses rotations near a small energy denominator
and bounds their magnitude (1917–1958). Those algorithmic choices require
their own accuracy analysis.

The older bandwise step calls an operator containing overlap corrections and
then explicitly subtracts the eigenvalue times the plane-wave coefficients
before preconditioning (`steep.F` 225–280). This connects the electrostatics
study's warning: an intermediate operator buffer need not yet be the complete
generalized residual. Orthogonality, projector coherence and the metric must
be followed through every transformation.

Failure handling also varies. The sampled residual solver warns and stops the
affected band's current work after a subspace eigensolver failure; the interior
Davidson branch can retry a smaller subspace before issuing a fatal error
(`rmm-diis.F` 486–520; `david_inner.F` 699–738). A successful outer return
therefore needs a trace of how local failures affect subsequent iterations.
No failure was reproduced in this study.

## Several different meanings of convergence coexist

The common outer helper compares the maximum magnitude of total-energy change
and a solver-supplied eigenvalue-change measure against the requested threshold.
It also enforces delay/minimum iterations and can withhold convergence until
mixing has occurred. At the iteration cap it terminates regardless, carrying a
separate unconverged indicator; a one-step cap has special handling
(`electron_common.F` 15–65). An external stop is another termination reason.

The main call supplies the energy change and the solver's weighted eigenvalue
change, **not a density norm**, to this helper (`electron.F` 639–650, 719).
The charge update and mixing occur later under their own conditions (777–850).
Consequently a loop-exit flag alone is not a density-convergence certificate.
Nor can an energy-change threshold prove global ground-state selection or the
accuracy of a particular observable.

Inner solvers have different rules. The blocked Davidson sample uses maximum
eigenvalue changes, relative improvement and storage depth; its reported
residual summary is weighted by occupations and reciprocal weights
(`davidson.F` 569–573, 741–780). The full variant separates strict and loose
state groups using occupations and allows residual/history-based refinements
(`david_full.F` 220–282, 569–592). The residual solver can stop low-occupation
bands early and changes behavior when the optional historical bound is absent
(`rmm-diis.F` 673–717).

These observations motivate distinct later questions about occupied states,
empty states used in response, density stationarity and observable accuracy.
They are not evidence that any particular calculation is inaccurate. A weighted
residual summary can conceal a weakly weighted state by construction.

## Mixing includes atomic and optional kinetic state

Simple mixing handles reciprocal density and PAW angular state together, with
different charge/magnetic settings. A reciprocal preconditioner suppresses
long wavelengths; the origin receives separate handling. A damped variant
retains velocity-like arrays between calls (`mix.F` 23–191).

The Broyden entry packs coarse-grid density, PAW state, optional kinetic density
and optional additional one-center state into one problem. It gives kinetic
density a separate preconditioning scale and also updates the fine grid outside
the coarse representation (`broyden.F` 100–238). The reduced-storage weights
and cell-volume normalization are part of the norm. This is not a mixer over
only the visible charge grid.

The update machinery preserves matrices, counters and vector history. Reset
can discard history or retain information; capacity management shifts stored
vectors (`broyden.F` 554–670). The initial reciprocal preconditioner treats the
origin differently from the simple mixer (1210–1274). Reset, cell change,
functional change and restart should therefore be analyzed as state transitions,
not assumed equivalent to a fresh iteration with the same density.

The much smaller `diis.F` helper is used by atomic routines in `rhfatm.F`;
it is distinct from both the band residual solver and the main charge mixer.
Its constrained linear solve can return an error before assigning a new result,
while the outer step does not act on that error (`diis.F` 166–257). This is a
specific source-level failure-propagation concern. Reachability with actual
atomic inputs, and the consequences at those callers, remain untested.

## Occupations determine more than the reported Fermi energy

The occupation/DOS driver selects Fermi smearing, other broadening schemes or
tetrahedron integration, handles spin constraints, and accumulates an entropy
contribution. It can separately request tetrahedron DOS after another occupation
route (`dos.F` 637–845). The total energy then includes this correction;
reported extrapolations and variational quantities need their exact consumer
conventions preserved.

The inspected modern Fermi-level procedure first tries a midpoint between
estimated band edges, checks electron count, then bisects if needed. Its
acceptable counting error can include an estimate of attainable precision;
it warns if interval collapse prevents the target (`fermi_energy.F` 139–251).
Distributed counting compensates for replicated communicator dimensions
(265–303). This is a method and layout contract, not simply sorting eigenvalues
and selecting one entry.

The smearing kernel includes bounded far-tail handling and several functional
forms, including a polynomial recurrence. Host and device paths use different
error-function calls (`fermi_energy.F` 412–509). Their numerical agreement has
not been measured. The full legacy root search and all entropy formulas remain
open.

Tetrahedron occupations involve integration weights, a degeneracy correction
for electron-count error and division by spin and sampling weights (`tet.F`
406–537, sampled portions). Degenerate bands and zero-weight sampling points
need explicit input-domain and caller analysis. The formulas and convergence
with reciprocal sampling remain largely unread.

## Other loops and postprocessing retain separate contracts

The direct-optimization driver has a corrector sequence and a different
convergence test, optionally including an expected energy change
(`electron_all.F` 438–473, 600–661). The sampled `rot.F` body adjusts steps
using energy/slope information and bounded polynomial fits, updates orbital
and projector combinations, rotates subspaces and restores orthogonality.
Some paths also update auxiliary eigenvalue state. This resolves its basic
role left open by the geometry pass; its full optimization derivation remains
future work.

The potential-optimization driver uses an inner linear-response iteration,
degenerate clusters and occupation differences under perturbed eigenvalues
(`electron_OEP.F` 597–689). The local-exchange driver builds a separate exchange
field and transfers it between grids (`electron_lhf.F` 433–480). An inner
self-consistency loop in `subrot_scf.F` can stop on relative density-norm
improvement as well as energy changes or an iteration cap (430–465). Their
names do not justify applying the main loop's convergence semantics to them.

Gap analysis requires sorted eigenvalues and calculates classifications using
both occupations and a local-Fermi construction. One occupation branch uses
a half-filled threshold (`bandgap_tools.F` selected ranges). The output is a
classification of the supplied electronic spectrum, not an independent
many-body gap calculation.

Localization, partial density and tunneling-output files extend this partition
beyond solvers. The sampled localization expression divides by density and
uses a separate floor in its final scale (`elf.F` 245–294); vacuum handling
requires upstream context. Partial-density selection and reconstruction remain
mostly unread. The sampled tunneling writer explicitly rejects more than one
reciprocal-point parallel group (`stm.F` 110–115). The shared `ini.F` spline
helper also crosses this partition into XC tables. None of these files is
considered deeply analyzed by inventory membership.

## Execution targets and return conditions

Band solvers combine batched operator work, reductions, redistributions and
device queues. The sampled full-Davidson operator path disables one asynchronous
redistribution option during offload, while its subspace solver disables the
distributed-aware branch when offload is active (`david_full.F` 1096–1099,
2190–2191). Density mixing and occupation calculation also include host regions.
These choices warrant workload-specific CPU/NVIDIA/AMD study; no execution
support or performance result follows from the directives.

Return with response/many-body consumers for empty-state accuracy and degeneracy;
with ions for stationarity needed by forces; with nonlocal interactions for
hybrid schedules; and with numerical libraries for eigensolver and reduction
contracts. Later work must derive convergence meanings, trace all failure and
reset paths, assess metastable solutions, and challenge charge conservation,
metric orthogonality, occupation integration and observable convergence on
independently chosen scientific workloads. This pass identifies those questions
without claiming that they have been tested or settled.

## Review disposition

The [single independent review](reviews/electronic-solution.md) requested no
corrections. Its scope and limits remain part of this first pass. No second
review, build or numerical experiment was performed.
