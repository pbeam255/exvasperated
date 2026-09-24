# Parallel execution, accelerators and resource ownership

First pass, 2026-09-24. Study area: `parallel`, 34 files. This is a source-level
study of execution contracts and selected backend bridges. No compiler, MPI
installation, GPU or scientific workload was tested. Backend source presence
does not establish a supported or working method/build combination.

## Reading scope and file roles

The [inventory](../vasp-source-inventory.csv) pins the files. Large Fortran files
received declaration searches and selected body reading, including accelerator
directives. The ranges below are contextual samples, not a complete audit.

| Files | Scope | Role and remaining depth |
| --- | --- | --- |
| `mpi.F` | 88-174, 209-381, 882-916, 1199-1253, 1650-1780; device and procedure searches | Communicators, host/device communication and reductions. Most wrappers and every caller's collective ordering remain open. |
| `mpi_shmem.F` | 206-273, 661-790; declaration scan | Shared allocations, aliases and collective deallocation. Lock algorithms and all ranks/shapes not audited. |
| `lib/getshmem.c` | Body scan throughout 1-233 | System V shared segments and semaphores, including local-process failure exits. |
| `shm.F` | 1-126 | Older conditional shared-workspace path; current build reachability untraced. |
| `pm.inc` | 1-29 | Historical commented declarations/instructions; no active implementation in this snapshot. |
| `offload.F` | 1-181 | Backend imports and nested offload control. |
| `offload_struct.F` | 1-19 | Shared permission, activation and device-count state. |
| `openacc.F` | 54-294, 737-758, 1574-1595; copy-helper searches | Device initialization, queues, batching and selected deep copies. Most object lifetimes remain partial. |
| `openacc_struct.F` | 1-27 | Saved queue selection and optional GPU-collective state. |
| `openmp.F` | 1-170, 247-321, 710-750, 1914-1946; copy-helper searches | Host threads, target selection and selected deep copies. Most mapping consumers remain partial. |
| `openmp_struct.F` | 1-45 | Thread controls and selected target state. |
| `nvcuda.F` | 127-207, 286-361; declaration scan including distributed eigensolver and pinned-memory entries | NVIDIA device information and numerical-library wrappers. Actual numerical calls, workspace/error contracts and distributed solvers mostly unexamined. |
| `crayhip.F` | 1-241; declaration and bridge-caller searches | AMD device information, FFT/BLAS/solver interfaces and plan metadata. Most numerical wrapper bodies remain partial. |
| `HIP/runtime_interface.cpp` | 1-18 | HIP initialization, device identity and memory queries. |
| `HIP/rocfft_interface.cpp` | 1-196 | FFT plans, layouts, workspace, streams and teardown. |
| `HIP/rocblas_interface.cpp` | 1-140, 280-344 | Enum conversion, selected BLAS/solver calls and an inactive solver wrapper. Middle wrappers remain unexamined. |
| `HIP/makefile` | 1-23 | HIP C++ support archive; external build flags remain relevant. |
| `intelmkl.F` | 115-134, 198-280; declaration scan | Additional vendor backend, unavailable memory query and selected FFT limitations. Not an added alpha-target requirement. |
| `oneapi/ze_device_get_uuid.cpp`, `oneapi/makefile` | 1-78; 1-22 | Level Zero device identity and its build archive. Runtime enumeration assumptions untested. |
| `simd.F`, `simd.inc` | 1-46; 1-58 | Conditional vector widths, types and arithmetic substitutions. Consumer alignment/tail handling untraced. |
| `lib/dclock.c`, `lib/dclock_.c`, `lib/dclock_ds20.c`, `lib/dclock_simple.c` | Body and result-assignment scans throughout | Alternative timing providers with differing interfaces and semantics; build selection untraced. |
| `lib/sclock_cray.F`, `lib/sclock_nec.F`, `lib/sclock_t3d.F` | 1-13; 1-25; 1-13 | Platform timing providers, including different relationships between elapsed and CPU time. |
| `lib/timing.c`, `lib/timing_.c`, `lib/timing_ds20.c`, `lib/timing.fujitsu.F` | Body and result-assignment scans throughout | Resource/time reporting alternatives; one provider returns unavailable status with zero results. |
| `lib/ptimers.f` | 1-95 | Older named timing/operation accumulators; external include and active selection untraced. |

## The source contains several independent execution choices

`offload.F` selects data-mapping support separately from vendor FFT, BLAS and
solver bindings. The examined NVIDIA path uses OpenACC interfaces and NVIDIA
libraries; the AMD bridge includes interfaces for both OpenMP-target and
OpenACC-style calls. The additional Intel path imports an offload library
interface. Distributed accelerator linear-algebra imports in this facade are
conditional on the NVIDIA backend. This is an observed asymmetry in the source,
not proof of the full capabilities or support status of any installed build.

The user's alpha requirement is CPU, NVIDIA GPU and AMD GPU execution. This
means later capability analysis must follow each scientific method through its
actual library calls and memory path on all three. The common facade does not
prove identical coverage. For example, the sampled Intel FFT builder rejects
batched plans and normalizes its stream choice (`intelmkl.F`, 198-269), whereas
the NVIDIA plan entry retains stream and batching distinctions
(`nvcuda.F`, 286-359). Even structurally similar interfaces need not implement
the same contract.

## Topology, threads and device assignment interact

MPI communicator records contain rank identity, size and IO ownership; the
wrapper converts ranks to an internal one-based convention (`mpi.F`, 104-115,
233-242). Cartesian subdivision and unequal-group subdivision take different
paths (271-372). A communicator can be absent on some ranks in the latter path.
This matters to consumers that might otherwise assume every rank participates
in every nested communicator.

The OpenMP build asks MPI for single-thread support in the sampled initializer
(`mpi.F`, 217-227), while host thread initialization limits active nesting and
sets separate thread counts for selected kernels (`openmp.F`, 42-81). This
identifies a calling-context obligation. It does not establish that any caller
actually violates the requested MPI thread level; parallel-region and MPI-call
placement need tracing together.

The OpenACC host-device choice can disable offload. Its NVIDIA device assignment
uses rank-based indexing, then gathers device identity information to determine
sharing (`openacc.F`, 54-140). The OpenMP target path collectively checks that
all ranks have devices and otherwise disables offload (88-147). Launch-time
visibility, rank ordering and node topology therefore affect effective placement.
No placement or fallback was reproduced on hardware.

Optional NVIDIA collectives are initialized per relevant communicator; a later
combined decision can disable their use when initialization is unsuitable
(`mpi.F`, 882-916; `openacc.F`, 115-131). A startup message about detected devices
would not by itself demonstrate which communication transport a calculation uses.

## Activation, residency and completion are distinct states

The offload controller stores permission and current activation separately and
uses a bounded saved stack for temporary changes (`offload.F`, 102-145).
Both stack operations issue an OpenACC wait before changing state (123, 139),
so they synchronize OpenACC work when those directives are active. They do not
explicitly transfer data, and those directives alone establish no corresponding
OpenMP-target wait. Balanced push/pop and valid residency remain caller
obligations; the saved state also warrants a thread-context audit.

The OpenACC wavefunction copy path transfers a parent object and selected
arrays, recursively maps its descriptor, and attaches the descriptor pointer
(`openacc.F`, 737-758). Its copyout path copies selected arrays back while deleting
others and detaching nested state (1574-1595). These operations use the current
asynchronous queue. The OpenMP counterparts express mapping and release rules
explicitly, with an additional pointer-mapping branch (716-748, 1914-1946);
the sampled projector mappings show related handling at 247-321.
Neither implementation is a general automatic traversal of every field.

This yields a concrete reconstruction hazard: adding or aliasing a scientific
field requires understanding its ownership, mapping and update direction. A
successful allocation or pointer-presence query cannot show that the copy
contains the latest data. The foundations study's aliased real/complex views
and reusable buffers make this more consequential.

Queue helpers wait for all queues, selected ranges or masks; an alternative
build path calls runtime synchronization directly (`openacc.F`, 183-253).
The memory-based batch estimate is conservative and only attempts a free-memory
query when a device is not shared by multiple ranks (260-287). Actual live
workspace and concurrent allocation can still change the usable capacity.

## Communication changes with memory location

The sampled real send wrapper chooses among host MPI, a device-pointer MPI path,
and optional GPU collectives (`mpi.F`, 1199-1248). The OpenACC MPI branch waits
for the selected queue before sending device storage; the GPU-collective branch
uses a stream and returns. The sampled sum wrapper also includes an explicit
wait around its GPU-collective path (1660-1737). Completion behavior must be
checked per operation rather than inferred from the wrapper family.

The NVIDIA startup checks MPI device support through a runtime query and selected
environment overrides (`nvcuda.F`, 155-194). A Cray MPI build branch instead
starts from an assumption of support before applying those environment checks.
The corresponding AMD helper shown
at `crayhip.F` 140-142 immediately returns. This is an asymmetry in checks, not
evidence that AMD device MPI is absent or broken. The OpenMP communication branch
still passes device pointers; correctness depends on the configured runtime and
the caller's mapping/completion contract.

Reduction routines bind working values to explicit MPI datatypes. Their agreement
with compiler kinds and external ABI belongs with the foundations study. Reduction
order and decomposition can also alter rounding; downstream convergence and
physical observables, rather than assumed bitwise identity, will determine the
necessary comparisons. No reproducibility tolerance is selected in this pass.

## Shared host memory has collective lifetime requirements

The sampled shared allocator records its communicator, brackets allocation with
barriers and returns an alias (`mpi_shmem.F`, 206-252). With multiple ranks, one
rank supplies storage and other ranks query it in the MPI shared-window path;
the alternative System V path distributes a segment identifier, attaches it and
marks it for removal after attachment (661-727). Single-rank storage follows a
normal allocation path.

Deallocation includes collective synchronization and window cleanup, then clears
stored associations (741-767). Thus a shared buffer's lifetime cannot be decided
independently by arbitrary consumers. The C System V helpers contain direct
process exits on errors (`lib/getshmem.c`), introducing a failure path outside
the coordinated Fortran shutdown discussed in the execution study. The effect
on peer ranks and outstanding operations is unresolved.

## Concrete backend concerns for later verification

These findings concern the inspected source, not observed calculation failures:

1. **AMD device identity:** `HIP/runtime_interface.cpp` 8-12 assigns a local
   pointer to the temporary device identifier instead of copying bytes into
   caller storage. The Fortran callers at `crayhip.F` 37-113 then consume their
   destination arrays to count devices and rank sharing. As written, the bridge
   does not supply those bytes. Actual builds and effects on placement/reporting
   need a bounded probe; the device-count conclusions cannot be trusted merely
   because the interface is present.
2. **FFT workspace and assertions:** in `HIP/rocfft_interface.cpp` 103-104,
   169-170 and 188, allocation/free calls occur inside assertions. A build that
   disables standard assertions would remove those side effects. The file's
   makefile inherits external flags, so this pass does not claim the distributed
   build actually disables them. The bridge also terminates the local process
   on checked FFT-library errors, requiring a distributed failure review.
3. **Uneven error and capability handling:** sampled BLAS calls do not propagate
   their library return status through the bridge. Solver calls can additionally
   expose numerical status through an output argument; those are different
   channels. One Jacobi-style generalized eigensolver wrapper has no active
   solver call (`HIP/rocblas_interface.cpp`, 309-316). A targeted search found
   no reference to that wrapper name in `crayhip.F`; reachability must precede
   any claim about a broken scientific method.

These observations support evaluating explicit errors, complete numerical
contracts and resource ownership during later design. They do not justify copying
the reference bridge or reproducing an apparent defect for compatibility.

## Performance evidence needs its own interpretation

The bundled timing alternatives do not all report the same quantity. Some pair
CPU accounting with wall-clock time; the simplest provider returns CPU time in
both outputs. One historical variant applies an extra scale factor, while a
platform resource provider reports unavailable data. SIMD choices also change
logical vector widths and arithmetic bindings. Build selection and active
consumers remain open. Neither source size nor a printed timing label establishes
comparable CPU/GPU performance.

## Return conditions

Return with representation for grid/wavefunction ownership, plan invalidation,
strides, normalization and asynchronous lifetime. Return with numerical consumers
for solver status, workspace and unsupported combinations. Return with IO and
execution for host visibility before output and coordinated failure. The later
reference campaign should resolve the concrete bridge concerns and exercise
actual CPU/NVIDIA/AMD workloads under different rank/device layouts. This report
does not select a portability framework, promise vendor parity, or launch those
experiments.

## Review disposition

The [single independent review](reviews/parallel.md) found a warranted correction
to activation-stack synchronization: both operations include OpenACC waits.
The report now states that behavior, corrects the OpenMP wavefunction copy-in
reference, and records the Cray MPI query exception. The cited source was checked
and all three findings addressed. No second review round was requested.
