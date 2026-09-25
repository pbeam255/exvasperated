# C++ rigor stack: tools, design discipline and qualification

2026-09-25. Documentation-grounded identification during open stack selection.
No tools installed, C++ build configured, or verification campaign executed.
Upstream sources include development documentation: qualify specific releases
before relying on their advertised capabilities.

## Design stance

The user's demoscene analogy means resource-conscious engineering throughout:
understand the machine, data movement and working sets; make abstractions earn
their cost. Memory layout is a first-class design concern alongside logic flow.
Algebraic data types, explicit ownership and justified bounds should structure
the system. Ring buffers with cursors are one useful example, not a prescribed
architecture. "Not one byte/cycle wasted" is a guiding spirit, not a literal
optimization objective. Padding, redundant computation or extra storage can earn
their cost by improving the complete calculation.

Use sum/product types, restricted constructors and operations, move-only owners,
and explicitly scoped views. Specify dimensions, strides, alignment, aliasing,
memory space and asynchronous completion. Pending work must retain its resources.
Choose AoS/SoA, tiling, packing and queue organization from the actual access
pattern. Expose a semantic type without assuming a particular physical layout is
always best. Keep instrumentation out of the production representation unless it
serves an actual operational need.

Bound capacities, work in flight, scratch space and integer ranges where justified;
specify overflow, full-capacity and failure behavior. A production bound and a
verifier's exploration bound are different. Neither licenses clipping scientific
inputs or silently discarding history. C++ concepts constrain interfaces, not
mathematical laws. [Boost.SafeNumerics](https://www.boost.org/doc/libs/latest/libs/safe_numerics/doc/html/index.html)
and [mp-units](https://mpusz.github.io/mp-units/latest/) are candidate libraries for
checked integer arithmetic and quantities, not general refinement-type provers.

If using no-alias annotations, establish the actual non-aliasing property first.
[`__restrict__` is a compiler extension in C++](https://gcc.gnu.org/onlinedocs/gcc/Restricted-Pointers.html),
not a run-time check. An invalid promise can permit incorrect optimization.
There is no system determinism promise. Controlled, reproducible test scenarios
remain useful without constraining scientific trajectories or physical hysteresis.

## Tool map

| Purpose | Candidates | Proposed application and limit |
| --- | --- | --- |
| Compiler diagnostics | Clang and genuine GCC builds | Different compilers and standard libraries; also test actual optimized CPU/CUDA builds |
| Lint and static analysis | clang-tidy, Clang Static Analyzer, Cppcheck, CodeQL | Selected checks and path/dataflow analysis; shared engines are not independent evidence |
| Dynamic memory/UB checks | ASan, UBSan, TSan, MSan, Valgrind Memcheck | Separate compatible configurations; executed paths and instrumented boundaries determine coverage |
| Properties and fuzzing | FuzzTest, RapidCheck | Typed generators, shrinking, adversarial inputs and command sequences |
| Bounded code verification | CBMC, ESBMC | Symbolic inputs, arithmetic/pointer checks and assertions in supported C++ subsets |
| Symbolic test generation | KLEE | Targeted LLVM-level exploration; runtime and numerical support need qualification |
| Protocol state exploration | Quint with TLC or Apalache | Finite state models, bounded checks or inductive reasoning; connect models to real code |
| Concurrent algorithm exploration | GenMC, Relacy | Tiny ownership/queue/completion algorithms under declared memory models |
| Controlled simulation | Application-specific harness; FoundationDB reference; SimGrid/SMPI | Real control logic with controlled external events; not automatic whole-program determinism |
| Mutation testing | Mull plus specified scientific fault families | Test whether meaningful errors are detected; no campaign launched |
| Coverage | LLVM source coverage, selected MC/DC | Locate unexercised code and decision conditions; does not establish numerical correctness |
| GPU/MPI checking | NVIDIA Compute Sanitizer, MUST | Real device/communication correctness; distinct from host sanitizers |
| Numerical verification | Independent references, MPFR, Verificarlo, Gappa | Higher precision, sensitivity studies and selected formal numerical arguments |
| Resource/performance scrutiny | Compiler reports, llvm-mca, Nsight Systems/Compute, measured regression cases | Allocation, movement, working set, synchronization, throughput and time to accepted result |

## Compiler and static-analysis configuration

An initial host warning profile to qualify is:

```text
-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow
-Wformat=2 -Wundef -Wdouble-promotion -Wnon-virtual-dtor
-Woverloaded-virtual -Wold-style-cast -Wcast-align
```

Make selected warnings errors in our code. Pin tool versions and explicit checks;
do not inherit every new warning as policy. Casts must have a range/representation
argument beyond silencing a warning. Keep third-party analysis distinguishable.
Use clang-format and a compilation database. Test optimized configurations as
well as diagnostic builds. [Clang manual](https://clang.llvm.org/docs/UsersManual.html).

Select [clang-tidy](https://clang.llvm.org/extra/clang-tidy/) checks from bugprone,
CERT, C++ Core Guidelines, performance and modernization families. Its
`clang-analyzer-*` checks use the [Clang Static Analyzer](https://clang.llvm.org/docs/ClangStaticAnalyzer.html);
CodeChecker can organize that analysis but is not another independent engine.
[Cppcheck](https://github.com/cppcheck-opensource/cppcheck) adds a different analyzer;
[CodeQL](https://codeql.github.com/docs/codeql-language-guides/codeql-for-cpp/) adds
dataflow queries and potential project-specific misuse checks.

[Thread-safety annotations](https://clang.llvm.org/docs/ThreadSafetyAnalysis.html)
and [lifetime analysis](https://clang.llvm.org/docs/LifetimeSafety.html) deserve
qualification on the selected toolchain. Clang explicitly describes lifetime
analysis as bug finding, with optimistic unannotated calls and possible misses.
It is not a general proof of lifetime safety. GCC's currently published
[`-fanalyzer` documentation](https://gcc.gnu.org/onlinedocs/gcc/Static-Analyzer-Options.html)
says that release is suitable only for C; do not count it as qualified C++ analysis.

## Runtime checking

Use [ASan](https://clang.llvm.org/docs/AddressSanitizer.html) plus
[UBSan](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html) for ordinary
memory misuse and selected UB checks. A proposed host profile is
`-O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined
-fno-sanitize-recover=all`, with sanitizer flags at link time too. This profile
has not been executed here. UBSan does not include every useful conversion check.

Run [TSan](https://clang.llvm.org/docs/ThreadSanitizer.html) separately for host
races. [MSan](https://clang.llvm.org/docs/MemorySanitizer.html) checks uninitialized
data but needs instrumented dependencies or correct interceptors; its supported
OS list excludes this macOS host. Native BLAS, MPI, GPU and assembly boundaries
require specific treatment. [Valgrind Memcheck](https://valgrind.org/docs/manual/mc-manual.html)
offers another instrumentation approach on supported platforms.

Enable [libc++ hardening](https://libcxx.llvm.org/Hardening.html) and a separate
[libstdc++ debug build](https://gcc.gnu.org/onlinedocs/libstdc++/manual/debug_mode_using.html).
The latter changes container representations: respect build/ABI boundaries.
Ensure essential validation and test checks retain their effect under `NDEBUG`.

Two specialized candidates: [TypeSanitizer](https://clang.llvm.org/docs/TypeSanitizer.html)
for strict-aliasing violations, with documented instrumentation gaps;
[RealtimeSanitizer](https://clang.llvm.org/docs/RealtimeSanitizer.html) for known
allocation/blocking calls under annotated nonblocking entry points. The latter
could check selected hot paths; it does not establish execution-time bounds or
detect every copy. Retain tests of uninstrumented release binaries.

## Properties, fuzzing and state exploration

[FuzzTest](https://github.com/google/fuzztest) combines typed input domains and
properties with coverage-guided fuzzing. Its documented
[CMake setup](https://github.com/google/fuzztest/blob/main/doc/quickstart-cmake.md)
requires Linux and Clang. [RapidCheck's stateful interface](https://github.com/emil-e/rapidcheck/blob/master/doc/state.md)
provides model/implementation command sequences and shrinking that preserves
preconditions. Sampling these sequences is distinct from exhaustive exploration.

Generate difficult scientific domains deliberately: degeneracy, ill-conditioning,
extreme scales, awkward strides and branch boundaries. Shrinking must preserve
the condition making the example meaningful. Metamorphic properties need their
premises: a valid covariance transformation, an adjoint relation under the stated
inner product, or a derivative identity in its smooth domain. Do not assume
universal energy monotonicity, branch uniqueness or history independence.

Assuming "koni" means [Kani](https://model-checking.github.io/kani/), the direct
C/C++ relative is [CBMC](https://www.cprover.org/cbmc/), its backend verifier.
[ESBMC](https://esbmc.github.io/docs/c-cpp/) is another candidate with a Clang-based
C++ frontend. Begin with size/stride arithmetic, indexing, serialization lengths
and small state transitions. Specify input ranges, machine widths, allocation
limits, loop bounds and external-call models. Retain unwinding completeness
checks; a truncated search, unsupported construct or timeout is not a proof.
Check that assumptions admit intended inputs and properties are reachable.

Verify modern C++ support on actual code. ESBMC uses
[standard-library models](https://esbmc.github.io/docs/c-cpp/supported-features/)
and documents [constructor/destructor ordering gaps](https://esbmc.github.io/docs/c-cpp/limitations/).
These matter directly for ownership: do not claim RAII behavior proved when the
pertinent lifetime semantics are modeled incorrectly. [KLEE](https://klee-se.org/)
is an additional symbolic test-generation candidate requiring focused qualification.

[Quint/TLC/Apalache](https://quint.sh/docs/what-does-quint-do) can explore protocol
models. State finite domains, bounds and fairness assumptions; distinguish
exhaustion, bounded checking and induction. Replay model traces through the real
transition interface to test the model/implementation relationship.

[GenMC](https://github.com/MPI-SWS/genmc) examines supported concurrent LLVM code;
its [manual](https://github.com/MPI-SWS/genmc/blob/master/doc/manual/features.md)
defines feature and memory-model scope. [Relacy](https://github.com/dvyukov/relacy)
offers instrumented synchronization types for small algorithms. A race-free
program can still have wrong atomic ordering. Sequentially consistent schedule
exploration does not cover all weak-memory behavior. Example candidate subjects
are queue cursors, ownership transfer and completion signaling. If a ring buffer
is selected, examine wraparound, full/empty distinctions, publication ordering,
slot lifetime and reuse; do not extrapolate tiny-capacity results without argument.

## Simulation, mutations and failure testing

[FoundationDB](https://apple.github.io/foundationdb/testing.html) is a design
reference for running real logic with controlled scheduling and simulated
services. Its simulator is integrated with Flow, not a drop-in C++ testing
library. Our proposed test boundary controls clocks, random inputs, storage
operations, message delivery and device-completion events. Preserve seeds and
event traces; a seed alone need not reproduce a scenario after code changes.

Exercise short writes, full storage, publication interruption, delayed completion
and supported rank-failure responses. Generate only orderings allowed by the
modeled interface. Whole-job termination may be the specified MPI failure result.
Simulation does not promise unavailable recovery or numerical determinism.
[SimGrid/SMPI](https://simgrid.org/doc/latest/app_smpi.html) and its
[model checker](https://simgrid.org/doc/latest/Tutorial_Model-checking.html) are
concrete MPI simulation candidates, limited to supported calls and models.
Actual filesystem durability, MPI and device execution still need hardware tests.

[Mull](https://mull.readthedocs.io/en/latest/Features.html) supports C/C++ mutation
testing with Clang/LLVM builds and incremental campaigns. Qualify compiler
coupling and mutation operators. Surviving mutants require interpretation,
including equivalent transformations and unexercised cases. Scientific faults
may need custom injection: missing conjugation, wrong normalization, transposed
indexing, omitted derivatives or altered boundary conditions. These are proposed
fault families, not claims about Mull's built-in operators. No local mutation
campaigns; cloud campaigns require explicit user intent under project instructions.

[LLVM source coverage](https://clang.llvm.org/docs/SourceBasedCodeCoverage.html)
provides region, branch and selected MC/DC measurements. MC/DC examines the
influence of individual conditions on decisions; it does not establish every
execution path or scientific validity. Track physical regimes and specified
failure behavior alongside structural coverage.

## GPU, MPI and numerical verification

[NVIDIA Compute Sanitizer](https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html)
provides memcheck, initcheck, racecheck and synccheck. Racecheck's documented
scope is on-chip shared memory, not every global-memory/cross-stream race.
Host sanitizers do not check device execution. [MUST](https://www.i12.rwth-aachen.de/cms/i12/forschung/forschungsschwerpunkte/lehrstuhl-fuer-hochleistungsrechnen/~nrbe/must/?lidx=1)
checks MPI runtime correctness, including deadlocks and communication misuse.
Qualify thread modes and GPU-aware communication separately.

Use independent historical references and test designs, with provenance and
reuse terms; retain VASP comparisons in quarantine. Shared derivations,
generators, datasets or numerical libraries can correlate oracle errors.
[MPFR](https://mpfr.org/mpfr-current/mpfr.html) supplies arbitrary-precision
correctly rounded operations; increased precision does not correct wrong physics.
[Verificarlo](https://github.com/verificarlo/verificarlo) enables rounding/precision
sensitivity experiments. [Gappa](https://gappa.gitlabpages.inria.fr/) supports
formal arguments about specified rounded expressions. Neither automatically
establishes a full scientific routine's accuracy.

Combine reference values, residual/backward-error checks, limiting cases and
physical relationships under method-specific assumptions. Use tolerances tied to
conditioning and observables. Specify FP behavior: no global `-ffast-math` by
default; qualify local transformations, FMA contraction, exceptional values,
subnormals and rounding. Clang's strict FP mode is useful when its environment
semantics are required; disabling FMA globally is not inherently more accurate.
[Clang FP options](https://clang.llvm.org/docs/UsersManual.html#controlling-floating-point-behavior).
Generated code and assembly face the same external tests; assembly can escape
compiler instrumentation and needs actual hardware examination.

## Performance evidence and first qualification cases

Inspect compiler vectorization/optimization reports and emitted instructions.
[llvm-mca](https://llvm.org/docs/CommandGuide/llvm-mca.html) models instruction
throughput and resource pressure; it is not a full cache/system simulator.
[Nsight Systems](https://docs.nvidia.com/nsight-systems/UserGuide/index.html) and
[Nsight Compute](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html)
support whole-execution and kernel-level GPU investigations. Account for profiler
perturbation and validate conclusions with ordinary executions.

Measure allocation counts, bytes moved, peak working set, packing costs, waits,
kernel launches and time to a scientifically accepted result. Benchmark realistic
layouts, problem sizes and overlap. Use declared measurement conditions and noise
treatment. Extra padding, recomputation or explicit packing can improve total
performance; resource consciousness does not imply minimizing each counter alone.

Proposed first qualifications:

1. Parser/shape arithmetic: compiler checks, properties, fuzzing, ASan/UBSan and
   bounded verification against malformed lengths, overflow and index errors.
2. Ownership through asynchronous completion: actual language constructs,
   state/concurrency exploration, controlled failures and measured handoff costs.
3. A scientifically grounded small kernel: independent oracles, adversarial
   generators and numerical checks in diagnostic and optimized CPU/NVIDIA builds.

Use small known-correct/incorrect qualification examples to establish that each
configured tool actually examines the intended behavior. Missing instrumentation,
empty discovery, timeouts and unreachable properties must not look like success.
Keep inexpensive checks per change; run expensive component-specific exploration
and hardware checks on appropriate schedules. Tooling qualification is distinct
from a mutation campaign. Preserve useful counterexamples as regressions.

Local inspection found Apple Clang 17 targeting arm64 macOS and CMake 4.3.0.
Both `clang++` and `/usr/bin/g++` identify as Apple Clang, so those commands do
not provide compiler diversity. `clang-tidy` and `cppcheck` were absent from PATH;
this is not a comprehensive installed-software audit. A pinned Linux environment
plus real NVIDIA hardware is the proposed qualification base, with macOS checks
retained for development. This report records no executed C++ verification result.
