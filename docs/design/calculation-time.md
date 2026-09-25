# Positions, iterations and time

Part of [design draft 0.2](README.md). This explains what the loops advance and
why a single `step` or `time` field would hide important differences. The examples
explain the proposed interfaces; they do not select an integrator or settle the
detailed design of any numerical subsystem.

## 1. What has a position?

In an ordinary electronic ground-state calculation, the input includes a cell
and the positions of the nuclei, often called ionic positions. Those positions
define the geometry at which the electrons are solved. Electrons are represented
through orbitals, occupations and density, rather than a classical list of
individual electron coordinates and velocities. Orbital coefficients and density
values can change during a solve while the nuclear positions stay fixed.
See the public [VASP theory overview](https://vasp.at/wiki/Category:Theory).

The same geometry can be used in several different procedures:

| Procedure | What changes | Does that change represent physical time? |
| --- | --- | --- |
| Electronic self-consistency at fixed geometry | Estimates of orbitals, density, occupations and solver history | No; iterations seek a solution for the specified geometry |
| Geometry optimization | Trial nuclear positions and possibly the cell, with new electronic evaluations | No; accepted and rejected search steps seek a structure |
| Born–Oppenheimer molecular dynamics | Nuclear positions and momenta, using forces from electronic calculations | Yes; an integrator approximates the selected equations of motion |
| Real-time electronic propagation | Electronic amplitudes/density and any coupled degrees of freedom | Yes; time is an argument of the evolution equations |
| Sampling, path methods or finite displacements | Samples, path images or perturbed geometries | Not automatically; an index or displacement is not elapsed physical time |

VASP's public input documentation itself distinguishes a molecular-dynamics time
step from an optimization step width and a finite-displacement length, even though
one input name is reused for them. Our internal interfaces should keep those
meanings separate. [POTIM](https://vasp.at/wiki/POTIM).

## 2. The nested calculation in ordinary Born–Oppenheimer dynamics

At a requested set of nuclear positions, the electronic calculation seeks a
stationary solution under the chosen model and branch preparation. In the common
self-consistency scheme, a density estimate determines an effective Hamiltonian;
solving for orbitals and occupations gives another density estimate. Updates
repeat until the specified stopping condition or a limit is reached.
These iterations do not represent elapsed physical time.
[Electronic minimization](https://vasp.at/wiki/Category:Electronic_minimization).

Then the derivative routines calculate forces for that geometry and electronic
solution. The nuclear integrator uses those forces to update positions and
momenta. At the next force evaluation, the new nuclear positions are held fixed
while the electronic problem is solved again. Electronic guesses and histories
may be carried forward according to the chosen method. Their effect on branch
selection and finite-precision continuation must be studied, not dismissed as
irrelevant because they are called solver history.

For a simple fixed-cell, unconstrained example with position-dependent forces,
velocity Verlet has this shape. Let `R` be nuclear positions, `P` momenta, `M`
the corresponding masses, `F` forces, and `dt` the selected time interval:

```text
Start with R_n, P_n and forces F_n evaluated at R_n.

P_half = P_n + (dt / 2) * F_n
R_next = R_n + dt * P_half / M

Hold R_next fixed:
    solve the electronic problem at R_next
    evaluate F_next at R_next using that solution

P_next = P_half + (dt / 2) * F_next
Completed state: R_next, P_next at t_n + dt.
```

The half-step momentum is an intermediate integrator value. Pairing it with
`R_next` does not make a completed full-step state; a checkpoint at that stage
needs to identify it and resume the remaining work. Constraints, thermostats,
moving cells, stochastic forces and coupled electronic dynamics require their
own stages and equations. This example is not their generic implementation.
See [VASP's integration overview](https://vasp.at/wiki/Time-propagation_algorithms_in_molecular_dynamics)
for velocity-Verlet and leapfrog staging, and the
[motion and dynamics research](../research/reference-campaign/dynamics-response.md)
for the focused studies still required.

Geometry optimization uses a different outer loop. It requests forces and perhaps
stress, chooses a trial displacement, evaluates it, then accepts or rejects it
under the optimizer's rules. That sequence is a search, not a trajectory of how
the material physically reached the structure. Static response and frequency-domain
calculations can describe dynamical properties without running either of these
position-update loops.

## 3. Keep these notions separate

| Quantity or ordering | Meaning | What it cannot establish |
| --- | --- | --- |
| Physical time and interval | Where a time-evolution method is on its modeled trajectory | Whether the machine has finished computing that point |
| Solver iteration or optimizer trial | Progress through a numerical procedure | Elapsed physical time or an accepted update |
| Integrator stage | Which intermediate updates have been performed and what each field represents | That every field belongs to the same full-step instant |
| GPU/MPI dependency and completion | Which work must finish before other work can read or reuse its data | That the result belongs to the requested geometry or branch |
| Archive entry and parent | A saved record and its continuation ancestry | A unique physical time across branches, or a new physical event for every save |
| Wall-clock time | Runtime measurement, deadlines and scheduling | Any simulated time interval |

Real-time electronic evolution and nuclear motion may use different step sizes
and exchange data at specified stages. A coupled method must define that schedule.
There is no proposed global clock to which all routines must conform. The existing
[electronic-evolution research](../research/reference-campaign/dynamics-response.md)
leaves these choices to the focused study.

## 4. What this requires from the interfaces

Pass the geometry, field-evaluation time where applicable, and the method-specific
stage through the operations that need them. Retain branch and solver history
where the method requires it. Do not make every routine carry a universal timestamp
or add a service that assigns one. A trial geometry and an accepted geometry must
remain distinguishable even if the same allocation is reused for them.

Execution dependencies usually form a partial order: independent work can overlap,
but a consumer must wait for its inputs. Completing later on a GPU does not make
one force evaluation the “newer” answer. The result must still refer to the geometry,
fields and method stage for which it was requested. Controlled tests can vary
completion order without promising deterministic numerical execution.

Concrete proposed teeth tests:

- Present completed forces from an earlier geometry to the next-stage operation;
  the public interface must prevent or reject that mismatch. Completion alone
  must not make it acceptable.
- Delay one independent operation so completion order reverses. Each consumer
  must still receive its requested result, and no buffer may be reused early.
- Save at a supported half-step and resume the remaining stages. Detect a skipped
  or repeated kick with an independently derived small problem, rather than only
  comparing two runs of the same implementation.
- Restore entries from two branches at equal physical time. Their data and history
  must remain distinct; matching time is not an equality rule.

These tests have not been implemented. Detailed continuation comparisons also
need to account for conditioning, chaotic trajectories and the chosen method's
history. No identical-future or physical-reversibility promise follows.
