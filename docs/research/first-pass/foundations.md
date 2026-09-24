# Numerical foundations and shared state

First pass, 2026-09-24. Study area: `foundations`, five files. All five were
read, but their consumers were only searched selectively. Reading a declaration
does not establish that every caller respects its contract. No executable or
scientific calculation was run.

## Reading scope and file roles

The [inventory](../vasp-source-inventory.csv) pins the source identities.

| File | Reading in this pass | Role and remaining depth |
| --- | --- | --- |
| `base.F` | 1-412 | Precision choices, shared calculation/control records and storage views. Field initialization and consumers need cross-partition tracing. |
| `lib/preclib.F` | 1-8 | Precision selection for the bundled support library; actual compiler kinds and library ABI remain unmeasured. |
| `constant.F` | 1-76 | Physical conversion factors and derived coefficients. Downstream unit consistency is not proved. |
| `smart_allocate.F` | 1-61 | Three reusable pointer-buffer helpers. Consumer search found FFT implementations for host and accelerator libraries. |
| `string.F` | 1-642 | Text ingestion, pattern scanning, case/newline operations and diagnostic formatting. Complete input grammar belongs to the IO study. |

## Precision is a request to the compiler, not a portable storage specification

`base.F` 8-26 requests real kinds with different decimal precision and integer
kinds with different ranges. A build switch can reduce the extended real kind
to the ordinary working kind; emulated extended arithmetic is also accommodated
by a conversion helper at 351-359. The support library independently requests the
same working decimal precision (`lib/preclib.F`).

**Observation:** these declarations do not themselves require a particular byte
width, exponent range, IEEE behavior, integer ABI or behavior of an external
numerical library. The compiler and build complete that contract. A fixed small
displacement used by some numerical differentiation routines is also declared
here; its declaration cannot justify accuracy for every differentiated observable.

**Implication:** CPU, NVIDIA and AMD comparisons must distinguish the selected
kinds, conversions, library interfaces and compiler arithmetic behavior. Merely
matching the kind request would not establish numerical parity. Where extended
precision is downgraded or converted for output, the result needs interpretation
at the actual precision used. No backend precision strategy is selected here.

## Unit conventions reach beyond constants

`constant.F` 20-65 combines atomic-style conventions with energy expressed in
electronvolts and length in angstroms. It derives the Coulomb and kinetic-energy
coefficients from its energy and length conversions, and includes mass,
temperature and magnetic conversions. Some literals carry an explicit working
kind while others do not. The source contains fixed historical numerical choices;
this pass neither replaces them with current tabulations nor treats their last
digits as physical truth.

The important reconstruction question is consistency: reciprocal vectors,
derivatives, charge normalization and externally supplied data must use the same
convention as the operator that consumes them. A scalar array with the right
shape can still carry the wrong units. Force, stress and response comparisons
will have to reconcile the complete chain of conversions. A future independently
chosen set of constants could intentionally differ from the reference and create
small systematic differences; that would require an explicit compatibility
decision after measurement.

## Shared records mix requests, effective state and calculated results

`base.F` 34-310 contains records spanning algorithm selection, iteration limits,
restart choices, output controls, mixing history, symmetry, prediction,
electrostatic corrections and accumulated energy terms. The same broad control
record reaches ground-state, response, many-body and plugin features. This helps
explain why following a single top-level flag does not isolate a calculation.

Initialization is uneven by construction. Some components have explicit default
values, including many energy components and selected output/plugin controls;
many other components and pointers have no declaration-time initialization.
The latter require a valid assignment or association before use. This observation
does not establish an uninitialized read: readers and startup routines may supply
the required values. Their order is part of the contract and must be traced.

Several limits and storage choices appear in these records, such as fixed-size
symmetry tables and a bounded mixing diagnostic array. Their presence identifies
questions about supported cases and overflow handling; it does not prove that
the physical method itself is restricted to the declaration's apparent size.
Energy components include corrections, double-counting terms and separately
recorded averages. Summing every field would not reconstruct a total energy.
The actual energy assembly belongs to the electronic and interaction studies.

## Storage views and reuse carry hidden caller obligations

The conversion helpers in `base.F` 361-410 create aliases to existing storage.
Complex-to-real views double the leading extent; the reverse real-storage view
halves it. Conditional branches sometimes retain complex storage directly.
These are views, not numerical conversions or independently owned copies.
The separate dimension-padding helper at 335-343 also changes a requested
extent. Its active callers and performance assumptions remain untraced;
requested dimensions and allocated strides must not be conflated.

Caller obligations therefore include storage lifetime, contiguous usable layout,
appropriate alignment, compatible representation, and a valid extent for the
reverse view. The helpers shown do not validate all of these. A mutation through
one view changes the storage seen by another. Searches found consumers in
`gridq.F` and `lr_helper.F`; their ownership and synchronization paths have not
yet been audited. These obligations are especially relevant when the same
storage has host and device associations.

`smart_allocate.F` keeps a previously associated buffer when it is large enough.
It replaces an undersized allocation, and it does not initialize new contents or
copy old contents into the replacement. Thus the requested length is a minimum
capacity, not necessarily the returned extent. Existing contents persist on the
reuse path but are not preserved on growth. The incoming pointer must have
defined association status and be suitable for any required deallocation.
Ownership, initialization and valid logical length remain caller responsibilities.
Searches found uses in `fftw.F`, `intelmkl.F`, `nvcuda.F` and `crayhip.F`; this is
a concrete connection to all required execution targets, not proof that those
targets execute successfully.

## Text helpers influence input and observability

`string.F` 91-211 reads a complete stream into an allocated string and provides
stateful scanning with escapes, ignored regions and line-ending recognition.
The scan counts before allocating result indices, then repeats the scan to fill
them. It recognizes different newline conventions and handles escaped line
continuations, but the meaning of those mechanisms in a user input file depends
on how the IO parser configures them. File-size handling, allocation failures and
malformed input need examination with that caller.

Default formatting in 257-607 is intended for compact inspection. It rounds to
a limited number of displayed digits, may suppress a small imaginary part, and
converts extended values through the working precision. Those defaults do not
provide lossless numerical interchange or restart serialization. Explicit-format
overloads at 353-365 and 513-525 can preserve more digits and complex components
when the supplied format succeeds within the temporary string capacity; failure
falls back to the defaults. Actual restart writers must be traced separately.

One concrete edge case deserves a later probe: at 397-419 the branch for values
failing the Fortran normality predicate distinguishes NaN and sign, but not
finite subnormal values from infinities. Under preserved subnormal arithmetic,
the source therefore appears capable of labeling a finite subnormal as infinite.
This is a source-level concern, not an observed VASP failure. The predicate does
include signed zeros, so zero does not justify the same inference. This language
detail was checked in the [Intel intrinsic reference](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2026-1/ieee-is-normal.html).
Compiler underflow modes and reachable callers determine its practical impact.

## Parity implications and return conditions

The useful first-pass finding is that this area contains scientific and memory
contracts despite its small size. Candidate improvements for later evaluation
include explicit units and valid state transitions, storage views with clear
ownership, and diagnostics that preserve the distinction between finite tiny
values and nonfinite values. These are findings to inform design, not an adopted
replacement architecture or a requirement to reproduce apparent defects.

Return with the representation and parallel studies to resolve aliasing,
padding, buffer reuse and device synchronization. Return with IO to trace record
initialization and text grammar. Return with energy, force and response studies
to reconcile units and differentiated quantities. The reference campaign can
then choose narrowly scoped probes of compiler kinds, numerical differentiation,
subnormal formatting and buffer growth. None of those probes ran in this pass.

## Review disposition

The [single independent review](reviews/foundations.md) identified an overbroad
formatting claim. The report now distinguishes default formatting from successful
explicit formats. The review's small padding observation was also added with
caller tracing left open. No second review round was requested.
