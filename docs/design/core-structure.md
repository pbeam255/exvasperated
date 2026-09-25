# Core structure, interfaces and memory

Part of [design draft 0.2](README.md). This refines the application core using
the established project tenets. Names below describe responsibilities and data,
not a chosen language, class hierarchy, package count or deployment topology.
No implementation or demonstrated teeth tests are introduced by this document.

## 1. Component boundaries

Each component owns its private state and exposes operations with declared input,
output, ownership and failure behavior. A public view is deliberately supplied
data; it is not permission to inspect private layouts. Calls can be direct and
in-process. Interface separation does not imply copying, serialization, RPC or
per-element dynamic dispatch.

| Component | Owns or interprets | Public operations | What its consumers do not inspect |
| --- | --- | --- | --- |
| Input dialect | Syntax, locations, precedence and public compatibility rules | Parse and resolve to a calculation request | Parser storage or private configuration maps |
| Application | Selected procedure, process lifecycle and delivery policy | Inspect, prepare, run, stop, return outcome | No scientific algorithm is reconstructed from a driver's internals |
| Scientific family | Its model/representation, working state and history semantics | Construct, evaluate, transform, continue, expose specified results/state | Private caches, iteration vectors, branch-history implementation |
| Method composition | Selected child calculations and scientifically defined ordering | Execute the concrete procedure; expose coherent boundaries | Children are accessed only through their scientific operations |
| Numerical/backend adapter | Allocation mechanism, kernel/library implementation, completion mechanism | Specific numerical operations, movement, completion and resource release | Vendor contexts, raw allocation internals, library-private handles |
| History and storage | Recorded entries, ancestry, payload dependencies and publication | Append, list, inspect, restore, branch and export | Physical schema, filenames and backend transaction machinery |
| Result/compatibility writer | Requested external format | Consume public result/record views and write outputs | Driver memory, private history schema or another writer's files |

These are dependency directions. A scientific family need not know a database
schema; a storage adapter need not understand how to advance its scientific method.
Family-owned encoders/decoders expose the intended recorded representation.
Debugging and research can inspect source; running systems must not use private
implementation knowledge as their integration interface.

Public build targets expose only intended headers/modules. Backend-specific
details stay private to their adapters. Proposed teeth: a consumer attempting to
access an internal representation fails for that reason, while its public use
works. A directory convention alone cannot establish this boundary.

## 2. Composition through data and operations

Use product types for simultaneously present data and sum types for actual
alternatives. Each alternative carries its own necessary data. Avoid unrelated
booleans admitting nonsensical combinations, inheritance trees, universal base
classes and mutable dictionaries of every possible scientific option.

Illustrative distinctions, to refine with each method:

```text
Initialization = Fresh(inputs)
               | Continue(recorded_point, permitted_controls)
               | InitializeFrom(source, selected_quantities, transformation)

Delivery = Written(location)
         | Failed(cause)
         | Uncertain(operation_identity)
```

The second sum belongs to an operation that can actually have an uncertain
external outcome. It is not a universal status field. Method outcomes retain
their own vocabulary: an integration interval completing and an SCF stopping
criterion being met remain distinct facts.

The application resolves the chosen driver once at a suitable boundary. The
driver is ordinary scientific control flow invoking family operations. Stable
small alternatives can use static dispatch; runtime choices can dispatch once
per substantial operation. Layout and specialization decisions must not cause a
combinatorial explosion of compiled variants without measured benefit.

Scientific composition is explicit in the selected method. A nuclear integrator
requests force evaluations at its defined stages; a force operation returns its
result and updated electronic session. The parent does not extract and edit the
child's mixer arrays. Child state needed for continuation is obtained through the
child's record operation and included at a coherent composite boundary.

A proposed input combination can be unavailable. Unsupported composition is an
explicit construction result, never an excuse to silently select a different
physical approximation. Experiment interpretation and suggestions remain outside
this core. Detailed numerical control and branch semantics remain subjects of the
focused scientific expeditions.

## 3. Ownership and asynchronous execution

The method owns its scientific state. Owning values retain their allocations;
the backend supplies the correct allocation/release operations. Submitting work
transfers the affected owners into the pending operation while storage stays
resident. Completion yields the resulting owned values. This requires no central
lease office or global mutable table of resource validity.

Illustrative operation shape, not an ABI or a generic task framework:

```text
submit(inputs, destination, workspace, selected_operation)
    -> NotSubmitted(cause, returned_owners)
     | Pending(owned_resources, completion)

finish(pending)
    -> Completed(results, reusable_resources)
     | Failed(cause, resources_with_known_safe_disposition)
```

`NotSubmitted` requires knowing no work can access the resources. If launch may
have happened, event recording fails, or completion cannot be established, the
adapter must retain the resources in an unresolved/failed execution context until
safe teardown. It cannot return them as reusable through either branch above.
The concrete backend must represent that case explicitly; these sketches are not
a complete failure-state enumeration. Dropping a handle or requesting cancellation
does not establish that a device or MPI operation has stopped accessing memory.

Shared immutable inputs and scoped views are available for actual computational
needs. Their lifetime must cover every use, including foreign calls. Explicit
resource ownership may move while read-only data remains shared; mutable aliases
require a defined disjointness or synchronization argument. A view carries no
right to outlive its owner or free a foreign allocation.

Separate reusable storage from valid cached numerical values. Reusing an
allocation does not authorize reusing its prior contents after geometry, basis or
model changes. A method defines those changes through operations on its own state.

## 4. Layout is part of each numerical operation

An operation specification includes both scientific representation and physical
storage requirements:

| Aspect | Questions to settle |
| --- | --- |
| Meaning | Basis/grid, units, normalization, component ordering and scientific stage |
| Indexing | Logical extents, partition map, strides, checked offset/size arithmetic |
| Placement | Host/device location and accessibility, alignment, intended locality |
| Access | Read-only inputs, mutation, permitted overlap and aliasing, completion |
| Resources | Persistent bytes, scratch, packing/staging, pending output, bounded concurrency |
| Numerical behavior | Precision, reductions, exceptional inputs, failure result and tolerance model |

The representation constructor establishes the necessary associations once where
possible. Inner loops receive data suitable for their work. Equal dimensions
alone do not establish equal bases. No-alias/alignment assumptions supplied to a
compiler must follow from actual construction and ownership.

Choose contiguous arrays, AoS/SoA, blocking, tiling, arenas, rings or other layouts
from access patterns and measurements. A ring is useful only where its lifetime
and access pattern fit. Its capacity and overwrite behavior must never silently
discard required scientific history. Padding, duplicated small data or packing
can improve total throughput; count their full cost instead of minimizing each
local byte count independently.

Plan peak simultaneous resources, not just final arrays. Include trial/accepted
states, child workspaces, communication staging and snapshots where those coexist.
Bound work in flight and handle a full queue explicitly. Required output can
apply backpressure; optional progress may be coalesced according to its declared
policy. Neither overflow nor out-of-memory licenses lowering precision, changing
the physical model or silently reducing required output.

Keep control/metadata work outside numerical inner loops where the selected
algorithm allows it. CPU and GPU may use different layouts and routines under
the same scientific operation. A conversion or transfer is an explicit operation
with a measured cost, not a hidden consequence of a language boundary.

## 5. Storage responsibilities without premature deployment choices

The database tenet generalizes to reusing strong existing implementations before
rebuilding their machinery. Transactions, integrity constraints, indexing,
queries, codecs and array containers deserve that presumption. Determine the
needed behavior before selecting which mature component supplies it.

Numerical libraries are explicitly on trial before adoption. Existing libraries,
our own routines and generated/specialized kernels must face the scientific spec,
independent tests and resource measurements. We may write some or all numerics;
infrastructure reuse does not predetermine those choices.

The core currently needs these history operations:

- Append a method record and its required payload references at a coherent point.
- Distinguish publication, durable acknowledgement and uncertain outcomes.
- Select a point or branch unambiguously; preserve recorded future branches.
- Restore the recorded values and retained history without rerunning science.
- Inspect observations even when continuation state is unavailable.
- Export the selected records and required dependencies with explicit omissions.

These needs do not select a DB engine, SQL schema, storage service, filesystem,
writer topology or array container. They do not require all numerical arrays to
be database rows or require an independent catalog service. Live numerical state
remains method-owned memory; persistence uses the method's exposed record.

Study storage options against the actual requirements later. Delegate the work
the selected DB does well, through the storage interface. If metadata and array
payloads use separate stores, their publication/failure relationship is a real
design obligation: a metadata transaction alone does not establish persistence
of external payloads. Avoid custom transaction/indexing machinery merely because
the prototype file layout already contains it.

Earlier HDF5/shard and filesystem-publication sketches in
[results](results-and-continuation.md) and [history](calculation-history.md) are
concrete candidates for reasoning, not selected deployment requirements. The
existing Python explorer addresses that specific abstract protocol; it does not
verify an eventual database-backed implementation. Linux-first development and
CPU/NVIDIA alpha support do not prescribe where researchers store their data.

## 6. Reuse and substitution

An implementation boundary names a scientific or infrastructural operation, its
data and its behavior. It does not promise that every library is interchangeable.
For a numerical replacement, compare domains, precision, error/failure behavior,
layout, workspace and asynchronous lifetime as well as runtime. For a storage
replacement, compare the restoration and publication behavior the caller uses.

Keep the operation interface as narrow as the real responsibility permits. The
first working implementation can be direct; multiple actual implementations can
motivate further factoring. No universal plugin registry, service locator,
scalar-level tensor interface or dependency-injection framework is required.
The [specification and implementation organization](specifications-and-implementations.md)
describes how alternatives face the same external questions.
