# Independent review: input, output and continuation

Reviewed 2026-09-24 against quarantined VASP 6.5.1. One review at depth one;
no delegated review and no reference execution. This assesses the bounded
first-pass report, not complete input grammars or scientific restart equivalence.

## Findings

### P2 — Distinguish end-of-run file capture from the input actually consumed

The output section says that original text inputs are captured at finalization
and discusses interruption, but it misses a related provenance limitation on
ordinary completion. `vhdf5.F` 119-139 selects file paths at shutdown;
`vhdf5_base.F` 2549-2562 reads those files at that time. The helper in
`string.F` 92-116 opens and reads the current file. This does not serialize the
previously consumed input buffer.

If a text input changes during a run, the archived text can consequently differ
from the input that established the calculation. This is a source-based inference,
not an observed run. Image-local file selection also happens again during this
capture, which makes the distinction relevant to staged input precedence.

**Suggested correction:** say explicitly that the finalizer rereads selected text
files from disk. Distinguish that capture from effective parameter output and from
a snapshot of input consumed earlier. Preserve exact provenance behavior as a
later bounded probe; no new architecture or experiment is needed for this pass.

### P3 — Scope the scaling description to the text path

The structure section's statement about one scalar or three component factors is
supported for text input. The inspected HDF5 branches differ between stages:
`poscar.F` 127-133 reads component factors in the early pass, while 414-427 in
the full pass first attempts a scalar and then component factors. The report
currently describes scaling without this qualification.

**Suggested correction:** identify the described scalar/component syntax as text
input behavior, and retain the differing HDF5 stage paths as an unresolved schema
and initialization question. These excerpts alone do not establish that valid
HDF5 inputs fail; caller and producer conventions remain to be traced.

## Supported claims and scope

The first-occurrence inference is supported by ordered append, array reduction
without deduplication, and forward lookup. Its stated restriction to this text
path and lack of execution verification are appropriate. Image-specific lookup,
text replacement of HDF5 parameter input, and later image-local replacement also
match the inspected paths.

The restart section correctly separates header fallback, basis adaptation and
density initialization changes. It does not promise that every incompatibility
falls back or that transformed state is physically equivalent. The ownership,
flush and XML closure discussion also avoids unsupported durability claims.
The file table and explicit unexamined bodies appropriately limit the study.

## Independently examined source

Ranges below were read in context; they are not a claim of whole-file coverage.

- `incar_reader.F`: 190-365, 745-1135; `incar_reader.inc`: 1-105.
- `reader_base.F`: 1-156; `reader_base.inc`: 1-31; `reader.F`: 120-215.
- `main_mpi.F`: 80-145, 320-370.
- `poscar.F`: 80-158, 388-460, 570-632, 1820-1905.
- `fileio.F`: 45-235, 270-380, 535-636, 840-940, 1394-1565.
- `vhdf5.F`: 75-157; `vhdf5_base.F`: 285-430, 445-470, 2538-2568.
- `xml.F`: 12-130, 510-562; `lib/diolib.F`: 1-160;
  `writer.F`: 90-160; `string.F`: 88-119.

No code, source comments or proprietary diagnostic text was copied into this
review. No blockers were found for proceeding after the bounded clarifications.
