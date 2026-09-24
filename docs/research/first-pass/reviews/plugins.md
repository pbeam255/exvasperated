# Plugins and foreign interfaces: first-pass review

Reviewed 2026-09-24 against quarantined VASP 6.5.1 and the
[first-pass report](../plugins.md). This is the requested single independent
review at depth one. No child review, compilation, interpreter embedding,
plugin execution or scientific experiment was performed.

## Finding to incorporate

**Add the occupation-control broadcast type mismatch to the local concerns.**
The existing declaration/use concern is supported, but the same decoder has
a separate communication mismatch. `plugins.F` 880 passes its integer
occupation-method addition to the real-valued broadcast routine. The ABI
declares this component as a C-compatible integer at
`plugins/interface_fortran.F` 77–85, with a corresponding C++ integer at
`plugins/interface_cpp.h` 82–90. The receiver routine declares a real array
at `mpi.F` 2938–2950 and broadcasts double-precision elements at 3015–3023.
The call is active under the MPI macro configuration (`symbol.inc` 235–260)
and the decoder's serial-callback branch.

Record this as a source-level argument/datatype mismatch requiring a focused
build and ABI review. Do not claim observed corruption or a scientific result:
the actual effect depends on compilation, representation, padding and the
communication path. This is an addition to the report's local findings, not
a correction to its current behavioral claims.

## Material claims checked

- **Update semantics and structure.** `plugins.F` 638–650 adds energy,
  forces and stress, while 718–742 assigns the potential callback's energy
  scalar and adds the field. Lines 809–819 add lattice and position changes.
  Lines 413–455 prepare density through a transform when present. The report
  correctly leaves the subsequent host state reconstruction and complete
  caller contracts open.
- **Occupation control and external calculations.** `plugins.F` 851–893
  supports additive occupation controls, the conditional chemical-potential
  request, and the output-intent declaration on a subsequently read argument.
  Lines 338–375 support zero initialization of the external calculation's
  energy, forces and stress, with pressure assigned inside the positive
  symmetry branch. The report does not assert a tested failure.
- **Ranks, modes and errors.** `plugins.F` 189–198 accepts three explicit
  modes, while 531–554 handles two in the grid gather. Lines 557–564 mark
  only the selected rank active in serial mode and all ranks active otherwise.
  Lines 638–650 contain broadcasts for serial mode and no addition-result
  reduction for other modes. Error statuses are reduced at 490–527. These
  observations support the report's limited distributed semantics.
- **Lifecycle.** `plugins.F` 115–148 sets the initialization state but does
  not set the finalization state on stop. A search of this file found the
  finalization flag's initialization and its reads, without an assignment
  after initialization. The C++ routines at `plugins/interface_cpp.cpp`
  273–284 directly enter and leave the interpreter. Repeated-finalization
  behavior remains untested.
- **Discovery and adjustment.** `_entry_points.py` 1–25 loads package
  entry points before appending the optional module's function. The common
  dispatcher at `_apply_interface.py` 8–16 adjusts constants before entering
  its exception handler and returns success for an empty discovered list.
  `_adjust_dataclass.py` 8–40 supports in-place index changes, write protection
  and recursive neighbor adjustment. The alias declarations at `typing.py`
  6–8 support retaining runtime identity as an unresolved question.
- **Ownership, errors and precision.** `plugins/interface_cpp.cpp`
  134–195 creates returned arrays over supplied buffers with a non-owning
  capsule, then reads scalar energy through a C++ float conversion in both
  sampled callbacks. The force/stress ABI energy field is double at
  `plugins/interface_cpp.h` 39–43. The wrapper at 247–269 catches Python
  exceptions rather than every C++ exception. The report appropriately
  separates these local facts from unproved lifetime and rollback guarantees.
- **Calculator behavior.** `_machine_learning.py` 31–68 supports periodic
  atoms from fractional positions, indexed atomic numbers, accumulation of
  predictions, double-precision array conversion, zero substitution for
  unsupported stress, and cached calculators. There is no visible stress
  sign or volume conversion in the adapter. Complete convention agreement
  remains a return question rather than a claimed discrepancy.
- **Tests and packaging.** `plugins/tests/test_interfaces.py` 56 and 62
  define the same module-level test name, so the later definition replaces
  the earlier binding. The sampled mock tests do not exercise the complete
  bridge. The dependency declarations, mixed-language archive recipe,
  Python-oriented CI and source-rewriting release recipe support the report's
  packaging observations.

## Review limits

The inventory contains 26 assigned files totaling 2,993 lines. Every assigned
path appears in the report's reading-scope table, including grouped entries.
That establishes scope accounting, not complete analysis. This review sampled
the principal claims and followed one additional communication concern into
the ABI and MPI implementation. It did not read the unexamined fixtures and
dependency lockfile, prove complete host iteration placement, execute Python
probes, establish physical unit conventions, or test any hardware target.

The report preserves those limits and does not choose the replacement's
extension architecture. No proprietary code, comments, diagnostics or fixture
content was included in this review artifact.
