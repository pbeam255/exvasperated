# Vibrations, electron–phonon coupling and transport: first pass

Reference: quarantined VASP 6.5.1, inspected 2026-09-24. The `vibrations`
partition contains 16 files and 31,404 lines, identified in the
[inventory](../vasp-source-inventory.csv). This is original source analysis;
no phonon, self-energy or transport calculation ran.

## Reading scope

Procedure maps guided selected body reads. Every assigned file is represented
below; inclusion does not mean complete analysis.

| File | Inspected body scope and limits |
| --- | --- |
| `finite_diff.F` | Initialization and force differences 145–223, 265–382; symmetric path 913–998; inverse and ionic dielectric contraction 1757–1810, 1855–1894. Full strain/piezoelectric reconstruction and output contracts remain unread. |
| `sydmat.F` | Selected tensor/symmetry reconstruction 68–135, 540–617. Full rank, displacement selection and constrained cases remain unread. |
| `phonon.F` | Polar checks/kernel 78–116, 153–192; initialization/acoustic correction 793–874; modes/directional limit 911–1086; Fourier construction 1164–1217. Complete interpolation and output remain partial. |
| `elphon.F` | Localized interpolation setup 3368–3421; coupling and mode rotation 4085–4168, 4207–4251. Most older self-energy, derivative and interpolation bodies remain unread. |
| `elphon_base.F` | Settings 45–108, 198–248; occupations 1583–1605; integration-window and mode contraction helpers 1615–1687. Most input validation remains unread. |
| `elphon_common.F` | Communicator setup 16–97; phonon-domain checks 1224–1253; selected dense-wave setup 1259–1355. Full velocity, interpolation and cache preparation remain partial. |
| `elphon_derivative.F` | Image mapping 69–125; export/setup 147–225; grid interpolation setup 610–664. Full derivative generation and serialization unread. |
| `elphon_driver.F` | Driver 96–196 and active electronic loop 278–374, with call map. Full accumulator dispatch/cleanup remains partial. |
| `elphon_kgrid.F` | Dataset setup 205–243 and triplet construction 450–515. Generalized-grid and external-library algorithms mostly unread. |
| `elphon_triplets.F` | Small integer-point/triplet methods 27–116. Their relation to every phase convention remains unproved. |
| `elphon_mels.F` | Coupling assembly/cache fragment 2040–2100; kernel dispatch 2325–2392; PAW terms 2692–2798. Redistribution and optimized contractions remain mostly unread. |
| `elphon_potential.F` | Import 81–145, 267–325; acoustic correction 328–390; dynamical matrix 573–646; modes 740–796; polar derivative 3543–3640; zero-point normalization 4055–4082. Most potential interpolation/cache bodies unread. |
| `elphon_potential_struct.F` | Selected declarations 7–63, 92–123: structural maps, force constants, polar tensors and derivative storage. Remaining declarations/lifetimes partial. |
| `elphon_accumulators.F` | Frequency conversion 166; broadened electron self-energy 992–1079; selected Debye–Waller contractions 1704–1757, 1810–1861. Tetrahedron electron kernel, degeneracy averaging and transforms mostly unread. |
| `elphon_selfen_ph.F` | Phonon self-energy tetrahedron accumulation 1248–1322, plus procedure map. Selection, integration setup and final normalization mostly unread. |
| `transport.F` | Quadrature driver 1006–1087; energy transformation 1350–1385; mean free path 1408–1416; lifetime 1580–1606; moments/coefficients 1661–1742. Hall, chemical-potential solving and full units remain partial. |

## Force derivatives, constraints and phonon modes

The finite-displacement state machine retains reference positions and forces,
selects displacement stencils and builds a force Jacobian. Large requested
steps above its local bound are replaced by a smaller default, and stencil
counts are restricted to the supported choices (`finite_diff.F` 145–223).
One-sided, central and higher-order differences therefore need separate
convergence studies. The matrix of force derivatives and the returned force
constants have opposite signs; mass weighting is another separate operation
(265–354). The complete HDF5 sign convention has not been traced.

Symmetry reconstructs tensor information through rotations and atom mappings
(`sydmat.F` sampled ranges). Symmetrizing the assembled matrix does not prove
that displaced forces were accurate or that the chosen directions span the
allowed constrained space. Two sampled real symmetric diagonalizations print
an error indication and continue on nonzero solver status (`finite_diff.F`
355–365, 982–995). Whether downstream consumers reliably reject such results
is unresolved.

The sampled inverse helper excludes the first three eigenmodes by index and
retains only subsequent eigenvalues above a threshold (1757–1810). That is a
specific restricted inverse, with assumptions about translations, stability
and ordering. It cannot be treated as a generic inverse for an arbitrary
constrained or unstable system. Ionic dielectric response contracts this
inverse with Born-charge tensors on both sides (1855–1894), connecting this
study directly to response convergence and acoustic constraints.

Two phonon paths enforce translational constraints differently. The older
initializer replaces an on-site block with the negative sum of other blocks
(`phonon.F` 793–874). The imported-force-constant path iterates row/column
corrections and transpose symmetrization before its on-site correction
(`elphon_potential.F` 328–390). These operations can change small frequencies;
raw and corrected tensors should be distinguished in future comparisons.

Fourier interpolation combines supercell/image maps, atomic phases, masses
and, when active, a polar long-range term. The older mode path explicitly
Hermitian-symmetrizes the dynamical matrix, checks the complex eigensolver's
status and returns signed square roots of eigenvalues (`phonon.F` 911–1086).
Negative values encode instability. Its Gamma polar correction depends on an
approach direction, with a default along the first reciprocal coordinate
axis (934–958, 1029–1070). A single Gamma result cannot stand for every directional
limit in a polar material.

The newer imported-force-constant path averages phases over equivalent shortest
images and includes atomic basis phases (573–646). Its mode routine converts
to angular frequency in units of inverse picoseconds and also uses signed
square roots, but does not check the eigensolver status locally
(`elphon_potential.F` 740–783). Later validity propagation is a return question.
The electron accumulator's conversion uses the reduced Planck constant
(`elphon_accumulators.F` 166), consistent with angular frequency; a cyclic
frequency interpretation would introduce a factor of two pi.

## Derivatives and matrix elements retain PAW and phase structure

Derivative data include local-potential changes, atomic matrix changes,
overlap information, force constants and polar tensors. Import checks compare
stored shortest-image information with reconstructed maps and handle alternate
structural records (`elphon_potential.F` 81–145, 267–325). The export path uses an existing primitive-cell object or constructs a related
object from a supplied primitive lattice, then can build an interpolation grid; identity-aligned and
general grid cases use different preparation (`elphon_derivative.F` 147–225,
610–664). Public format contracts and migration behavior remain to be established.

The sampled long-range derivative uses Born charges and quadrupoles, dielectric
screening, Ewald damping, atomic phases and optional radial Coulomb truncation.
It excludes the reciprocal origin (`elphon_potential.F` 3543–3640). Separating
short- and long-range pieces correctly requires consistent cell, phase,
normalization and dielectric conventions on both sides of interpolation.
The local checks read here do not prove the dielectric tensor's physical domain.

Couplings combine smooth-potential and PAW contributions. Selected PAW kernels
contain projector derivatives weighted by atomic Hamiltonian minus band energy
times overlap, and another term proportional to the two band energies'
difference (`elphon_mels.F` 2692–2798). An independent reconstruction must derive
these generalized-metric terms and their conjugations. A scalar local potential
derivative alone would omit inspected contributions.

The coupling path caches derivatives by reciprocal transfer, adjusts wave and
projector phases, reduces Cartesian couplings across the band communicator,
and contracts with mode vectors (2040–2100; `elphon_base.F` 1668–1687).
The dispatch selects direct or matrix-product kernels; a separate explicit
skip setting fills the Cartesian coupling with unity (2358–2388). Runs using
that setting would not constitute a physical matrix-element comparison.

Mode normalization is supplied before this contraction in the newer route:
positive frequencies receive the zero-point displacement factor including
mass; nonpositive modes are zeroed and an error flag is returned. Its immediate
wrapper does not inspect that flag (`elphon_potential.F` 786–796, 4055–4082).
An earlier dispersion check rejects sufficiently negative frequencies unless
the corresponding override is enabled (`elphon_common.F` 1224–1253).
The older route instead uses a complex square root for negative modes and
zeros only near-zero modes (`elphon.F` 4207–4251). These are materially different
policies, not a demonstrated numerical discrepancy on a stable workload.

## Electron and phonon self-energies

The sampled broadened electron kernel forms squared matrix elements multiplied
by Bose and Fermi occupation factors, with emission and absorption denominators.
The static approximation removes phonon energy from those denominators while
retaining it in occupations; small modes are omitted. A requested derivative
of the self-energy is accumulated separately (`elphon_accumulators.F`
992–1079). Temperature, chemical potential, broadening, mode cutoff and band
selection all affect the result. Tetrahedron integration is a separate path
whose full equations remain unread.

The sampled Debye–Waller construction combines mode covariance-like factors
with Gamma Cartesian couplings and electronic energy denominators. If its
broadening is exactly zero, the selected body substitutes a nonzero value
(1704–1757, 1810–1861). The rigid-displacement identities, approximation scope
and cancellation with the electron self-energy require a joint derivation;
individual term agreement is insufficient.

A local concern in the phonon self-energy kernel deserves a bounded return.
The temporary self-energy is reset before the mode loop, incremented within
that loop and added to each mode's stored result (`elphon_selfen_ph.F`
1302–1317). Thus the local arithmetic carries preceding mode contributions
into subsequent modes. Its intended accumulation contract, active reachability
and numerical consequences have not been established. This is a source concern,
not an observed scientific failure. The same body uses occupation differences,
tetrahedron delta weights and squared couplings, so a later diagnostic should
separate mode indexing from integration and spin normalization.

## Transport and execution

Transport forms mean free paths from velocities and lifetimes, symmetrizes
velocity products, integrates a transport function and builds Onsager moments
(`transport.F` 1006–1087, 1408–1416, 1661–1687). The sampled quadrature maps
Gauss–Legendre points through the Fermi-function variable; zero temperature
uses a collapsed energy grid (1350–1385). This ties integration accuracy to
temperature, band edges, sampling and lifetime variation.

The lifetime helper starts from zero and only assigns the inverse of twice
the imaginary self-energy magnitude above its threshold (1580–1606).
Below threshold it leaves zero, rather than a divergent lifetime. Conductivity
inversion enters thermopower and thermal conductivity, and mobility divides
by carrier density (1690–1742). Singular conductivity and vanishing carrier
density require caller/domain analysis; the local formulas do not settle them.
Full units and all selected relaxation approximations remain unproved.

The driver prepares dense waves and separate communicators, then supports
constant-relaxation-time transport without loading derivative/force-constant
data. A selected dispersion route can return early. The electronic loop's dry
run returns only after earlier preparation (`elphon_driver.F` 96–196,
278–374). The active loop constructs integer momentum triplets with
k equal to k-prime plus q, filters contributions and computes couplings.
Generalized-grid setup can use compiled external symmetry support or imported
symmetry data (`elphon_kgrid.F` 205–243); selected triplet reduction invokes
external grid routines and counts representative multiplicities (450–515).

For CPU, NVIDIA GPU and AMD GPU, the relevant work includes dense-wave
redistribution, derivative and wave caches, matrix contractions, FFTs,
small eigensolvers, shared-memory storage and threaded reductions. The inspected
code does not establish all-target execution or numerical agreement. Cache
phase identity and collective ownership need equal attention with arithmetic
throughput. No backend is selected by this study.

## What should bring us back

Return after localized interpolation and numerical-helper studies to derive
phase/gauge and normalization contracts, and after many-body work to compare
frequency, degeneracy and self-energy conventions. The local phonon accumulator,
eigensolver-status paths, unstable-mode policies, lifetime threshold and
singular transport domains are named follow-up questions. Complete per-file
reading, public interface attribution, scientific workloads and hardware runs
remain future work. This bounded pass provides connected questions without
claiming exhaustive closure.

## Independent review disposition

The [single independent review](reviews/vibrations.md) supported the checked
scientific claims and identified two corrections. The author corrected the
Gamma/Fourier source labels and citations, and clarified the provenance of the
primitive cell used by derivative export. Both corrections are incorporated
above. Local concerns remain untested; no second review or experiment ran.
