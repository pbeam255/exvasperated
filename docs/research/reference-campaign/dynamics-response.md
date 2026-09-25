# Dynamics, response, vibrations and electronic evolution

2026-09-25. Broad acquisition and selected reading for outline buckets **9–11
and 14**. This pass supports the overall design. **Before detailed design or
implementation of any family below, make a focused expedition and reground the
work in its equations, assumptions, current implementations and difficult cases.**
Acquiring a paper or source archive does not establish subsystem readiness.

## Acquired material and actual scope

The [catalog](catalogs/dynamics-response.json) records 28 references: **20 acquired
paper PDFs, five acquired implementation archives, one acquired documentation
page, one paper whose download failed and one implementation with gated access**.
Each acquired asset has its source URL, local path, byte count and SHA-256; source
archives are pinned to commits. ArXiv version identifiers are recorded separately
from journal DOIs. In those records the year is the deposited version's year,
which can differ from the journal publication year.

Full texts are in ignored `papers/exvasperated/dynamics-response/`; inert source
snapshots are in ignored `quarantine/references/dynamics-response/`. Only this
original synthesis and metadata are intended for Git. No downloaded program was
built, installed or executed, no scientific calculation ran, and no source,
fixture, dataset or model was adopted into Exvasperated. Locally extracted text
and selected source files are reading aids, also ignored. Catalog inspection
fields distinguish selected pages/routines from unread material.

### Literature map

| Family | Primary references acquired | What was actually examined |
| --- | --- | --- |
| Thermostatting and time discretization | [Bussi, Donadio & Parrinello](https://doi.org/10.1063/1.2408420); [Leimkuhler & Matthews](https://doi.org/10.1063/1.4802990) | Canonical kinetic distribution, degrees of freedom, stochastic rescaling; numerical distortion of configurational distributions and barrier estimates. Full integrator proofs remain open. |
| Pressure and bias histories | [Bernetti & Bussi](https://doi.org/10.1063/5.0020514); [Barducci, Bussi & Parrinello](https://doi.org/10.1103/PhysRevLett.100.020603) | Volume equation and coordinate/momentum scaling; adaptive bias evolution and limiting distributions. |
| Nuclear evolution interfaces | [i-PI 3.0](https://doi.org/10.1063/5.0215869); [PLUMED 2](https://doi.org/10.1016/j.cpc.2013.09.018) | Socket force-provider composition and continuity caveat; enhanced-sampling library scope. |
| Transition paths | [Henkelman, Uberuaga & Jónsson](https://doi.org/10.1063/1.1329672) | Force projection, tangent role, climbing-image motivation and surface-reaction examples. |
| Perturbation response and finite field | [Baroni et al.](https://doi.org/10.1103/RevModPhys.73.515); [Souza, Íñiguez & Vanderbilt](https://doi.org/10.1103/PhysRevLett.89.117602) | Linearized coupled equations, occupied-space projection; field-polarized manifold, branch structure and mesh-dependent stability. |
| Magnetic/core observables | [Pickard & Mauri](https://doi.org/10.1103/PhysRevB.63.245101); [Taillefumier et al.](https://doi.org/10.1103/PhysRevB.66.195107) | Gauge-origin problem in atomic reconstruction; core transition matrix elements, core-hole impurity model and beginning of recursion formulation. |
| Harmonic and anharmonic vibrations | [Togo & Tanaka](https://arxiv.org/abs/1506.08498); [Togo, Chaput & Tanaka](https://doi.org/10.1103/PhysRevB.91.094306) | Force constants, mass/phase normalization, thermodynamic quantities; cubic Hamiltonian and phonon self-energy setup. |
| Electron–phonon coupling and transport | [Giustino review](https://doi.org/10.1103/RevModPhys.89.015003) **and [2019 erratum](https://doi.org/10.1103/RevModPhys.91.019901)**; [Verdi & Giustino](https://doi.org/10.1103/PhysRevLett.115.176401); [Perturbo](https://doi.org/10.1016/j.cpc.2021.107970) | Selected transport equations, all of erratum, long-range polar separation, occupation collision equation and bath assumptions. Most review sections remain unread. |
| Time propagation and GPU execution | [Gómez Pueyo et al.](https://doi.org/10.1021/acs.jctc.8b00197); [Octopus](https://doi.org/10.1063/1.5142502); [Perturbo GPU study](https://doi.org/10.1038/s41524-026-02135-5) | Nonlinear/time-dependent versus frozen-operator propagation; physical and numerical memory; state packing, residency and collision reduction layouts. Benchmark claims were not reproduced. |

The older [Castro, Marques & Rubio propagator paper](https://doi.org/10.1063/1.1774980)
was found, but the author-hosted PDF failed local TLS verification. Only metadata
and indexed abstract were read. The acquired 2018 treatment and Octopus paper
provide substantive starting material without pretending that this older body
was examined.

## Findings that affect the overall design

### 1. Correct evolution requires the specified measure and history

A plausible average temperature or a stable trajectory is insufficient to check
a sampling algorithm. The Langevin study exhibits discretization-dependent
configurational bias, including altered apparent barriers. The appropriate tests
must examine the requested observable's distribution and time-step dependence;
accuracy for a configurational average does not establish accuracy for a physical
time correlation. This distinction follows from the sampling objective explicitly
analyzed by [Leimkuhler & Matthews](https://doi.org/10.1063/1.4802990).

Pressure updates connect coordinate rescaling, momentum rescaling and the
kinetic contribution to pressure. Bernetti and Bussi derive different consistent
forms depending on which momenta are held fixed. Combining selected pieces from
those forms would change the stochastic evolution. The paper is a concrete
return reference for the source study's distinction between printed pressure and
the stress actually driving the cell. [Stochastic cell rescaling](https://doi.org/10.1063/5.0020514)

Bias history is part of a chosen procedure. Well-tempered metadynamics changes
future bias deposition using accumulated bias; restarting positions alone cannot
continue that same procedure. The inspected PLUMED implementation additionally
has explicit continuation handling for accumulated acceleration estimates.
Neither observation licenses identifying physical hysteresis with numerical
history, or erasing one because a configuration happens to match another.
[Method paper](https://doi.org/10.1103/PhysRevLett.100.020603),
[pinned MetaD source](https://github.com/plumed/plumed2/blob/f3d17f6dd8927a802c4c8580e7007c1ea7d99fb6/src/bias/MetaD.cpp)

### 2. A force-provider interface does not promise temporal continuity

The i-PI paper explicitly explains that successive requests to a client need not
be nearby configurations. That matters for electronic guesses, branch-sensitive
solutions, extrapolation and neighbor-list assumptions. Its method separation
is useful reference material, while Exvasperated must independently determine
which state is associated with a trajectory, replica or calculation request.
The sampled checkpoint code stores random-generator state and the generator
supports multiple streams; their exact continuation semantics still need a
focused trace. [i-PI paper](https://doi.org/10.1063/5.0215869),
[pinned generator](https://github.com/i-PI/i-pi/blob/1a93493d23c819fc0078ce1d9a85c83c37c846ee/ipi/utils/prng.py)

### 3. Response is a coupled scientific solve

The DFPT derivation couples first-order orbitals, density and potential. Its
occupied-space projection resolves a singular operator while retaining the
relevant response; it is not simply an ordinary eigenproblem with a small
parameter changed. The metallic and generalized-overlap cases need their own
return study before this derivation can be used to design PAW response routines.
This connects directly to the source report's degeneracy handling, occupation
response and numerical differences inside its response implementation.
[DFPT review](https://doi.org/10.1103/RevModPhys.73.515)

For finite electric fields, the occupied manifold, reciprocal mesh and
polarization branch enter the formulation. The Souza–Íñiguez–Vanderbilt paper
makes the mesh-dependent field stability explicit: refining the reciprocal mesh
at fixed field is not automatically a routine improvement that leaves the same
stable discrete problem. Branch tracking and field limits require scientific
analysis, including the path used to prepare the state.
[Finite-field paper](https://doi.org/10.1103/PhysRevLett.89.117602)

### 4. Nuclear observables reach into atomic reconstruction

The GIPAW starting material shows why changing the magnetic gauge origin matters
to a finite partial-wave representation even though the all-electron observable
is gauge invariant. The sampled derivation also imposes norm conservation in a
simplifying step. It cannot be transplanted unchanged into arbitrary PAW overlap
representations. The XANES paper supplies a separate reconstruction of core
transition amplitudes and a recursive route to spectra, with a specified
core-hole model. NMR shielding, hyperfine terms, field gradients and core spectra
need separate focused derivations and data assessment.
[GIPAW](https://doi.org/10.1103/PhysRevB.63.245101),
[XANES](https://doi.org/10.1103/PhysRevB.66.195107)

### 5. Phonons and transport depend on conventions and limiting procedures

The acquired harmonic treatment gives explicit force-constant signs, phase
factors, mass weighting and normalized eigenvectors. Phonopy's sampled reference
kernel averages equivalent-image phases and can explicitly Hermitian-symmetrize
the result; its polar path accepts a direction near the reciprocal origin.
These are useful independent checks for the source findings, but agreement after
symmetrization does not establish agreement of raw derivatives.
[Phonon paper](https://arxiv.org/abs/1506.08498),
[pinned dynamical-matrix source](https://github.com/phonopy/phonopy/blob/4f614db85c254f20cca1aecb18c87d0a0bf7fcf7/phonopy/harmonic/dynamical_matrix.py)

Polar electron–phonon interpolation must separate the long-range contribution
before treating the remainder as localized. The Verdi–Giustino treatment
connects that term to dielectric response and Born charges; quadrupolar and
low-dimensional extensions remain outside this reading pass.
[Polar-vertex paper](https://doi.org/10.1103/PhysRevLett.115.176401)

A particularly consequential acquisition is **Giustino's erratum**. It corrects
normalization factors, a current-density volume factor, and missing band and
occupation factors in the linearized transport equation. The original review's
transport page was among the pages read here. Equations used in later design
must incorporate the correction. This is a concrete example where a respected
reference and an apparently sensible implementation can share a subtle error.
[2019 erratum](https://doi.org/10.1103/RevModPhys.91.019901)

Relaxation-time transport, iterative linearized transport, and time-dependent
occupation dynamics ask different questions. The original Perturbo paper's
occupation dynamics holds the phonon bath fixed. It is also distinct from
coherent propagation of electronic orbitals: an occupation equation does not
retain the same phase information. These distinctions must survive any shared
implementation of grids, scattering data or evolution drivers.
[Perturbo method paper](https://doi.org/10.1016/j.cpc.2021.107970)

### 6. Electronic propagation has both physical and numerical memory

The 2018 propagator paper separates density-dependent nonlinear evolution from
applying an exponential of a frozen operator. It also distinguishes XC history
from the common adiabatic approximation, while numerical multistep schemes
retain history for a different reason. These are independent choices. A good
matrix exponential is not by itself a correct self-consistent propagator.
The sampled Octopus source alternates propagation with potential updates and
contains an inner self-consistent variant retaining a half-step state; this is
a concrete code path for the next derivation, not a verified algorithm here.
[2018 propagator study](https://doi.org/10.1021/acs.jctc.8b00197),
[pinned ETRS routines](https://gitlab.com/octopus-code/octopus/-/blob/f5a65398e0054ef4f11a2688053c4ae8bf33a6aa/src/td/propagator_etrs.F90)

### 7. NVIDIA work should follow the actual operation and dataflow

The Perturbo GPU study reorganizes irregular scattering contributions by their
destination so updates can avoid competing atomic writes. Its channel selection
already contains energy-window, broadening and matrix-element thresholds; those
approximations must be held fixed when comparing implementations. Its published
performance is specific to the studied systems and hardware, not an Exvasperated
forecast. The current public installation page also records concrete NVIDIA
compiler-version constraints and which calculation modes use the GPU path.
[GPU study](https://doi.org/10.1038/s41524-026-02135-5),
[installation documentation](https://perturbo-code.github.io/mydoc_installation.html)

Octopus's paper provides a complementary operation: propagating packed orbital
batches while keeping states resident on GPUs. Its current pinned README
advertises CUDA and HIP, but neither backend was exercised here. CPU/NVIDIA are
our first-wave targets; later AMD work should examine actual portability of each
operation. These references do not choose a backend for us or settle cuda-oxide's
merits. [Octopus paper](https://doi.org/10.1063/1.5142502),
[pinned README](https://gitlab.com/octopus-code/octopus/-/blob/f5a65398e0054ef4f11a2688053c4ae8bf33a6aa/README.md)

## Implementation holdings and terms

| Implementation | Pinned snapshot | Inspected terms and useful scope |
| --- | --- | --- |
| [i-PI](https://github.com/i-PI/i-pi) | `1a93493d23c819fc0078ce1d9a85c83c37c846ee` | Project offers MIT or GPL choice; MIT text inspected. Nuclear evolution, force-provider integration, random and continuation state. |
| [PLUMED](https://github.com/plumed/plumed2) | `f3d17f6dd8927a802c4c8580e7007c1ea7d99fb6` | LGPL-3.0-or-later in sampled source; root LGPL text inspected. Bias/collective-variable implementation and host interface. |
| [Phonopy](https://github.com/phonopy/phonopy) | `4f614db85c254f20cca1aecb18c87d0a0bf7fcf7` | BSD-3-Clause root license. Harmonic matrix, symmetry/image/phase handling and polar directions. |
| [phono3py](https://github.com/phonopy/phono3py) | `fece802ca1662b95211449ca6b40d0afd91697dd` | BSD-3-Clause root and sampled source. Anharmonic interactions/self-energy and lattice transport. |
| [Octopus](https://gitlab.com/octopus-code/octopus) | `f5a65398e0054ef4f11a2688053c4ae8bf33a6aa` | Distribution GPL-3.0; README describes GPL-2.0-or-later or MPL-2.0 individual files and bundled exceptions. Real-space response and time evolution. Official GitLab source acquired; GitHub namespace was empty. |
| [Perturbo](https://perturbo-code.github.io/mydoc_installation.html) | Source **not acquired** | Individual access request required; code license uninspected. Public paper/docs acquired. No registration submitted or message sent. |

Phonopy and phono3py are related projects, so agreement between them is not
independent evidence for all shared mathematics. Perturbo relies on QE routines
and QE/Wannier inputs; separate software names do not establish independent
electronic-structure reference data. QE, ABINIT and GPAW are acquired by the
adjacent ground-state expedition; their response/phonon components should be
examined jointly rather than downloaded again here.

A useful Rust lead appeared in the acquired sources: Phonopy exposes a C/Rust
backend choice, and phono3py's self-energy wrapper calls an external `phonors`
module. Only wrapper paths were inspected; its Rust source and capabilities were
not acquired or verified in this track. Follow that dependency before treating
it as an available numerical implementation.

Paper distribution permissions are distinct from code licenses. Most deposited
papers grant arXiv distribution permission rather than general downstream reuse;
the Leimkuhler–Matthews deposit indicates CC BY 3.0. Publisher/author copies and
bundled examples/data retain their own terms. Exact inspected terms/URLs are in
the catalog; none of these holdings is approved for incorporation by this pass.

## Discriminating calculations to develop next

These are proposed bounded experiments, **not results or accepted thresholds**.

| Question | Candidate calculation and what it could distinguish |
| --- | --- |
| Sampling versus stability | Harmonic oscillator and two-basin potential: compare known configurational/kinetic distributions over time-step and friction changes. Separate stationary averages, crossing statistics and physical time correlations. |
| Pressure measure and constraints | Idealized NPT model plus a constrained molecule in a skew cell: examine volume fluctuations, momentum scaling, constraint residuals and correct measure. Derive the constrained measure before selecting a reference histogram. |
| Continuation and branch history | Split/continuous stochastic and biased runs with specified generator and bias state; separately follow an insulating finite-field path. Test what each claimed continuation preserves without requiring different physical preparations to coincide. |
| Path search | Analytic curved path/narrow barrier with known saddle, then independently specified surface diffusion or dissociation. Check tangent sensitivity, image resolution and saddle index; a small projected force alone is insufficient. |
| Derivative response | Small insulating molecule/crystal: compare finite field/displacement and response on the same specified branch; sweep perturbation, solver accuracy and reciprocal mesh independently. Keep raw and symmetry-projected tensors. |
| Magnetic/core reconstruction | Gauge-origin translations for molecular shielding, then diamond/alpha-quartz reference families for NMR/core absorption. Assess partial waves, core-hole model, cell size and spectral broadening separately. |
| Phonons and transport | Nonpolar silicon and polar GaAs/anatase TiO2: test phase/mass conventions, directional long-wave behavior, direct versus interpolated matrix elements, and coupled mesh/broadening convergence. Contrast specified RTA and iterative models without demanding equal answers. |
| Coherent time evolution | Analytically solvable fixed Hamiltonian followed by a small self-consistent driven system: separate exponential error, time-ordering error, feedback error and physical approximation. Conservation tests apply only in limits where the chosen equations conserve the quantity. |
| CPU/NVIDIA comparison | The same bounded propagator or collision calculation with unchanged model, thresholds and inputs; examine norm/current/occupation and observable errors under ordering and precision changes before timing. |

## Required focused returns before subsystem design

1. **Motion and sampling:** acquire foundational SHAKE/RATTLE, constrained-measure,
   Nosé–Hoover-chain and flexible-cell derivations and corrections; current set
   does not cover these sufficiently. Trace `ipi/engine/motion/`, `thermostats.py`,
   `barostats.py`, corresponding serializers and PLUMED bias continuation. Derive
   degrees of freedom, measure and force/stress conventions for each chosen method.
2. **Response and branches:** read DFPT metallic/strain/long-wave sections and PAW
   response derivations; trace QE/ABINIT/GPAW response paths with their atomic
   datasets. Derive degeneracy treatment, occupation variation, polarization
   branches and validity of finite-difference comparisons. Hyperfine, EFG,
   spin-orbit magnetic response and optical sum rules remain major gaps.
3. **Vibrations and transport:** finish phono3py BTE/anharmonic derivations; read
   corrected electron–phonon equations, polar quadrupole/2D extensions and modern
   EPW/Perturbo methods. Trace Phonopy raw versus corrected force constants,
   phono3py self-energy/transport, and the `phonors` dependency. Define handling
   of true instabilities, vanishing scattering and singular conductivity from the
   chosen equations, without inserting numerical substitutes by habit.
4. **Electronic time evolution:** derive the selected equation including initial
   state, XC memory assumption, fields, moving metric/basis and feedback. Deeply
   inspect Octopus propagators and restart plus an independent basis formulation;
   distinguish coherent TDKS, electron–hole amplitude evolution and kinetic
   occupation dynamics. Electron–hole/BSE references belong with the adjacent
   correlated-electron expedition. Conservation alone does not settle phase or
   spectral accuracy.
5. **Hardware:** inspect actual device kernels and compiler restrictions for
   selected operations. Benchmark only after defining scientific comparisons.
   Do not infer cuda-oxide suitability from another compiler's success or failure.

The [ions](../first-pass/ions.md), [response](../first-pass/response.md),
[vibrations](../first-pass/vibrations.md), [many-body](../first-pass/many-body.md)
and [electronic-solution](../first-pass/electronic-solution.md) findings remain
open research inputs. This acquisition pass has not resolved their suspected
source defects, full capability combinations or every-file analysis.
