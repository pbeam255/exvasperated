# First-pass source studies

This delivery covers the 20 areas in the [source partition](../vasp-source-partition.md).
The reference is the local VASP 6.5.1 tree identified by the
[file hashes](../vasp-source-inventory.csv). Paths and line numbers in the reports
refer to that snapshot. Reports contain independently written analysis, never
copied implementation text or proprietary diagnostic prose.

A first pass can identify useful behavior while leaving substantial questions.
Each report states its reading scope, distinguishes source observations from
inferences, and records questions and circumstances for returning. No calculation
or scientific validation is implied by source inspection. The present work ends
after all study reports receive one independent subagent review and warranted
corrections; the broad research campaign and replacement design follow later.

Each review is a single round at depth one. Review records identify findings;
the report records how the author addressed them. A corrected report is not sent
through another automatic review round. Work and follow-up are tracked in beads
under `exv-epl` and `exv-6l0`.

## Reports

- [Execution, build selection and lifecycle](execution.md)
- [Numerical foundations and shared state](foundations.md)
- [Input interpretation, output and continuation](io.md)
- [Parallel execution, accelerators and resource ownership](parallel.md)
- [Geometry, reciprocal sampling and symmetry](geometry.md)
- [Numerical representations and Fourier contracts](representation.md)
- [Atomic datasets, PAW and augmentation](paw.md)
- [Electrostatics, charge assembly and Hamiltonian fields](electrostatics.md)
- [Exchange-correlation, orbital corrections and magnetic constraints](xc.md)
- [Electronic iterations, eigensolvers, mixing and occupations](electronic-solution.md)
- [Nonlocal exchange and dispersion](nonlocal-interactions.md)
