# Independent review: numerical foundations and shared state

Reviewed 2026-09-24 against the quarantined 6.5.1 source. This is the single
independent review requested for this first pass. No child agents were used,
and no VASP build or runtime experiment was performed.

## Scope checked independently

- Read the project guidance and the complete foundations report.
- Inspected all five assigned files: `base.F` 1-412, `lib/preclib.F` 1-8,
  `constant.F` 1-76, `smart_allocate.F` 1-61 and `string.F` 1-642.
- Checked search hits connecting the buffer helpers to `fftw.F`, `intelmkl.F`,
  `nvcuda.F` and `crayhip.F`, and the storage views to `gridq.F` and
  `lr_helper.F`. These searches confirm callers exist; they do not validate
  caller lifetimes, synchronization or numerical behavior.
- Independently checked the cited intrinsic semantics. Intel documents that
  the Fortran normality predicate accepts both signed zeros and excludes
  subnormals. This supports the report's carefully conditional formatting
  concern. The direct page fetch failed in this review, but the official
  documentation was retrievable through the search tool. See the
  [Intel intrinsic reference](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2026-1/ieee-is-normal.html).

## Finding requiring a report correction

### FND-1 — Medium: distinguish default formatting from explicit formats

The formatting paragraph currently applies the loss-of-detail conclusion to
the entire helper interface. The precision reduction and optional suppression
of an imaginary component describe the default formatting routes. They do not
describe every overload.

At `string.F` 353-365 and 513-525, real and complex overloads instead accept a
caller-supplied format and use it when formatting succeeds. Their fallback
returns to the defaults. These routes can request more digits and preserve
complex components, subject to the fixed temporary string capacity and the
format's success. The extended-value route at 598-607 still converts to the
working kind before using default formatting.

**Suggested fix:** qualify the rounding and interchange warning as properties
of the default formatting routes; acknowledge the explicit-format routes and
their fallback. Retain the warning that actual restart writers have not been
traced. This avoids turning a sound default-behavior observation into a claim
that higher-fidelity formatting is impossible through this module.

## Optional addition for the next return

`base.F` 335-343 also contains a dimension-padding helper. The report's return
conditions already mention padding, but its current file-role discussion does
not identify this source of it. A short mention would help the representation
study separate requested dimensions from allocated strides. Its callers and
performance assumptions may remain open; no further study is required to finish
this pass.

## Disposition

The report otherwise supports its central observations: compiler-selected
precision is not an ABI specification; declarations do not prove initialization;
energy fields cannot be indiscriminately summed; the storage helpers alias
existing memory; and reused buffer capacity and initialized logical contents
are different obligations. The source references and limitations are useful and
appropriately bounded. No unsupported claim of successful execution on any
hardware target was found. Correct FND-1, then move on with the recorded return
conditions. A second review is not requested.
