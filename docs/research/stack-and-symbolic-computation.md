# Stack and symbolic computation: discussion starting point

2026-09-25. User-directed reopening of stack selection. No language, compiler,
runtime, numerical library or code generator is selected by this note. Evidence
is documentation reading, with the acquired Libxc README inspected at its pinned
revision. No compiler or numerical experiment was run for this comparison.

The subsequent [C++ rigor stack investigation](cpp-rigor-stack.md) maps candidate
verification and performance tools, with their limits and proposed qualification
cases. It preserves open stack selection and the user's resource-conscious design
stance.

## Separate the choices, then test their composition

The application language, scientific routine language, kernel execution backend,
and mathematical derivation/code-generation tools need not be identical. Each
additional boundary must earn its integration cost. A single-language option
remains eligible; mixed-language execution is a candidate rather than a premise.
CPU and NVIDIA remain alpha requirements; AMD remains the second wave.

Go, JVM languages and Zig are excluded by current user direction. C, C++, Rust
and OxCaml are explicit whole-program candidates. Julia is a proposed addition;
modern Fortran can also be considered for a whole scientific application. Chapel
is a secondary possibility if its task/distribution runtime is acceptable, not
a way to reintroduce an unwanted concurrency architecture.

## Core candidates: provisional engineering judgments

| Candidate | Reason to examine it | Questions that could change the judgment |
| --- | --- | --- |
| C | Direct native interfaces, explicit storage, small abstraction vocabulary | Cost of manually expressing ownership, cleanup, scientific distinctions and generic numerical operations |
| C++ | Strong native HPC/GPU baseline, RAII, templates and library integration | Undefined behavior exposure, alias/lifetime discipline, build complexity and whether abstractions actually optimize away |
| Rust | Static ownership, algebraic data types and explicit unsafe boundaries | Actual async/FFI ownership, kernel compiler coverage, native library integration and whether safety remains effective across them |
| OxCaml | Algebraic data types plus modes, unboxed values, stack allocation and SIMD; attractive for symbolic/compiler work too | MPI/GPU/native-array integration, allocation control, runtime interactions and supported deployment targets |
| Julia | Numerical expressiveness, specialization and an existing DFT reference in DFTK | Type stability, allocations, compilation/deployment behavior, runtime ownership and distributed/device interoperability |
| Modern Fortran | Array-oriented numerical source, scientific toolchains and direct GPU options | Application data modeling, interface/build ergonomics, temporaries and compiler-specific accelerator paths |

These are reasons for experiments, not measured rankings. C++ is a useful native
HPC integration baseline; Rust's principal attraction is structural control of
ownership, not an assumed speed advantage. All candidates still need scientific
validation. Memory safety does not establish correct equations or conditioning.

Primary capability references:

- [Kokkos programming model](https://kokkos.org/kokkos-core-wiki/ProgrammingGuide/ProgrammingModel.html)
  separates execution, memory and layout in its C++ model; adopting it is a separate choice.
- [Rust ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)
  describes compile-time ownership; foreign/device operations need their own sound boundary.
- OxCaml documents [modes](https://oxcaml.org/documentation/modes/intro/),
  [stack allocation](https://oxcaml.org/documentation/stack-allocation/reference/)
  and [SIMD](https://oxcaml.org/documentation/simd/intro/). Those capabilities
  justify evaluation, without establishing a complete HPC stack.
- Julia's [performance guidance](https://docs.julialang.org/en/v1.12/manual/performance-tips/)
  identifies allocation, type stability and compilation concerns; DFTK documents
  [GPU execution and its coverage limits](https://docs.dftk.org/stable/tricks/gpu/).
- [Chapel GPU documentation](https://chapel-lang.org/docs/technotes/gpu.html)
  describes GPU/multilocale execution and concrete restrictions. Its runtime
  model needs explicit consideration given the user's concurrency preferences.

## Ownership handoff with resident data

The user wants existing allocations to stay in place while ownership moves through
operations. Their word "lease" was withdrawn and supplies no architectural basis
for a leasing service, registry or manager. A normal operation takes an owning
handle; after completion it returns the resulting owned state. Pending GPU/MPI
work owns the resources it still needs. Dropping a caller's handle cannot permit
early deallocation or concurrent mutation of unfinished work.

The native adapter must preserve the allocation's original destruction mechanism.
Ownership of an operation can be expressed in the host while a foreign routine
receives a scoped address/descriptor; the foreign routine need not own the allocator.
Shared immutable inputs, independent output storage and temporary borrows are
available where the actual computation needs them. Their use does not mandate
central runtime accounting.

Each candidate must demonstrate operating on existing storage with compatible
element/complex representation, dimensions/strides, alignment, memory space and
device context. Completion dependencies must cross the boundary correctly.
Necessary redistribution, representation conversion or faster explicit packing
is measured as part of the operation. A shared pointer alone does not establish
that a runtime performs no hidden copying or device migration.

## Calculation languages and tools

**Fortran deserves a real comparison.** Standard C interoperability permits
deliberate interfaces; CUDA Fortran provides explicit NVIDIA device programming.
Study native/compiler-directive alternatives against actual required loops and
library calls. Do not assume array syntax is free of temporaries or that one
GPU compiler's support establishes portability.
[Fortran C interoperability](https://gcc.gnu.org/onlinedocs/gfortran/Interoperability-with-C.html),
[CUDA Fortran](https://docs.nvidia.com/hpc-sdk/compilers/cuda-fortran-prog-guide/).

**APL is an array-language family, so choose an implementation for evaluation.**
[Co-dfns](https://github.com/co-dfns/co-dfns) is a concrete compiled APL candidate.
Its actual primitive coverage, FP64/complex behavior, external storage integration,
runtime dependencies and distribution terms need study. Compact source alone
does not establish kernel fusion, residency or speed.

**Futhark is worth adding to the kernel list.** It provides compiled array programs
with a C API and GPU backends. The documented ordinary array constructor copies
input data; the raw constructor instead uses external storage that the caller
must retain and that Futhark does not free. This is concrete evidence for an
ownership/residency experiment. Its raw interface is marked unstable; inspect the
actual semantics and maintenance cost instead of deciding from that label.
Context compatibility and asynchronous completion remain part of the test.
[Futhark C API](https://futhark.readthedocs.io/en/latest/c-api.html).

**cuda-oxide remains open on its merits.** Its current feature table reports
FP64 math and NVIDIA compilation paths. These are upstream claims to check on
our pinned compiler, kernels and hardware; neither the label nor the table
establishes numerical qualification. Coordinate with `exv-x34`.
[Feature table](https://nvlabs.github.io/cuda-oxide/appendix/supported-features.html).

## Symbolic work before numeric execution

There is a concrete precedent: FFTW's OCaml generator constructs and algebraically
simplifies transform graphs, then emits numerical code. This demonstrates a role
for a different generator language without requiring that language at numerical
runtime. [FFTW generator](https://www.fftw.org/doc/Generating-your-own-code.html).

The acquired Libxc README at commit
`db80b1dcb8b2ece33d89cfd581f80cec15f817f3`, in its Maple implementation section,
describes generating C kernels and derivatives from a functional expression.
That is evidence for the method, not a claim that the current upstream pipeline
is unchanged. [Pinned Libxc README](https://gitlab.com/libxc/libxc/-/blob/db80b1dcb8b2ece33d89cfd581f80cec15f817f3/README.md).

Candidate opportunities to establish through each scientific expedition:

| Opportunity | Potential benefit | Required justification |
| --- | --- | --- |
| Derive related energy/derivative expressions together | Shared subexpressions, fewer transcription discrepancies | Full dependencies and the intended derivative, including representation changes |
| Specialize on established model structure | Remove absent terms, exploit proven symmetries, reduce indexing work | Assumptions remain valid for that method/configuration |
| Preserve factorizations and contraction structure | Avoid large intermediates and choose an efficient contraction order | Dimensions, conjugation, numerical error and memory/communication costs |
| Derive local series or stable equivalent forms | Improve accuracy near cancellation or limiting regimes | Domain, branch, remainder/error and switching behavior |
| Fuse repeated array expressions | Reduce passes through memory and temporary arrays | Register pressure, occupancy, actual layouts and end-to-end measurements |

For illustration, evaluating `U (V† X)` can avoid constructing a dense `U V†`
when the factor dimensions make that advantageous. This is ordinary algebra made
available to the implementation through a structured representation; it is not
a claim that every operator in our science admits that factorization.

An expression generator needs explicit assumptions, a choice of derivative,
numerically justified rewrites, scheduling and target code generation. SymPy has
code printers and generation tools, but its documentation explicitly says that
printing does not automatically produce optimized code and CSE is not applied
automatically throughout the pipeline. [SymPy code generation](https://docs.sympy.org/latest/modules/codegen.html).

Automatic differentiation is also a candidate, with a different role from
symbolic simplification. Enzyme works on LLVM representations; its usable
language/backend/compiler combinations need concrete evaluation. A differentiated
program still needs justification that it computes the derivative required by
the science. Iterative stopping, branch changes, degeneracies and omitted basis
dependence cannot be resolved by the mere presence of an AD tool.
[Enzyme](https://enzyme.mit.edu/), [usage and semantic options](https://enzyme.mit.edu/getting_started/UsingEnzyme/).

Real-number identities are not blanket permission to reorder floating-point
arithmetic. A rewrite can alter cancellation, overflow, domain or branch behavior.
Fewer scalar operations can also increase storage or register pressure. Keep
the mathematical specification and the numerical implementation inspectable,
and use independent limits/derivative checks/high-precision evaluations where
appropriate. Generating both production code and its sole oracle from the same
expression would leave shared conceptual mistakes unchallenged.

## Evidence needed before selection

Propose a small matched set after the relevant focused studies define its science:

1. A core operation involving owned device state, native calls, interruption and
   output, to compare whether ownership remains intelligible across boundaries.
2. A local formula with derivatives and difficult limits, comparing written and
   generated implementations against independently established values/properties.
3. A complex operator/contraction on already allocated arrays, including layout,
   scratch space and GPU completion. Compare native and array-language paths.
4. A representative driver phase involving FFT/library operations and MPI, to
   expose synchronization, transfers and repeated conversion hidden by microbenchmarks.

Use the same trusted numerical backend first when isolating host-language effects;
then compare each candidate's strongest complete implementation. Measure time to
the specified scientifically acceptable result, memory, communication and data
movement, with construction/compilation costs reported separately. Correctness
and performance remain joint acceptance requirements. No universal tolerance,
bitwise replay criterion or fastest-language claim follows from this note.

The concrete evaluation work is tracked as `exv-9lz` in beads; detailed scientific
methods remain with the mandatory focused expeditions. The current output is a
discussion and an open decision, not authorization by implication to implement a
multi-language runtime or build a general symbolic compiler.
