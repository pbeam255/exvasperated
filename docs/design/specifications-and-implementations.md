# Specifications, implementations and verification work

Part of [design draft 0.2](README.md). The durable technical work includes the
scientific specifications and the tests challenging them. Their size may exceed
the numerical implementations. This organization remains language-neutral and
introduces no certification objects, ADRs or review authority hierarchy.

## 1. What accompanies a calculation operation

The focused expedition precedes its detailed implementation. Develop two views:
the physics and its assumptions, and the mathematical problem apart from the
physical interpretation. Compare them to find hidden premises and useful work in
other fields. Neither view automatically validates the other.

For a concrete operation, develop the following together:

| Material | Content |
| --- | --- |
| Physical account | Model, observables, assumptions, regimes, path/branch preparation and limits |
| Mathematical account | Equations, spaces, operators, boundary conditions and existence/uniqueness issues |
| Numerical account | Discretization, conditioning, approximation, stopping rules, precision and error distinctions |
| Interface | Inputs/results, units, representation, ownership, layout, workspace, completion and failure |
| Composition | Call order, child state, trial/accepted state, history and continuation prerequisites |
| Executable challenges | Independent cases, properties, adversarial inputs, reference comparisons and meaningful failure witnesses |
| Implementations | Clear reference, optimized candidates and associated build/runtime adapters as justified |

This is the content needed to understand an operation, not mandatory files or a
form to complete. Keep open questions explicit. A spec can be wrong; disagreement
between a test, derivation and implementation is an investigation, not automatic
permission to edit expected values until green.

## 2. A bounded implementation zoo

Keep the scientific operation stable enough to compare alternatives, while
allowing each implementation to state its supported domain, layout and resource
requirements. A common adapter must preserve scientific meaning and ownership;
it must not hide conversions, synchronization or unsupported cases.

Retain useful source and knowledge without maintaining every candidate as an
active backend. A contest asks a named question and has a bounded set of entrants
and workloads. Compare accuracy, robustness, memory and time to accepted result.
First use controlled comparisons to isolate a language/backend question; separately
compare the strongest complete implementations, including integration costs.

Every numerical library is on trial before adoption, regardless of pedigree.
Our own implementations remain eligible for some or all operations. Selection may
differ by operation, physical/numerical regime and target hardware; a library
winning one comparison does not win unrelated operations by association.

Generated code, symbolic specialization, Fortran, Futhark and targeted assembly
remain candidates where their benefits justify their boundaries. No language or
library is selected by this organization. The no-OOP rule applies to our code.
CPU and NVIDIA are alpha requirements, AMD later; implementations may specialize
for hardware without fragmenting the scientific meaning of their results.

## 3. Oracle independence

Study historical implementations, their difficult test cases and benchmark
designs. Record enough source/version information to revisit a finding. Inspect
reuse terms before importing fixtures or code; VASP material stays quarantined.

Check independence at the level of formulation, algorithms, expected-data origin,
compiler, numerical libraries and generators. Different repositories or languages
can still share the same defect. A high-precision run of the same mistaken formula
does not resolve a mathematical disagreement. Use analytic limits, independently
derived finite cases, residuals, derivative relations and comparisons where their
premises actually apply.

Construct adversarial domains deliberately and retain useful counterexamples.
Test histories, method combinations and failure paths as well as individual
numbers. A property needs its domain: no assumed branch uniqueness, universal
energy monotonicity or equivalence of differently prepared states. A persisted
point restores recorded state; future trajectories need not be deterministic.

## 4. Teeth tests for the core

These are proposed test shapes, not tests already written or demonstrated red:

| Prescription | Relevant red witness | Adherence that should make it green |
| --- | --- | --- |
| Interface-only composition | A consumer can access private state despite the intended boundary | Public operations work; private access is rejected for the right reason |
| No premature reuse | A delayed operation still reads an allocation after it is made reusable | Owner survives to actual completion, including failure paths |
| Checked shape arithmetic | A supported boundary case overflows an offset or allocation size | Correct computation or explicit rejection before access/allocation |
| Explicit full-capacity behavior | Work is lost or required state is overwritten at capacity | Declared backpressure, failure or method-supported action |
| No accidental allocation/copy | The exercised operation exceeds its specified allocation/movement behavior | The implementation meets its concrete resource requirement |
| Recorded-state preservation | Saving/branching mutates prior recorded values or loses a required dependency | Earlier points remain restorable under the stated storage model |
| Automated required checks | Relevant workflow proceeds although a required check fails or never runs | Its trigger executes the check and handles failure explicitly |
| Bounded review cycle | Orchestration automatically launches another check after straggler fixes | It stops and waits for explicit operator approval |

For compile-fail tests, a rejected misuse must fail for the intended reason;
an unrelated syntax or link failure is not a successful demonstration. For
runtime tests, retain actual assertions about behavior. Empty discovery, skipped
checks and a timeout are not passing results. Resource tests need a stated
operation, input regime and measurement method; no literal global zero-waste
promise follows from the design stance.

## 5. Executable development workflow

Implementation proceeds in planned tranches: substantive tests red, code, tests
green, adversarial review, fix all, one subagent validation, fix stragglers, STOP.
Report remaining work. No second review/checking cycle without explicit operator
approval; do not evade the limit by changing reviewers or relabelling work.

When establishing the build workflow, connect checks to the actual operation
that needs them. Initialization should configure or verify its necessary test
machinery; invoking the relevant change workflow should run its required checks.
Dependency/build visibility should reject unsupported private access. Return
failures through the workflow rather than asking a person or model to remember
follow-up commands. The exact commands and infrastructure remain unimplemented.

Substantive checks run under explicit scopes and budgets. This prevents a finite
test suite from silently becoming an unbounded fuzz/mutation campaign. Existing
restrictions on mutation campaigns remain. Tools that require the JVM run only
under the narrow verification exception, in minimal disposable containers with
programmatic teardown on success, failure and interruption. Test that cleanup
when building the launcher; do not require a cleanup reminder.

The automation has operational states such as executing, failed or awaiting the
operator's next instruction. It does not issue certificates, maintain an authority
registry or turn a reviewer's opinion into a scientific fact. Hypotheses and good
intentions that lack meaningful red witnesses remain plainly described as such.
