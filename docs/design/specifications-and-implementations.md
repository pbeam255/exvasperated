# Specifications, implementations and verification work

Part of [design draft 0.2](README.md). The specifications and tests may be larger
than the numerical code they describe. They are central to the project. This
proposal leaves implementation languages open.

## 1. What accompanies a calculation operation

Study each subsystem before designing and implementing its routines. Describe
both the physics, with its assumptions, and the mathematical problem without its
physical interpretation. Comparing these views can reveal hidden assumptions
and useful methods from other fields. Neither account establishes that the other
is correct.

For each operation, develop the following together:

| Topic | What to explain |
| --- | --- |
| Physics | Model, measured quantities, assumptions, applicable conditions, preparation of branches and limits |
| Mathematics | Equations, spaces, operators, boundary conditions, and whether solutions exist or are unique |
| Numerical method | Discretization, conditioning, approximations, stopping rules, precision and sources of error |
| Interface | Inputs and results, units, representation, buffer ownership, layout, workspace, completion and failures |
| Use with other routines | Call order, child sessions, trial and accepted values, history and requirements for continuation |
| Tests | Independent cases, properties, adversarial inputs, reference comparisons and examples that expose errors |
| Implementations | A clear reference implementation, optimized alternatives and the adapters each needs, where useful |

These topics need answers, not a mandatory set of files or a form. Record open
questions. A spec can be wrong. When a test, derivation and implementation disagree,
investigate the disagreement before changing expected values.

## 2. A bounded implementation zoo

Give alternatives the same problem and required behavior, while allowing each
to state its supported inputs, layouts and resource needs. Adapters must preserve
what the data means and who may change or release it. Expose conversions,
synchronization and unsupported cases.

Keep useful source and findings without maintaining every candidate as an active
backend. Each comparison should answer a named question with a bounded set of
implementations and workloads. Measure accuracy, robustness, memory use and time
to a result that meets the stated criteria. Use matched implementations to isolate
a language or backend difference. Also compare the best complete implementations,
including their integration costs.

Every numerical library is on trial before adoption, regardless of pedigree.
We may write some or all operations ourselves. Choices can differ by operation,
input conditions and hardware. A library winning one comparison does not win
unrelated operations.

Generated code, symbolic specialization, Fortran, Futhark and targeted assembly
remain candidates where the benefits justify integration and maintenance. No
language or library is selected here. Our code uses no OOP. CPU and NVIDIA are
alpha requirements, AMD later. Implementations may specialize for hardware while
preserving the operation's defined inputs and results.

## 3. Oracle independence

Study historical implementations, difficult test cases and benchmark designs.
Record enough source and version information to revisit findings. Check reuse
terms before importing fixtures or code; VASP material stays quarantined.

An oracle is a reference used to judge a result. Check whether our test references
share formulations, algorithms, expected-data sources, compilers, libraries or
code generators. Different repositories and languages can share the same defect.
Higher precision does not fix a mistaken formula. Use analytic limits,
independently derived finite cases, residuals, derivative relations and other
comparisons where their assumptions hold.

Build difficult inputs deliberately and retain useful counterexamples. Test
histories, combinations of methods and failure paths as well as individual
numbers. State where each property holds: do not assume a unique branch,
universally decreasing energy or equivalence of differently prepared states.
Restoring saved values does not promise deterministic future trajectories.

## 4. Teeth tests for the core

These are proposed tests. They have not been written or demonstrated red:

| Rule | A failure the test must expose | What should make it pass |
| --- | --- | --- |
| Use public interfaces | A caller can access data intended to be private | Public calls work; private access is rejected for the intended reason |
| Keep buffers until work finishes | Delayed work reads a buffer after it becomes reusable | Retain the buffer until completion, including failure paths |
| Check shape arithmetic | A supported boundary case overflows an offset or allocation size | Compute correctly or reject before allocation/access |
| Define behavior at capacity | A full queue loses work or overwrites required state | Wait, fail or take an action explicitly supported by the method |
| Meet allocation/copy limits | An operation exceeds its specified allocation or movement limit | Stay within the limit for the stated inputs |
| Preserve saved state | Saving or branching changes old values or loses required data | Earlier points remain restorable under the stated storage assumptions |
| Trigger required checks automatically | Work proceeds when a required check fails or never runs | Run the check at its trigger and handle failure |
| Stop the review cycle | Automation launches another check after straggler fixes | Stop and await explicit operator approval |

A compile-fail test must fail for the intended misuse, not an unrelated syntax
or linker error. Runtime tests must assert actual behavior. Finding no tests,
skipping them or timing out is not a pass. Resource tests need a named operation,
input range and measurement method. We do not promise literally zero wasted
bytes or cycles everywhere.

## 5. Executable development workflow

Work in planned sections: substantive tests red, code, tests green, adversarial
review, fix all, one subagent validation, fix stragglers, STOP. Report remaining
work. A second review/checking cycle requires explicit operator approval. Changing
reviewers or renaming the work does not reset that limit.

Connect each required check to the operation that needs it. Initialization should
set up or check its test tools. The relevant change workflow should run its checks
and return failures, without depending on someone remembering a command. Build
visibility should reject private access. These commands and automation have not
yet been implemented.

Set scopes and budgets for checks so a finite test run cannot grow into an
unbounded fuzzing or mutation campaign. Existing mutation-campaign restrictions
remain. A necessary verifier requiring the JVM is permitted only under the narrow
exception: a minimal disposable container torn down programmatically on success,
failure and interruption. Test that cleanup when building its launcher.

The automation runs work, reports failures and stops when it needs the operator's
next instruction. It does not issue certificates or create an authority registry.
A rule without a meaningful demonstrated failure remains a good intention.
