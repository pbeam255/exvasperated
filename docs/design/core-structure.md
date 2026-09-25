# Core structure, interfaces and memory

Part of [design draft 0.2](README.md). This describes the proposed components,
what data they keep, and how they call each other. Language, package boundaries
and deployment remain open. The tests described here have not been implemented.

## 1. Component boundaries

A component exposes operations and selected views of its data. Callers use those
interfaces; they do not read its private fields or storage. Each operation states
what it accepts, what it returns, who can change or release the data, and how it
can fail. Calls can pass existing arrays directly within one process.

| Component | Responsible for | Public operations | Private details |
| --- | --- | --- | --- |
| Input adapter | Syntax, source locations, defaults and compatibility rules | Parse and resolve a calculation request | Parser storage and configuration maps |
| Application | Selected procedure, startup, shutdown and required outputs | Inspect, prepare, run, stop, return outcome | Launch and output coordination |
| Calculation module | A group of related routines, such as electronic solvers; their data and history | Construct, evaluate, transform, continue, read results, save state | Caches, iteration vectors and history storage |
| Method driver | The loop that calls routines in the order required by the selected method | Run the procedure, stop or save at supported stages | Loop bookkeeping and child-session storage |
| Numerical/backend adapter | Allocations, kernels, library calls and completion | Compute, move data, wait for completion, release resources | Vendor contexts, allocation internals and library handles |
| History and storage | Saved entries, parent links, array blocks and publication | Append, list, inspect, restore, branch and export | Schema, filenames and transactions |
| Result/compatibility writer | A requested output format | Write from public result or saved-state views | Formatting and writer buffers |

The electronic solver need not know a database schema. The storage adapter need
not know how to advance an SCF iteration. Each calculation module defines the
values its encoder saves and its decoder restores. A writer receives those values
through the module's interface; it does not dig through the solver's memory.
Source inspection remains part of debugging and research.

Build targets should expose only the intended headers/modules. A proposed teeth
test would compile a caller using the public interface and reject one reaching
into private data. The rejection must be caused by that access. Putting files in
a directory named “private” is insufficient.

## 2. Composition through data and operations

Use product types to group fields that belong together and sum types for
alternatives. Each alternative carries the data it needs. Avoid collections of
booleans that permit impossible combinations, inheritance trees, universal base
classes and mutable dictionaries containing every calculation option.

Illustrative distinctions, to refine with each method:

```text
Initialization = Fresh(inputs)
               | Continue(recorded_point, permitted_controls)
               | InitializeFrom(source, selected_quantities, transformation)

Delivery = Written(location)
         | Failed(cause)
         | Uncertain(operation_identity)
```

Use `Uncertain` when the caller cannot establish whether an operation succeeded:
for example, when a reply is lost or storage synchronization fails after data
becomes visible. Include it only where such uncertainty can occur. Calculation
outcomes also need specific names: completing a requested time interval and
meeting an SCF stopping criterion are different results.

The application selects a driver during setup. That driver is an ordinary loop
calling calculation routines. Small, stable choices can be resolved at compile
time; runtime choices can be resolved once per substantial operation. Specialize
layouts and kernels where measurements justify the added compiled variants.

For example, a nuclear integrator requests forces at specified stages. The force
routine returns the forces and the updated electronic session used to calculate
them. The integrator calls that session's operations; it does not edit the
session's mixer arrays. When saving, it asks the session for its record and saves
it with the matching positions, momenta and integrator stage.

Reject unsupported combinations during construction. Do not silently select a
different physical approximation. Experiment interpretation and suggestions
remain outside this core. Detailed solver controls and treatment of branches
still require focused study of each method.

## 3. Ownership and asynchronous execution

An SCF loop keeps its orbitals, density and mixing history between calls. A
molecular-dynamics loop keeps positions, momenta and integrator history. Their
operations control updates to those values. Each buffer has an owner responsible
for keeping its allocation alive and eventually releasing it through the correct
backend operation.

When a routine submits GPU or MPI work, it hands the affected buffer owners to
the pending operation. The bytes stay where they are. Once the work finishes,
the caller gets the results and reusable buffers back. There is no central lease
registry.

Illustrative operation shape, not a final ABI or task framework:

```text
submit(inputs, destination, workspace, selected_operation)
    -> NotSubmitted(cause, returned_owners)
     | Pending(owned_resources, completion)

finish(pending)
    -> Completed(results, reusable_resources)
     | Failed(cause, resources_with_known_safe_disposition)
```

`NotSubmitted` means submission was rejected before work could use the buffers.
Work that ran, even partly, follows the completion/failure path regardless of
whether its buffers are now safe to release. If launch may have happened,
recording a completion event fails, or completion cannot be confirmed,
the adapter keeps the resources until it can safely tear down the execution
context. It must not return them as reusable. The final API needs an explicit
case for this; the sketch above is incomplete. Cancelling work or dropping a
handle does not establish that a device or MPI operation has stopped using memory.

Read-only inputs can be shared, and routines can receive temporary views into
existing arrays. Those arrays must stay alive for every use, including foreign
calls. Multiple mutable views require either disjoint regions or explicit
synchronization. A view cannot outlive its owner or free a foreign allocation.

Reusable storage and reusable values are different. After a geometry, basis or
model change, an allocation may still fit while its cached projector values are
stale. The calculation module's update operations decide which values to rebuild.

## 4. Layout is part of each numerical operation

Specify what an array represents and how the routine accesses its storage:

| Aspect | Questions to settle |
| --- | --- |
| Meaning | Basis/grid, units, normalization, component order and calculation stage |
| Indexing | Dimensions, partition map, strides, checked offset/size arithmetic |
| Placement | Host/device location and accessibility, alignment and locality |
| Access | Read-only inputs, mutation, permitted overlap and completion |
| Resources | Persistent storage, scratch, packing/staging, pending output and maximum concurrent work |
| Numerical behavior | Precision, reductions, exceptional inputs, failures and error tolerances |

Constructors should check associations such as an array's basis once where
possible, so inner loops receive suitable data. Equal dimensions do not mean
equal bases. Compiler assumptions about alignment or non-overlapping pointers
must hold for the actual allocations and calls.

Choose contiguous arrays, arrays of structures or structures of arrays, tiles,
arenas, rings and other layouts from access patterns and measurements. A ring
fits some workloads; overwriting it must never silently discard required history.
Padding, duplicated small data or packing can improve total throughput. Measure
their total cost.

Budget peak simultaneous memory: trial and accepted states, child workspaces,
communication buffers and snapshots may all coexist. Limit work in flight and
specify what happens when a queue fills. Required output can make the calculation
wait; optional progress messages may be combined under a stated policy. Neither
a full queue nor exhausted memory permits silently lowering precision, changing
the model or dropping required output.

Keep bookkeeping outside numerical inner loops where the algorithm allows it.
CPU and GPU implementations may use different layouts for the same operation.
Make conversions and transfers explicit and measure their cost, including those
at language boundaries.

## 5. Storage responsibilities without premature deployment choices

Before rebuilding transactions, constraints, indexes, queries, codecs or array
containers, investigate mature implementations. Establish what we need and use
the component that does it well.

Numerical libraries still go on trial. Compare existing libraries, our own
routines and generated kernels against the operation's specification, independent
tests and resource requirements. We may write some or all of the numerics.

The core currently needs these history operations:

- Save the method's values and required array references at a supported stage.
- Distinguish data being visible to readers from a save confirmed as durable,
  and represent cases where the writer cannot tell whether a save succeeded.
- Select a saved point or branch without ambiguity; preserve existing branches.
- Restore saved values and retained history without rerunning the calculation.
- Inspect observations even when the saved data cannot support continuation.
- Export selected records and their required data, stating any omissions.

These operations leave the database, schema, service, filesystem, number of
writers and array container open. Arrays need not become database rows, and a
separate catalog service is not required. Running calculations keep their working
arrays in memory; storage receives the records the calculation modules expose.

Evaluate storage options against these needs. Use the selected database through
the storage interface. If metadata and arrays live in separate stores, specify
how they are published and recovered together. A metadata transaction does not
make external arrays durable. The prototype file layout is no reason to commit
to custom transaction or indexing code.

The HDF5/shard and filesystem sketches in [results](results-and-continuation.md)
and [history](calculation-history.md) remain candidates. The Python explorer
examines that abstract file protocol; it does not test a future database
implementation. Linux development and CPU/NVIDIA support do not prescribe where
researchers store data.

## 6. Reuse and substitution

An interface defines an operation, its data and its behavior. Before replacing a
numerical implementation, compare supported inputs, precision, errors, failures,
layout, workspace and asynchronous lifetimes as well as speed. Before replacing
storage, compare the save and restore behavior callers rely on.

Keep interfaces specific to their job. Start with a direct implementation and
factor out shared code when actual alternatives show what is shared. No universal
plugin registry, service locator, scalar-level tensor interface or dependency-
injection framework is required. See [specifications and implementations](specifications-and-implementations.md)
for how we compare alternatives.
