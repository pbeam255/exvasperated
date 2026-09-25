# Ground-state foundations: literature and reference acquisition

2026-09-25. Buckets 2–8 of the [core outline](../core-program-outline.md).
This is a bounded expedition for **overall design orientation**. Each subsystem
requires a focused deep expedition and scientific regrounding before its detailed
design or implementation. Acquiring these references does not establish readiness
to implement their methods.

## Acquired material and actual inspection

The [catalog](catalogs/ground-state.json) records 29 sources: **17 acquired full-text
PDFs, seven pinned implementation archives, one bounded dataset sample, and four
metadata-only papers**. Every acquired file listed in the catalog has a URL,
SHA-256 and byte count. Full texts and source archives remain in ignored
`papers/exvasperated/ground-state/` and `quarantine/references/ground-state/`.
No downloaded code was installed, built or executed. No scientific calculations
were performed, and no third-party implementation or dataset was adopted.

Reading was selective: abstracts/introduction passages and named sections relevant
to the questions below, with scope recorded per item. Source inspection covered
licenses, introductory documentation, selected interface/driver introductions and
file locations. Large implementation bodies, derivations and numerical results
remain unaudited. Archive acquisition includes upstream bundled examples and data;
their presence supplies no permission or scientific justification to adopt them.

## What the sources change about our questions

### PAW correctness spans the dataset and its consuming formulation

The [author PAW review](https://arxiv.org/abs/cond-mat/0201015),
[real-space GPAW derivation](https://arxiv.org/abs/cond-mat/0411218), and
[two-formulation comparison](https://users.wfu.edu/natalie/papers/PAWform/PAWformman.sdarticle.pdf)
provide different views of the same reconstruction problem. They connect smooth
orbitals, projector duality, reconstructed quantities and energy derivatives.
This is the appropriate starting point for the source study's unresolved overlap,
compensation-density and atomic/smooth cancellation questions.

The [2019 correction paper](https://doi.org/10.1016/j.cpc.2019.05.009)
is particularly valuable: a compensation-density contribution used in one PAW XC
formulation can lead to problematic density arguments. Remedies alter dataset
construction and require convergence checks. A broadly successful formulation
can still have a narrow, physically significant failure domain.

The [JTH v2.0 validation report](https://www.abinit.org/atomic_data/paw/ATOMICDATA/JTH-PBE-v2.0.pdf)
explicitly describes changes intended to avoid non-positive overlap matrices and
negative XC density arguments, as well as changes to radial resolution. Its tests
use specified ABINIT and generator versions. Those findings are concrete leads
for investigating metric positivity, radial interpolation and model matching;
they are not proof that our future consumer will handle the data correctly.

**Design implication to investigate:** reconstruct the selected mathematical
formulation, dataset ingredients and derivatives together. File-format compatibility
alone cannot settle equivalence. See the [PAW study](../first-pass/paw.md).

### Precision must be tested through several observables

[SSSP](https://arxiv.org/abs/1806.05609) combines equation-of-state comparisons
with convergence of phonons, bands, cohesive energies and pressure. It supplies
an immediate reason to resist treating energy convergence as a universal proxy.
Its explicit distinction between verification and validation matches our need to
separate numerical correctness, agreement with another code and physical accuracy.

[Bosoni and collaborators](https://arxiv.org/abs/2305.17274) provide a broader
reference built from 960 equations of state, cross-checked between all-electron
implementations. Their comparison requires deliberate matching of numerical and
methodological choices, including occupations and reciprocal sampling. Magnetic,
relativistic and other property coverage remains a separate question. We acquired
the paper, **not the raw 960-system calculation archive**.

**Candidate comparisons:** small selections of unary solids and oxides with
contrasting bonding/oxidation environments; independent convergence sweeps for
energy, pressure, force derivatives and band quantities. Select an explicit
physical model and observable before interpreting cross-code differences.

### Electronic convergence and path selection remain scientific questions

[Woods, Payne and Hasnip](https://arxiv.org/abs/1905.02332) organize the nonlinear
SCF problem, ill-conditioning and solver robustness around a diverse test suite.
The acquired DFTK SCF guide provides a compact independent route into the same
questions. Neither establishes that an algorithm has reached the branch a
researcher seeks. Initial electronic state, occupation treatment and numerical
history remain part of the specified procedure.

[Cold smearing's original Al(110) application](https://www.physics.rutgers.edu/~dhv/pubs/local_copy/nm_al110.pdf)
connects broadening moments and positive occupations to free-energy and derivative
behavior. Broadening used for integration must be distinguished from a physical
electronic temperature. Follow this through forces and stress, rather than
selecting an occupation function solely by how quickly SCF terminates.

**Candidate comparisons:** insulator, metal, elongated metal cell, metal/vacuum
slab and a separately chosen competing-spin-state problem. Record the explicit
initialization and continuation procedure. Investigate branch differences without
automatically treating one trajectory as the correct answer. See the
[electronic study](../first-pass/electronic-solution.md).

### Numerical improvements can change the approximation

[PBE](https://dft.uci.edu/pubs/PBE97.pdf) and
[r²SCAN](https://arxiv.org/abs/2008.03374) give a useful contrast between functional
construction and numerical regularization. The latter explicitly addresses the
interaction of smoothness and exact constraints. A stabilizing transformation
needs its own physical justification; it is not necessarily a harmless implementation
detail. Energy, potential and response derivatives require separate inspection,
as illustrated by the [Libxc paper](https://arxiv.org/abs/1203.1739).

[ACE](https://math.berkeley.edu/~linlin/publications/ACE.pdf) ties an exchange
compression to its construction subspace and adapts it as orbitals change.
This is a concrete return point for the [nonlocal study](../first-pass/nonlocal-interactions.md):
which actions are preserved, when is rebuilding required, and what remains valid
for empty states and derivatives? The paper's performance results were not reproduced.

### Geometry, boundaries and derivatives expose different errors

[Magnetic symmetry algorithms](https://arxiv.org/abs/2211.15008) explicitly
distinguish magnetic-vector action, time reversal and tolerances for positions
and moments. A geometry-only operation list is insufficient. Proposed checks
should include skew cells, perturbations across tolerance boundaries and explicit
spin transformations; the admissible symmetries still depend on the physical model.

[Ismail-Beigi's Coulomb truncation](https://arxiv.org/abs/cond-mat/0603448)
is a direct reference for confined systems represented periodically. Follow the
boundary prescription and limiting kernels through the whole energy expression
and its derivatives. Convergence with vacuum size is a useful test ingredient,
not a proof that all long-wavelength and stress terms are correct.

[AD combined with DFPT](https://arxiv.org/abs/2509.07785) offers a promising
independent route for derivative comparisons. Its implicit treatment of electronic
response deserves study alongside analytic and finite-difference expressions.
Automatic differentiation does not establish that a branch is smooth or that the
chosen discrete calculation represents the intended physical derivative.

## Independent implementation candidates acquired

The full commit hashes and upstream license locations are in the catalog. These
are research references; no library or architecture selection follows.

| Reference | Pinned commit prefix | Useful entry points for focused reading | Inspected terms |
| --- | --- | --- | --- |
| [DFTK](https://github.com/JuliaMolSim/DFTK.jl) | `5a94a1407fa6` | `docs/src/guide/self_consistent_field.jl`; `src/scf/`; `src/postprocess/forces.jl`, `stresses.jl`; force-error examples | MIT |
| [Quantum ESPRESSO](https://github.com/QEF/q-e) | `61569eb48023` | `PW/src/electrons.f90`, `mix_rho.f90`, `forces.f90`, `stress.f90`; `README_GPU.md` | Root GPLv2 text/README; bundled components need separate inspection |
| [ABINIT](https://github.com/abinit/abinit) | `edbeb6602f08` | `doc/tutorial/paw2.md`; `shared/libpaw/src/m_pawtab.F90`, `m_pawxc.F90` | COPYING says mostly GPLv3 plus selected Apache-2.0 exceptions; README itself has GPLv2-or-later notice |
| [GPAW](https://gitlab.com/gpaw/gpaw) | `2c0c73577daf` | PAW formalism paper; `gpaw/mixer/` and its legacy aliases; distinguish representation and old/new implementation paths | GPL-3.0-or-later |
| [Libxc](https://gitlab.com/libxc/libxc) | `db80b1dcb8b2` | `src/xc.h`, r²SCAN module metadata, symbolic/generated expressions, derivative tests | **MPL-2.0** in current acquired tree; old BSD descriptions are insufficient |
| [Spglib](https://github.com/spglib/spglib) | `a6b561fb60cd` | Magnetic API/algorithm paper; symmetry and reciprocal-mesh implementation to locate in focused pass | BSD-3-Clause |
| [DFT-D4](https://github.com/dftd4/dftd4) | `82fbaf41724a` | `src/dftd4/disp.f90`, model modules and derivative tests; citation file identifies periodic extension paper | LGPL-3.0-or-later in inspected source headers |

QE's acquired GPU documentation is a useful CPU/NVIDIA execution reference.
These archives do not establish comparable coverage or performance on our target
hardware. CPU/NVIDIA remain the alpha targets; AMD is a later objective.

The [JTH dataset repository](https://github.com/abinit/paw_jth_datasets), pinned at
`a03e3f0b7ac8395550cca88880d8cb7dcd478bb3`, supplied only the hydrogen PBE v2.0 XML,
its generator input, README and GPLv3 LICENSE. The inspected XML records units,
generator, functional, partial-wave and radial-grid metadata. Numerical arrays
remain unexamined. Dataset reuse/distribution terms must be settled specifically;
we do not infer them from ABINIT's code license or acquire a whole library by default.

References are not automatically statistically or mathematically independent.
Several codes use Libxc, may share dataset families or numerical libraries, and
implement the same approximation. A focused comparison must identify which parts
are genuinely independent and which sources of error can therefore be exposed.

## Next focused expeditions before subsystem design

| Buckets | First questions and required deeper work |
| --- | --- |
| 2: representations/symmetry | Reconstruct reciprocal normalization, spinor phases and symmetry maps. Read original integration theory and Spglib magnetic search; compare reduced/full calculations and changing-cell basis policies. |
| 3: atomic/PAW | Work through original and modified PAW derivations, 2010/2019 comparisons and JTH generation. Inspect full libPAW/GPAW operator and energy paths. Acquire/evaluate ATOMPAW itself; establish projector completeness, overlap behavior, radial errors, ghost states and transferability. |
| 4: electrostatics | Derive each chosen boundary kernel and origin limit, then follow ionic, electronic and compensation terms through energy/forces/stress. Charged cells, environmental models and applied fields need dedicated literature. |
| 5: XC/spin/orbital terms | Acquire original functional papers plus errata, verify symbolic/analytic derivatives and low-density/kinetic-density limits. DFT+U, noncollinear magnetism, spin-orbit coupling, constraints and potential-only approximations need substantially more acquisition. |
| 6: nonlocal terms | Derive exchange singularity treatment and ACE reconstruction/refresh; acquire original screened-hybrid and density-based dispersion literature. DFT-D4 is only one dispersion family; periodic charge and force/strain dependence require study. |
| 7: stationary electronic problem | Deep-read SCF algorithm derivations and actual solver/mixer bodies. Acquire benchmark inputs under known terms. Separate nonlinear residual, eigenproblem error, occupations, branch selection and continuation history. |
| 8: derivatives | Acquire stress theorem full text and PAW force/stress derivations. Compare analytic, finite-difference and AD/response constructions under matched branch, occupation, basis and cell-change assumptions. Include incomplete-stationarity error. |

All seven buckets have starting references, but several subfamilies have only
leads. The broad first-pass source studies retain their own unresolved questions;
this acquisition does not close them. In particular, this is not a complete
hybrid/XC/relativistic capability bibliography or a scientific acceptance suite.

## Access limits and follow-up

Four originals remain metadata-only: [Blöchl 1994](https://doi.org/10.1103/PhysRevB.50.17953),
[Kresse–Joubert 1999](https://doi.org/10.1103/PhysRevB.59.1758),
[Monkhorst–Pack 1976](https://doi.org/10.1103/PhysRevB.13.5188), and
[Nielsen–Martin 1983](https://doi.org/10.1103/PhysRevLett.50.697).
The catalog distinguishes publisher authorization, fetch failure and simple
non-acquisition. These are full-text acquisition tasks, not papers already read.
The original PBE erratum also needs focused reading.

Initial arXiv downloads for ACE and cold smearing returned HTTP 406; legitimate
author-hosted PDFs were acquired instead. GitLab acquisition succeeded after
checking actual default branches. No subscription barriers were bypassed.

Local checks: acquired-file hashes and byte counts checked against catalog;
JSON parsed, record IDs checked for uniqueness, all bucket numbers 2–8 represented.
Those checks concern acquisition integrity, not scientific correctness.
