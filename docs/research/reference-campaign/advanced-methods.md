# Localized spaces, correlated electrons and learned interatomic models

2026-09-25. Broad acquisition pass for buckets **12, 13 and 15**, with connections
to correlated forces (8), numerical primitives (1) and electronic propagation
(14). This follows the [core outline](../core-program-outline.md) and the
[localized](../first-pass/localized.md), [many-body](../first-pass/many-body.md),
[Fortran ML](../first-pass/ml-fortran.md) and
[C++ ML](../first-pass/ml-cpp.md) studies.

## Scope and material acquired

The [catalog](catalogs/advanced-methods.json) records **20 papers, nine implementation
snapshots and one candidate dataset repository**. Nineteen paper full texts were
acquired; Hirshfeld's 1977 article remains metadata-only. Eight implementation
snapshots and the dataset are pinned to Git commits; BerkeleyGW is its official
4.0 release archive. Asset URLs, byte sizes and SHA-256 hashes are recorded.

Reading covered abstracts, introductory material and selected passages identified
per record. Source inspection covered licenses, READMEs, file membership and a
few headers/procedure maps. It did not establish the correctness of any solver.
No downloaded program was installed, built, tested, trained or run. Archives
remain inert under ignored `quarantine/references/advanced-methods/`; reading
copies remain under ignored `papers/exvasperated/advanced-methods/`. Bundled
fixtures and models have not been adopted or audited, and no separate large
foundation-model or training-data collection was downloaded.

**This pass supports overall design exploration. Each subsystem requires a
focused deep expedition and regrounding before its detailed design or
implementation.** Acquiring a paper or a source archive does not make that
subsystem ready. The concrete questions below identify where to begin those
passes, without choosing an architecture or method for researchers.

## Literature map

Years below identify publication years when established; two records retain their
preprint year. The catalog distinguishes the edition actually acquired.

| Reference | Why it belongs here | Reading boundary |
| --- | --- | --- |
| [Marzari–Vanderbilt, 1997](https://arxiv.org/abs/cond-mat/9707145) | Spread minimization, gauge freedom and phase-branch/local-minimum behavior. | Abstract and local-minimum discussion; gradient derivation pending. |
| [Souza–Marzari–Vanderbilt, 2001](https://arxiv.org/abs/cond-mat/0108084) | Separate band-subspace selection from localization; inner/outer windows and initialization. | Abstract and silicon example. |
| [Damle–Levitt–Lin, 2018 preprint](https://arxiv.org/abs/1801.08572) | Variational alternative and selected-column initialization; useful challenge to an inherited optimization split. | Abstract and section 3.4. |
| [Knizia–Chan, 2012](https://arxiv.org/abs/1204.5783) | Entanglement bath and impurity construction, density-matrix matching and exact limiting cases. | Opening construction and self-consistency passage. |
| [Hirshfeld, 1977](https://doi.org/10.1007/BF00549096) | Definition of a real-space density partition, distinct from an orbital population. | Publisher abstract only; full text unavailable in this pass. |
| [Aryasetiawan et al., 2004](https://arxiv.org/abs/cond-mat/0401620) | Constrained screening, target-space polarization and frequency-dependent local interactions. | Motivation and screening-partition identity. |
| [Kaltak–Kresse, 2020](https://arxiv.org/abs/1909.01740) | Finite-temperature time/frequency grids, bosonic versus fermionic quantities and transform errors. | Introduction and concluding convergence/conservation discussion. |
| [Schäfer–Ramberger–Kresse, 2017](https://arxiv.org/abs/1611.06797) | Plane-wave Laplace MP2, basis convergence and parallel algorithm alternatives. | Abstract and introduction. |
| [Ramberger–Schäfer–Kresse, 2017](https://doi.org/10.1103/PhysRevLett.118.106403) | RPA derivatives, GW self-energy relationship and moving overlap operators. | Abstract and introduction; force derivation still requires study. |
| [Deslippe et al., 2012](https://arxiv.org/abs/1111.4429) | Independent GW/BSE implementation and its response/convergence choices. | Abstract and selected polarizability/Coulomb passage. |
| [Sangalli et al., 2019](https://arxiv.org/abs/1902.03837) | Yambo's excited-state algorithms, coupled BSE and iterative spectra. | Abstract and Krylov/Haydock section. |
| [Rohlfing–Louie, 2000](https://doi.org/10.1103/PhysRevB.62.4927) | Electron–hole kernel and the approximations linking a quasiparticle calculation to an optical spectrum. | Abstract and selected kernel/Tamm–Dancoff passage. |
| [van Setten et al., 2015: GW100](https://doi.org/10.1021/acs.jctc.5b00453) | Cross-implementation comparison that exposes basis, core, frequency and root-selection differences. | Abstract and multiple-root/method-comparison passage. |
| [Duchemin–Blase, 2019 preprint](https://arxiv.org/abs/1912.06459) | Continuation of screened interaction versus self-energy; contour-deformation alternative. | Abstract and introductory methodological comparison. |
| [Bartók et al., 2010: GAP](https://arxiv.org/abs/0910.1019) | Kernel energy model with force information and a locality approximation. | Abstract and selected GP/phonon passage. |
| [Bartók–Kondor–Csányi, 2013: SOAP](https://arxiv.org/abs/1209.3140) | Environment invariance, differentiability and limitations of finite descriptors. | Abstract and introductory representation discussion. |
| [Vandermause et al., 2020](https://doi.org/10.1038/s41524-020-0283-z) | Bayesian uncertainty and reference acquisition during dynamics. | Abstract and uncertainty/model discussion. |
| [Jinnouchi–Karsai–Kresse, 2019](https://arxiv.org/abs/1904.12961) | On-the-fly fitting and melting-point workloads with a thermodynamic correction for model-energy errors. | Abstract and thermodynamic-perturbation passage. |
| [Batzner et al., 2022: NequIP](https://arxiv.org/abs/2101.03164) | Equivariant learned representations and an alternative to fixed invariant descriptors. | Abstract and introductory workloads. |
| [Batatia et al., 2022: MACE](https://arxiv.org/abs/2206.07697) | Higher-body-order messages and the accuracy/execution tradeoff they investigate. | Abstract, introduction and opening model description. |

Public papers authored by VASP developers are legitimate scientific references.
They are not independent implementation checks merely because they are public.
None of the quarantined implementation, coefficient tables, diagnostic prose or
fixtures were transferred into this report or catalog.

## What the references change about our questions

### 12: Localized spaces and embedding

Localization has several separable choices: the band space, a gauge within that
space, the optimization objective and the interpolation derived from it. The
original Wannier paper discusses local minima associated with phase branches;
the disentanglement paper's silicon example shows initialization-dependent
localization minima. A small spread alone cannot establish that a selected space
represents the observable a researcher intends to compute. These are questions
for numerical and physical study, not reasons to silently select a preferred
branch. [Marzari–Vanderbilt](https://arxiv.org/abs/cond-mat/9707145),
[Souza–Marzari–Vanderbilt](https://arxiv.org/abs/cond-mat/0108084).

The variational/SCDM work supplies a genuinely different formulation to examine.
Its role here is to challenge assumptions about initialization and optimization;
it does not establish universal superiority. DMET supplies a precise example of
what an embedding construction and matching condition actually mean. Exporting
localized orbitals or interaction tensors alone does not implement that theory.
[Damle–Levitt–Lin](https://arxiv.org/abs/1801.08572),
[Knizia–Chan](https://arxiv.org/abs/1204.5783).

**Next deep pass:** derive overlap-metric projections and rank decisions; follow
phase/center conventions through interpolation; compare frozen-window and
variational constructions; identify how embedding bath rank and occupation are
defined. Begin at Wannier90's `src/disentangle.F90`, `src/wannierise.F90`,
`src/overlap.F90` and the postprocessing operators, plus PySCF's `pyscf/lo/`
and integral-export interface. Those scientific bodies remain unread here.

Useful candidate workloads are silicon valence/conduction interpolation, copper
entangled bands and a small Hubbard embedding. Add deliberately deficient trial
projections and degenerate subspace rotations. Compare projectors and observables
appropriate to the same subspace, rather than demanding one arbitrary orbital
gauge. For populations, a separate pass must distinguish original Hirshfeld,
iterative stockholder, orbital populations and other real-space partitions.

### 13: Screening, correlation and excitations

GW100 explicitly identifies multiple quasiparticle roots as a source of differing
answers even when underlying self-energies are similar. Therefore an energy-only
comparison can conceal an important disagreement about what was solved. The
continuation reference supplies a further distinction: approximating the
frequency dependence of the screened interaction and approximating that of the
self-energy need not have the same numerical difficulty. A candidate comparison
should retain enough of those functions to diagnose the difference.
[GW100](https://doi.org/10.1021/acs.jctc.5b00453),
[Duchemin–Blase](https://arxiv.org/abs/1912.06459).

The cRPA derivation partitions polarization before defining the partially
screened interaction. This makes the localized-space definition part of the
scientific method. A scalar interaction value detached from its target space,
frequency treatment and projection conventions is insufficient to reproduce the
calculation. [Aryasetiawan et al.](https://arxiv.org/abs/cond-mat/0401620).

Likewise, a coupled BSE, a Tamm–Dancoff BSE, a broadened response spectrum and a
selected set of exciton eigenpairs are different calculation choices. Yambo's
paper discusses dense diagonalization, spectrum-oriented Haydock iteration and
Krylov eigenvector approaches. Their convergence questions need to follow the
quantity being requested. [Rohlfing–Louie](https://doi.org/10.1103/PhysRevB.62.4927),
[Sangalli et al.](https://arxiv.org/abs/1902.03837).

**Next deep pass:** derive a small response/self-energy problem by two frequency
treatments; follow all quasiparticle roots and residues before defining a root
comparison; distinguish linearized, one-shot and updated calculations. Inspect
PySCF's `pyscf/gw/gw_ac.py`, `gw_cd.py`, `gw_exact.py`, `utils/ac_grid.py` and
periodic counterparts. Its public user documentation describes the three
frequency-integration approaches, while the pinned archive also contains
additional updated-GW modules; method scope must be checked at the chosen
version. [PySCF GW documentation](https://pyscf.org/user/gw.html).

For BSE, inspect BerkeleyGW's `BSE/kernel.f90`, `absorption.f90`,
`absp_lanczos.f90` and `full_solver/`, Yambo's `src/bse/`, and PySCF's
`pyscf/gw/bse.py`. For correlation energies and derivatives, return separately to
the Laplace MP2, finite-temperature quadrature and RPA-force papers; their full
derivations were not completed in this pass.

Candidate workloads include selected GW100 molecules spanning ordinary valence
and difficult root/continuation cases; bulk silicon GW; a reduced-dimensional
optical example with stated Coulomb boundary treatment; and small insulating
MP2/RPA systems. Compare direct sums with transformed quadrature in a tractable
finite model. Compare dense BSE spectra with iterative/propagated spectra under
matched broadening and approximations. Correlated force finite differences must
differentiate the same energy expression with controlled electronic errors.

### 15: Learned interatomic models

SOAP/GAP, low-dimensional Bayesian models and equivariant message models give
several ways to express environments and fit observables. Invariance, derivative
consistency, predictive error and uncertainty calibration are separate questions.
An invariant descriptor can still lose distinctions, and an accurately fitted
model can still be inappropriate outside the sampled environments.
[SOAP](https://arxiv.org/abs/1209.3140),
[GAP](https://arxiv.org/abs/0910.1019),
[NequIP](https://arxiv.org/abs/2101.03164),
[MACE](https://arxiv.org/abs/2206.07697).

Acquisition during dynamics changes the training history and hence later
predictions and decisions. It deserves a method-specific continuation study.
FLARE's original paper and current sparse implementation also need to be
distinguished: the original low-dimensional uncertainty argument cannot simply
be assigned to every later sparse model. The melting-point paper supplies a
useful workload because it assesses the effect of learned-energy errors on a
thermodynamic quantity, beyond fitting residuals.
[Vandermause et al.](https://doi.org/10.1038/s41524-020-0283-z),
[Jinnouchi–Karsai–Kresse](https://arxiv.org/abs/1904.12961).

**Next deep pass:** derive descriptors and coordinate/strain derivatives; study
cutoff smoothness, isolated atoms and difficult cells; follow fitting noise,
regularization and sparsification into uncertainty; examine acquisition and
restart as part of the scientific procedure. Start with FLARE's
`flare/learners/otf.py`, `flare/bffs/sgp/sparse_gp.py` and their C++ dependencies,
then compare the energy/force/stress paths in MACE's `mace/modules/` and NequIP's
`nequip/model/` and `nequip/nn/`. Source headers and maps were sampled, not these
complete computations.

Candidate tests include rotations and species permutations, derivative checks
across neighbor-list changes, held-out phases/defects, and frozen-model versus
continued-learning trajectories. Thermodynamic or rare-event workloads must
separate surrogate error, sampling error and error in the electronic reference.
Identical coordinates need not imply identical acquisition state; a reset is a
specified change of procedure, not an assumed equivalent continuation.

## Independent implementations and terms

The catalog has complete pins. These are research references, not dependency
selections. Top-level licenses do not establish every bundled file, model,
dataset or external dependency's terms.

| Snapshot | Scientific role | Terms actually inspected |
| --- | --- | --- |
| [Wannier90](https://github.com/wannier-developers/wannier90) | Localization/disentanglement and interpolation; library-interface candidate. | `LICENSE` and README: LGPL-2.1-or-later. |
| [BerkeleyGW 4.0](https://berkeleygw.org/download/) | Plane-wave screening, GW and BSE; independent GPU/distributed reference. | Archive `license.txt`: modified BSD with an additional enhancements grant; individual exceptions remain to inspect. |
| [Yambo](https://github.com/yambo-code/yambo) | Independent excited-state implementation, coupled BSE and propagation reference. | `COPYING` and README: GPL-2.0-or-later. |
| [PySCF](https://github.com/pyscf/pyscf) | Small molecular and periodic correlated calculations, local orbitals and alternative frequency treatments. | Apache-2.0; NOTICE and sampled source notices inspected. Dependencies have separate terms. |
| [QUIP](https://github.com/libAtoms/QUIP) | Potential/descriptor interfaces and atomistic integration. | README: mostly GPLv2, some public domain; GAP separately licensed. |
| [GAP](https://github.com/libAtoms/GAP) | Scientific reference for sparse kernel fitting and prediction. | Academic Software Licence, with academic noncommercial restriction. **Source-available, not OSS.** Held inert; no adoption. |
| [FLARE](https://github.com/mir-group/flare) | Bayesian acquisition, sparse models and continuation comparisons. | MIT code license. |
| [NequIP](https://github.com/mir-group/nequip) | Equivariant model and execution comparison. | MIT code license. Extension/model terms separate. |
| [MACE](https://github.com/ACEsuit/mace) | Higher-order equivariant model and execution comparison. | MIT-labelled code grant; README identifies differing model licenses, including ASL. |

QUIP's submodules were not fetched; the separate GAP archive is pinned
independently and is not asserted to match QUIP's gitlink. Source archives can
contain examples/fixtures; these remain quarantined reading material.

The [GW100 author repository](https://github.com/setten/GW100) was also acquired
at a commit. Its README describes method-labelled results and molecular
structures. No top-level license was identified in the inspected material.
Its data and scripts are not release fixtures, and the paper's license does not
establish their redistribution terms.

## Execution and comparison implications

CPU and NVIDIA are the first-wave targets; AMD remains second wave. BerkeleyGW
4.0 documents NVIDIA and later-AMD-relevant build paths using vendor libraries
and OpenACC/OpenMP target offload. This gives us concrete reference workloads and
decompositions to inspect; it does not prescribe our implementation framework.
[BerkeleyGW GPU manual](https://manual.berkeleygw.org/4.0/gpu-compilation/).

MACE and NequIP document accelerated tensor operations and compiled inference;
FLARE documents a GPU-capable LAMMPS route. They supply candidate precision,
derivative and throughput comparisons. No GPU capability or performance was
verified locally. cuda-oxide evaluation belongs to the execution track and should
use relevant contractions/operator applications from these families once bounded
workloads are specified; a framework's release label supplies no verdict.

The comparison hierarchy remains explicit:

- Algebraic identities, limiting cases and independently derived finite problems
  can verify a defined numerical operation.
- A genuinely independent implementation can challenge representation, algorithm
  and approximation choices; agreement still depends on matched inputs and scope.
- Agreement with VASP is oracle agreement under recorded conditions.
- Physical validation asks a further question, accounting for the chosen model,
  measurement and material conditions.

Shared external libraries, atomic data, equations or training labels limit the
independence of a comparison. None of the acquired models should be treated as an
independent physical truth simply because its implementation is open.

## Remaining gaps and verification of this delivery

The focused passes must broaden embedding/DMFT and impurity solvers, real-space
population methods, cRPA variants, stochastic estimators/covariance, correlated
stress and forces, and modern sparse time/frequency representations. CP2K and
additional periodic correlated implementations remain useful comparison leads;
they were not acquired by this track. BSE propagation and general electronic
time evolution need coordination with the dynamics/response track.

Hirshfeld full text was not obtained: the publisher provides subscription
content and the author's institutional record marks the article restricted.
Other initial HTTP errors/incomplete downloads were resolved using legitimate
arXiv, publisher, author or institutional endpoints. Paper editions and rights
remain distinct from implementation/model terms.

Delivery checks cover JSON structure, unique IDs, asset existence, byte counts,
SHA-256 hashes, PDF readability and source-archive readability. These are
acquisition checks, not scientific tests. Detailed equations, implementation
behavior, physical workloads, target measurements and method-specific acceptance
criteria remain work for the focused expeditions.
