# Independent review: execution first pass

Reviewed 2026-09-24 against the quarantined VASP 6.5.1 snapshot. One review
round, depth one; no delegated review, build or calculation. Findings refer to
the report before author fixes. All source discussion below is original prose.

## Findings

### P2 — Limit the preparation-only claim to paths reaching its check

The lifecycle discussion (report lines 91-94) could be read as a promise that
the preparation-only command-line mode cannot perform a scientific calculation.
Its check is in `main.F` 2569-2575. The supplied-force-constant phonon branch
at 1278-1298 invokes the phonon driver and jumps to finalization before that
check. The input setting is read independently in `phonon.F` 690-711, and the
command-line handling at `command_line.F` 84-87 only sets the preparation flag.
The flag search found no earlier check that protects this alternate branch.

Suggested fix: say that paths reaching this check stop before the ordinary
electronic/ionic loop. Explicitly retain the earlier phonon-driver exception as
a source-level finding, with its combined command-line behavior still requiring
a bounded execution probe. Avoid claiming that preparation performs no numerical
work; setup itself includes numerical operations.

### P2 — Describe staged structure reading and early output precisely

The statement that structure reading precedes the general settings reader
(report lines 88-90) overstates what has been read. `main.F` 652-653 reads the
structure header; the general reader is called at 698-726; the fuller structure
read follows at 930-932. This ordering matters because the report is identifying
dependencies between input interpretation and initialization.

Also, thread/device initialization precedes the main program's main output-file
opening block, but startup can already create image-local standard output
within `main_mpi.F` 330-337. That occurs during the MPI initialization call at
`main.F` 528, before thread/device initialization at 540-551.

Suggested fix: distinguish header reading from the later full structure read,
and qualify the output statement to the main output block or mention the early
image-output exception. Add the newly examined ranges to the report's reading
scope when incorporating the correction.

## Other assessed claims

The sampled source supports the report's main findings: preprocessing changes
representation and arithmetic dispatch; input handling and rank topology are
coupled; some band-decomposition choices are normalized; ordinary calculation,
alternate drivers and finalization have distinct paths; electronic recovery
and termination policy cannot be reduced to a successful process exit.

The report appropriately separates source inspection from execution evidence,
leaves method/target combinations unproven, and records return conditions.
Its limited first-pass scope is acceptable after the above corrections; a full
cleanup proof or exhaustive analysis of the large main program is not required
to finish this pass. No copied proprietary implementation text was found in the
report.

## Review scope

Read project guidance and the complete report. Independently inspected:

- `makefile` 1-281; `lib/makefile` 1-48; the beginning of `.objects`;
  `makedeps.awk`, `makeparam.F` and `param.inc`; the `vasp.cfg` header.
- `symbol.inc` 1-100 and 660-814; `main_mpi.F` 80-405.
- `main.F` 505-750, 910-945, 998-1025, 1260-1304, 2550-2580,
  3318-3378, 3445-3495, 3670-3706, 5188-5230 and 5690-5905;
  searches for structure reading, preparation-only checks and termination.
- `command_line.F` 1-117; `tutor.F` 460-530; `phonon.F` 690-730;
  a case-insensitive preparation-flag search across Fortran/include files.

This review did not independently audit every scope-table file or verify the
author's historical reading activity. It checked the substantive lifecycle
claims and their source-level limitations. No reference executable was run.
