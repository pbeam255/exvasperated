# Input interpretation, output and continuation

First pass, 2026-09-24. Study area: `io`, 16 files. This pass traces selected
input and continuation contracts through their implementations. It is not a
complete grammar, binary-format specification or output-schema audit. No VASP
calculation or restart was executed.

## Reading scope and file roles

Source identities are pinned in the [inventory](../vasp-source-inventory.csv).
All files received a procedure/declaration scan. Context reading is listed below;
unlisted bodies remain unexamined in this pass.

| File | Context reading | Role and unresolved depth |
| --- | --- | --- |
| `incar_reader.F` | 1-365, 750-1045; image/key searches | In-memory input map, typed retrieval, image overrides, usage tracking and grammar machinery. Remaining value/group transformations need further tracing. |
| `incar_reader.inc` | 1-157 | Generated typed/ranked bodies for text, HDF5 and parameter output. |
| `reader_base.F` | 1-156 | Legacy calling interface over the new input reader. |
| `reader_base.inc` | 1-31 | Wrapper behavior for counts, defaults and error continuation. |
| `reader.F` | 60-210; procedure scan elsewhere | Large scientific default/selection reader plus MPI/thread and atomic-data readers. Most parameter interactions remain with their scientific studies. |
| `poscar.F` | 80-190, 365-735, 1825-1905 | Staged structure reading, coordinate/scaling conversion and continuation trailer. Alternate readers and complete velocity/thermostat input remain partial. |
| `poscar_struct.F` | 1-102 | Structure, dynamics, lattice and thermostat records, including pointer relationships. |
| `fileio.F` | 53-232, 265-380, 540-635, 843-937, 1394-1560 | Wavefunction record selection, basis-remapping entry, density restart and fallback. Full binary layout and all writers remain partial. |
| `vhdf5.F` | 1-157; procedure scan elsewhere | Scientific HDF5 schemas, trajectories, wavefunctions and original-input capture. Most dataset layouts remain unexamined. |
| `vhdf5_base.F` | 180-216, 292-429, 449-468, 2538-2568; synchronization search | File creation, access properties, write ownership, errors and text-file capture. Typed datasets, dimensions and resource cleanup need deeper tracing. |
| `xml.F` | 12-129, 515-559 | Incremental structured output, tag stack and closure. Observable-specific serialization remains partial. |
| `xml_writer.F` | 16-120 | Grouped effective-parameter output; remaining parameters not individually audited. |
| `writer.F` | 8-160 | Optional atom-centered moment/density output, allocations and a parallel restriction. Scientific projection bodies remain partial. |
| `lib/diolib.F` | 1-156 | Conditional flush versus close/reopen behavior. Other file-position helpers only scanned. |
| `lib/dlexlib.F` | 264-392 | Item counting, typed validation and repeated-value handling; the remaining lexical routines only scanned. |
| `lib/drdatab.F` | 1-155 | Older file-search parser and initialization, buffer limits and opening. Remaining extraction and current callers not traced. |

The execution study supplies context from `main_mpi.F` 85-138 and 330-361.
Public file names below are established interfaces, documented by VASP's
[output overview](https://vasp.at/wiki/Output), [structure format](https://vasp.at/wiki/POSCAR),
[wavefunction file page](https://vasp.at/wiki/index.php/WAVECAR) and
[density file page](https://vasp.at/wiki/CHGCAR). Current documentation is a public
interface reference; the source findings below specifically concern 6.5.1.

## A parameter has several stages of meaning

The text path stores assignments before knowing which numerical type and shape
a consumer will request. Typed retrieval is later, using Fortran input conversion
after preprocessing the stored value (`incar_reader.inc`, 56-88). A missing
assignment leaves the caller's value unchanged. Defaults consequently belong
largely to the consuming readers, not to one central schema.

The distinction matters in `reader.F` 131-210: the initial restart choice depends
on whether a wavefunction file was found, and a later algorithm selection can
override an earlier numerical selector. The general pattern is input discovery,
caller default, user assignment, interpretation, then later adjustment. A final
effective setting need not equal the parsed assignment or a printed default.

`reader_base.F` and its include preserve older call shapes but route retrieval
through the newer reader. Some legacy arguments are ignored; the old open/close
entry points are empty. Thus an apparent repeated file-opening sequence in a
caller need not perform repeated disk IO. However, the old lexical library is
still involved: the new reader calls its item counter (`incar_reader.F`,
306-317). Replacing the text parser without examining these helpers would miss
part of actual numerical syntax and validation.

Error handling also depends on the call. A missing value is distinguished from
a conversion failure; supplying an error-result argument allows a conversion
failure to return instead of requesting immediate logging/stopping
(`incar_reader.F`, 772-785). The wrapper's continuation argument changes which
form it invokes (`reader_base.inc`, 24-31). The caller must interpret the returned
state; there is no universal all-or-nothing validation transaction established
by these routines.

## Precedence is contextual

For ordinary text lookup, the reader first searches an image-specific key, then
the common key, using case-normalized names (`incar_reader.F`, 813-832). The inner
search returns the first matching stored assignment. Parser construction appends
recognized assignments and its reduction step only resizes the array
(229-250, 893-925). Together these support a first-occurrence interpretation for
duplicate keys in that path. This has not been verified by execution, and is not
a claim about every historic parser or HDF5 representation.

The MPI startup can initialize HDF5 input state and then replace it with the
text-file representation when the text file exists (`main_mpi.F`, 91-113).
After topology selection, an image-local text file can replace the input object;
without one, the image selector supplies an override context (330-361).
Structure input independently prefers its text file when present
(`poscar.F`, 90-104). These are separate choices; they do not establish a single
global precedence rule covering every input object.

Unused-input reporting is based on whether a reader consumed an assignment,
with exceptions for some later reads and irrelevant image scopes
(`incar_reader.F`, 319-362). It is therefore sensitive to feature activation and
read timing. An unused assignment is not automatically a misspelling, and a
consumed assignment is not proof that it determines the final method.

The grammar machinery recognizes nested groups, comments, continuations and
multiline values. The important unresolved cases are interactions: quoted
delimiters, malformed nesting, duplicate assignments, short arrays, surplus
values and repeated-value counts. They should become independent, minimal
compatibility probes after the full value transformations are traced.

## Structure IO already performs scientific transformations

The early structure read establishes dimensions and lattice information; the
later read establishes positions and dynamics state. Text input accepts either
one factor or three Cartesian component factors. A negative scalar is interpreted
through a requested volume. Lattice orientation is checked after scaling
(`poscar.F`, 106-153, 395-457). Cartesian input positions are scaled and converted
to fractional coordinates before a primitive-cell mapping call (615-623).
Consequently a byte-identical coordinate triple can represent different physical
positions under different input modes.

The inspected HDF5 stages differ: the early reader requests component scaling
factors (127-133), while the full reader first attempts a scalar and falls back
to components (414-427). Producer conventions and initialization need tracing
before claiming equivalent accepted inputs or diagnosing a runtime defect.

The full read allocates dynamics arrays, initializes several histories, and
aliases the structure's position pointer to the dynamics position storage
(577-589). That joins IO to the foundations study's lifetime and aliasing
questions. The flags for constrained movement also require the geometry/ions
studies to explain which directions they constrain.

Continuation adds more than positions. The trailer writer includes conditional
lattice velocities, ionic velocities, a time step, thermostat state and predictor
history (`poscar.F`, 1825-1900). Velocity conversion itself depends on the dynamics
mode. A restart that reads only positions and velocities may fail to reproduce
the intended continuation, even if its first printed energy looks reasonable.
Complete trajectory equivalence remains a scientific question, not a format
acceptance test.

## Electronic restart is adaptation, validation and possible fallback

The wavefunction opener discovers a direct-access record length from the file
before reopening it, and the reader recognizes several precision/record variants
(`fileio.F`, 53-122, 279-300). The writer has a separate compile-time coefficient
precision choice (843-937). Working arithmetic precision alone therefore does
not determine checkpoint precision or layout.

The header contains cell, cutoff and dimensional information. Some disagreements
are tolerated for a later attempt; an unreadable header can reset the startup
choice, while a particular continuation mode requests an error (145-217).
The coefficient reader constructs a mapping between old and new plane-wave
bases, with different lattice choices for different restart modes (359-372).
Spin conversion and distribution paths are also present. Their mathematical
normalization, all failure branches and read/write round trips remain open.

The density path similarly performs scientific work: after reading the old
geometry and density, it subtracts the superposed atomic density at the old
positions and adds it at the new positions (`fileio.F`, 1433-1493). It also reads
PAW on-site occupancies and magnetization channels. Missing atoms, incompatible
grid data, incomplete density or missing on-site data can change the requested
initialization mode (1446-1472, 1500-1558); partial magnetic data has separate
handling. The final caller response needs tracing before asserting exactly which
new initialization occurs.

**Parity implication:** continuation has at least three distinct outcomes to
characterize: accepted state, transformed state and a changed initialization
request. It cannot be assessed by file existence or parser success alone.

## Output ownership, visibility and completeness are separate contracts

The HDF5 layer separates scientific writers from general file/dataset operations.
Output creation can truncate an existing file, is gated by write ownership, and
can configure MPI access only under corresponding build support
(`vhdf5_base.F`, 292-400). A synchronization-related path disables file locking
and a separate guarded flush calls into HDF5 (373-380, 452-457). Those source
actions alone do not establish crash consistency or safe concurrent readers;
the complete HDF5 access protocol needs further inspection.

Selected text input files are reread from disk during ordinary HDF5 finalization
(`vhdf5.F`, 99-153; `vhdf5_base.F`, 2549-2562). This is distinct from both
effective-parameter output and a snapshot of the input consumed earlier: a file
changed during the calculation could be archived in its later form. File and
image-local path selection also occur again at shutdown. This is a source-level
inference, not an observed run. Ordinary completion, early exits and interrupted
jobs therefore deserve separate checks for results and provenance. Likewise, XML is built
incrementally with a saved tag stack, and ordinary finalization closes it
(`xml.F`, 12-115, 515-552). A well-formed final XML file and a scientifically
converged calculation are different properties.

The legacy flush helper may close and reopen a file, while another build branch
uses a flush for sequential access (`lib/diolib.F`, 10-156). This identifies
platform and filesystem behavior to measure, without assuming the helper's name
guarantees persistence after a crash.

Finally, `writer.F` is not a universal output dispatcher: it handles optional
atom-centered quantities, allocates projection-related state and rejects one
reciprocal-point parallel subdivision in the examined moment path (139-147).
Output capabilities can constrain a parallel calculation too. Device-to-host
readiness before writers and continuation across CPU/NVIDIA/AMD require the
representation and parallel studies; no successful cross-target restart is
claimed here.

## Candidate improvements and return conditions

Later design could make input precedence, effective settings and restart
adaptations directly inspectable. It could also make interrupted output easier
for downstream tools to interpret. These are candidate improvements inferred
from the studied paths, not chosen architecture or a promise to preserve every
reference fallback.

Return with geometry and ions for constraints, velocity conventions and complete
continuation state; with PAW/representation for on-site data, basis remapping
and normalization; with parallel for ownership, collective errors and device
synchronization. Return with each scientific study to trace its reader defaults
and observable schemas. Useful later probes pair fresh/restarted calculations,
vary one representation choice, and deliberately exercise incomplete input and
interrupted output. No such experiment ran here. This first pass leaves exact
format specifications, full schemas and the complete input-combination surface
for later work.

## Review disposition

The [single independent review](reviews/io.md) identified two warranted
clarifications. The report now distinguishes shutdown-time disk capture from
previously consumed input, and scopes the scalar/component scaling description
to text input while preserving the HDF5 stage difference as an open question.
Both were checked against source and corrected; no second review was requested.
