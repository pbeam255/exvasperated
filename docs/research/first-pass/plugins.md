# Plugins, foreign interfaces and host callbacks

Reference: quarantined VASP 6.5.1, inspected 2026-09-24. The partition contains
26 files and 2,993 lines, identified by the [inventory](../vasp-source-inventory.csv).
This is source inspection only. No interpreter was embedded, plugin loaded,
test executed or external calculator run. All analysis is original prose;
interface strings and private fixtures were not imported as project contracts.

## Reading scope

| File | Reading in this pass |
| --- | --- |
| `plugins.F` | Lifecycle/settings, callback dispatch, rank policy, grid transfer, additions decoding and selected data encoders. Most principal paths sampled; full host call order remains open. |
| `c2f_interface.F` | Declaration map of parser, numerical, system and profiling bindings; implementations are elsewhere. |
| `plugins/interface_cpp.cpp` | Structure/dynamics conversion, mutable arrays, force/potential callbacks, exception wrapper and interpreter lifecycle, 85–200 and 247–310. Other conversions mapped. |
| `plugins/interface_cpp.h` | Error/mode and force/stress ABI declarations, 1–50; occupation additions, 82–90; remaining layouts unread. |
| `plugins/interface_fortran.F` | Corresponding ABI declarations, 1–60; occupation additions, 77–85; remaining layouts unread. |
| `plugins/src/vasp/__init__.py` | Exports/status constants read. |
| `plugins/src/vasp/_adjust_dataclass.py` | Full adjustment functions read. |
| `plugins/src/vasp/_apply_interface.py` | Full dispatch function read. |
| `plugins/src/vasp/_entry_points.py` | Full discovery module read. |
| `plugins/src/vasp/_force_and_stress.py` | Dataclasses and dispatch read. |
| `plugins/src/vasp/_local_potential.py` | Dataclasses and dispatch read. |
| `plugins/src/vasp/_machine_learning.py` | Calculator adapter, cache and exception handling read. |
| `plugins/src/vasp/_occupations.py` | Dataclasses and dispatch read. |
| `plugins/src/vasp/_structure.py` | Dataclasses and dispatch read. |
| `plugins/src/vasp/typing.py` | Array aliases/protocol read. |
| `plugins/tests/test_entry_points.py` | Discovery tests read, not run. |
| `plugins/tests/test_interfaces.py` | Selected mock dispatch, adjustment and calculator tests; remaining assertions mapped. Fixtures not adopted. |
| `plugins/tests/test_version.py` | Test/assertion map only. |
| `plugins/tests/conftest.py` | Inventory only; unread. |
| `plugins/tests/__init__.py` | Empty file in inventory. |
| `plugins/.gitlab-ci.yml` | Environment and test invocation read. |
| `plugins/makefile` | Mixed-language archive recipe read. |
| `plugins/make-release.mk` | Conditional-source release transformation read, not executed. |
| `plugins/pyproject.toml` | Packaging and dependency declarations read. |
| `plugins/pdm.lock`, `plugins/README.md` | Inventory only; dependency records and documentation remain unread. |

## Callback families have different update semantics

This facility exposes contributions to forces/stress, the local potential,
electronic occupation controls, structural updates, and an external
machine-learning calculator route. Settings can also change the host's ionic
update mode (`plugins.F` 154–208). The complete placement of every hook in
electronic and ionic iterations remains a cross-partition question.

Force/stress callbacks add returned quantities to host energy, force and
stress arrays (`plugins.F` 638–650). The local-potential decoder instead
assigns its energy output from the returned scalar while adding the potential
to the distributed host field (718–742). Whether that scalar is an isolated
energy contribution or an accumulated total is determined by its caller;
one generic “additions” interpretation would lose this distinction.

Structural returns are displacements of lattice vectors and fractional
positions, added to the host arrays (809–819). This local decoder does not
establish subsequent reciprocal-lattice, symmetry or neighbor rebuilding.
The structure callback's input density is prepared through a transform when
allocated (413–455). Charge normalization, grid axis order and the availability
of other host state require complete caller contracts.

Occupation-control returns are mostly added to existing values. A nonzero
chemical-potential change sets a separate requested value relative to the
current chemical potential; a zero change leaves that request untouched
(`plugins.F` 851–893). The decoder declares the additions argument as output
while reading its incoming components. The declaration/use mismatch requires
a Fortran semantic and caller review; no compiler-dependent failure was tested.

The same decoder sends an integer occupation-method change through the real
broadcast routine in the serial-callback branch (`plugins.F` 880).
The ABI declares an integer (`plugins/interface_fortran.F` 77–85;
`plugins/interface_cpp.h` 82–90), while the MPI routine accepts a real array
and communicates double-precision elements (`mpi.F` 2938–2950, 3015–3023).
This is a source-level argument/datatype mismatch in an MPI configuration.
Its effect depends on compilation, layout and padding; no memory corruption
or scientific consequence was observed in this source-only study.

The external-ML host entry starts energy/forces/stress at zero, invokes the
force callback, and conditionally applies symmetry. Its pressure assignment
is inside the positive-symmetry branch (`plugins.F` 338–375). The caller's
use of pressure when that branch is absent remains unresolved.

## Ranks, grids and lifecycle

The sampled serial mode calls Python on the communicator's designated root
and broadcasts returned additions. Other modes mark all ranks active
(`plugins.F` 557–564, 638–650). The sampled grid gather supports two named
modes, gathers real planes and transposes their layout (531–554), while the
reader accepts an additional mode (189–198). Accepted input does not alone
establish that every callback supports it.

In the all-rank force path, decoding has no sum over callback results.
Plugins cannot assume that returning a rank-local contribution automatically
produces a global result. Error codes, however, are reduced across ranks before
dispatch to host diagnostics (`plugins.F` 490–527). Hanging callbacks,
exceptions before a collective and failures on only one rank require separate
operational analysis.

The host tracks initialization/finalization state and checks numeric-kind
compatibility (`plugins.F` 115–148, 464–488). The sampled stop routine does
not set its finalization flag, and the file search finds only that flag's
initialization. This weakens what the local state checks establish; repeated
finalization behavior was not executed. C++ initializes/finalizes the embedded
interpreter directly (`plugins/interface_cpp.cpp` 273–284).

## Python discovery, ordering and ownership

Python discovery loads installed entry points, then appends a matching
function from an optional conventional module. An empty discovery result
warns and returns an empty list (`plugins/src/vasp/_entry_points.py` 1–25).
The common dispatcher iterates that list, mutating a shared additions object,
and returns success even when the list is empty
(`_apply_interface.py` 8–16). Ordering may matter when multiple plugins alter
the same data; this pass did not establish stable ordering across installations.

Before dispatch, array annotations select index conversion, arrays are marked
non-writable, and nested neighbor records are adjusted recursively
(`_adjust_dataclass.py` 8–40). This is an in-place transformation before the
dispatcher's exception-catching block. Reusing a previously adjusted constants
object is therefore a different case from receiving a fresh callback object.
The integer/index array aliases have the same declared underlying type
(`typing.py` 6–8); their runtime identity and selective adjustment behavior
remain a focused return question. No local Python probe was run.

Mutable returned arrays are constructed over host buffers with a capsule
whose cleanup does not own the buffer (`plugins/interface_cpp.cpp` 134–140).
They are then placed in the additions object (143–195). In-place array edits
and rebinding a dataclass attribute need not have the same effect on host
memory. Retaining such arrays beyond the callback requires a lifetime contract;
the read-only flag on constants does not establish memory isolation.

The common Python callback handler catches exceptions from discovery/invocation
and returns an error status. The C++ wrapper separately catches Python errors
and distinguishes import failures (`_apply_interface.py` 8–16;
`plugins/interface_cpp.cpp` 247–269). It is not a catch-all for every C++
exception. Earlier plugins may already have mutated buffers when a later one
fails; no transaction or rollback behavior was established.

## Precision and calculator meaning

Two C++ paths convert the Python energy scalar to a single-precision C++
value before assigning it to a double field (`plugins/interface_cpp.cpp`
169–170, 193–194; `interface_cpp.h` 39–43). That narrowing is an actual local
precision loss, though its observable effect depends on magnitudes and use.
Array precision and scalar precision must both enter a compatibility study.

The calculator adapter constructs periodic atoms from lattice vectors,
fractional positions and indexed atomic numbers, obtains energy/forces/stress,
and adds them to the return object. Missing stress support is replaced with a
zero tensor (`plugins/src/vasp/_machine_learning.py` 31–48). Thus success
does not establish that a calculator supplied stress. That distinction matters
for cell motion and pressure-dependent scientific claims.

The adapter promotes returned arrays to double precision, which cannot recover
accuracy lost inside a lower-precision model. Stress is forwarded without a
visible sign/volume conversion in this function and then added directly by the
host decoder; the complete unit/convention agreement needs explicit tracing
against the host and calculator contracts. Calculator objects are cached
(64–68), so hidden state and invalidation also matter for repeatability.

## Existing tests, packaging and targets

The sampled tests check discovery, dispatch, index adjustment, non-writable
arrays, and accumulation from mock calculators
(`plugins/tests/test_entry_points.py`; `test_interfaces.py` 51–110).
The interface test module defines two functions with the same name at lines
56 and 62; ordinary Python module binding replaces the earlier definition.
The apparent source count therefore overstates independently collected tests.
These tests do not exercise the full Fortran/C++/Python bridge, energy
narrowing, physical stress conventions or distributed callback semantics.

Packaging declares NumPy, pybind11 and ASE dependencies; the build creates a
mixed Fortran/C++ archive, while the sampled CI script runs Python tests in a
site-specific environment (`plugins/pyproject.toml`, `plugins/makefile`,
`plugins/.gitlab-ci.yml`). The release recipe rewrites source according to
preprocessor choices (`plugins/make-release.mk` 3–13). Release configuration
must therefore accompany any reference-behavior claim. No recipe was run.

CPU, NVIDIA and AMD alpha support must include callback transfer, synchronization
and failure behavior for the execution modes actually offered. These Python
and host-memory views establish no device-memory contract. External calculators
can have their own hardware and numerical restrictions, which cannot be inferred
from the host executable's target support.

## Returns

Return with host iteration, geometry and ML studies to trace call order,
energy/stress units, structural cache rebuilding and restart behavior. Other
focused questions are precision narrowing, absent stress, rank agreement,
error/lifetime behavior, index annotation identity, finalization state and
occupation-decoder intent. Complete unread ABI layouts, fixtures, documentation
and dependency provenance later. Publicly documented interface contracts still
need attribution before promising compatibility. This report does not choose
our extension architecture or begin the broader reference campaign.

## Review disposition

The [single independent review](reviews/plugins.md) supported the existing
claims and identified an additional integer/real MPI broadcast mismatch.
That finding and its ABI/MPI evidence are now included with explicit limits
on untested consequences. No second review or experiment was performed.
