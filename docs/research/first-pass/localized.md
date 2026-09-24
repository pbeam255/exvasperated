# Localized orbitals, interpolation and embedding: first pass

Reference: quarantined VASP 6.5.1, inspected 2026-09-24. The `localized`
partition contains 35 files and 46,934 lines, identified in the
[inventory](../vasp-source-inventory.csv). This independently written report
records source observations. No localization, embedding or interpolation run
was performed.

## Reading scope

Procedure maps cover the Fortran files; the body reads below are deliberately
bounded. Generated parser bodies and substantial scientific bodies remain unread.

| Files | Body scope and limits |
| --- | --- |
| `locproj.F` | Input/setup 88–174; trial-overlap fragment 710–744; projected transformation 1003–1116; orthogonalization 2319–2427 and caller search. Full radial construction and intrinsic-orbital method unread. |
| `locproj_struct.F` | All 40 lines: orbital, position, spin, radial and storage declarations. |
| `mlwf.F` | Driver 505–622; neighbor overlaps 1220–1270; external-library route 1849–1914; rotated Hamiltonian 3605–3627; reader early return 3633–3660. Full setup, disentanglement, transformations and serialization partial. |
| `wannier.F` | Older rotation fragments 812–866, 885–926; centers/spreads 983–1120. Full optimization and PAW terms unread. |
| `wannier_interpol.F` | Hamiltonian setup 267–285; diagonalizer 335–361; Fourier driver 390–494. Velocity, optics and DOS paths mostly unread. |
| `wannier_mats.F` | Minimum-image Fourier sum 590–623; diagonalization 640–668. Descriptor, packing and HDF5 lifecycle mostly unread. |
| `lie.F` | Manifold search/update 855–953 and stopping/result 966–1027. Full objectives, line searches and matrix exponential unread. |
| `umco.F` | Setup 425–510; random seed 811–827. Complete orbital objective and convergence remain unread. |
| `embed.F` | Dispatch 167–235; second-method guards/branch 439–447, 486–503 and output/termination 550–605; entangled/complement transformation and PAW overlap 615–718. Other embedding methods and output remain unread. |
| `dmft.F` | Matrix-element entry 366–490. Four-index contractions, screened interaction and frequency assembly mostly unread. |
| `twoelectron4o.F` | Entry/reconfiguration 94–175. Integral kernels and full state restoration unread. |
| `fcidump.F` | Entry 62–162. Indexing, symmetry and serialized integral conventions mostly unread. |
| `lcao_bare.F` | Atomic initialization 97–176; radial iteration 240–327. Full basis selection, radial solver and convergence unread. |
| `sphpro.F` | Occupation diagonalization/sorting 1829–1915. Projection construction and full output mostly unread. |
| `stockholder.F` | Iterative density partition and normalization 998–1110; broader call map. Radial/angular integration, convergence domain and restoration partial. |
| `k-proj.F` | Execution restriction 130–143; active projection 243–274; writer 352–394. Coordinate mapping partial; intervening commented material was not treated as active code. |
| `wap.F` | Derivative import declarations 3205–3240 and dimension reader 3299–3357. Older derivative/interpolation bodies and full data reader unread. |
| `afqmc.F`, `afqmc_struct.F` | All 79 lines, including selection rejection, empty propagation and inactive default. |
| `parser/basis.cpp`, `parser/basis.hpp` | All 127 lines: parsed record layout, Cartesian product assembly and output helpers. |
| `parser/functions.cpp`, `parser/functions.hpp` | All 133 lines: angular/hybrid specification mapping and declarations. |
| `parser/sites.cpp`, `parser/sites.hpp` | All 51 lines: sites, ranges and coordinate storage. |
| `parser/radial.cpp`, `parser/radial.hpp` | All 27 lines: include-only source and radial modifier record. |
| `parser/locproj.l` | All 44 lines: lexical rules, comments, ignored characters and numeric conversion. |
| `parser/locproj.y` | Grammar 25–133; foreign entry/cleanup/error handling 145–207. Header/global setup remains partial. |
| `parser/call_from_fortran.F90` | Demonstration declarations and caller 25–120; not treated as production ABI proof. |
| `parser/makefile`, `parser/yywrap.c` | Complete build rules and small scanner termination helper. |
| `parser/lex.yy.c`, `parser/locproj.tab.c`, `parser/locproj.tab.h` | Inventory/build membership only in this pass; generated bodies unread. |

## Several different scientific objects share this area

Local projections, localized subspaces, interpolated operators, orbital
populations, real-space charge partitions and four-orbital interactions have
different meanings. Their dependencies overlap, but a projection coefficient
is not automatically a normalized probability and a converged localization
objective does not establish interpolation accuracy.

The local-orbital record carries radial choice, angular character, position,
local axes, spin direction and projector-channel information
(`locproj_struct.F`). Input can request automatically derived orbitals and
full reciprocal sampling; the complex route can request polarization-related
setup (`locproj.F` 88–166). The sampled trial construction contracts with the
PAW overlap metric (710–744). The atomic basis route also performs a radial
self-consistent iteration with density and on-site density-matrix mixing
(`lcao_bare.F` 240–327); it is more than reading an orbital shape.

The projected transformation weights band overlaps and takes an SVD. It
requires at least as many bands as localized functions, checks solver status
and combines singular vectors without singular-value scaling (`locproj.F`
1003–1116). This is the polar-factor construction of a subspace transformation.
The sampled body does not reject small singular values: rank-deficient input
can leave a mathematically nonunique completion. Its physical consequences
and any earlier rank checks remain unresolved.

A separate PAW-metric orthogonalization uses inverse square roots of singular
values, zeroes directions below a fixed threshold and alerts, then transforms
and normalizes states (2319–2427). It selects the first reciprocal point.
The two searched callers pass band ranges beginning at one (1990, 2177),
which matters because the helper uses global band indices into locally sized
arrays. This inspection does not establish that arbitrary starting bands are
supported. Rank truncation, normalization and preservation of the intended
subspace need joint analysis.

## Gauge, localization and interpolation

The main localization adapter distinguishes supplied projections, automatic
projections and selected-column construction, and either invokes an external
Wannier library or its internal transformation route (`mlwf.F` 505–622).
The selected-column algorithm itself belongs to the representation study;
this pass follows its use and excluded-band remapping. The sampled spin-matrix
export only handles its accepted spin-axis orientation (542–553).

Neighbor overlaps include reciprocal-cell offsets, use the polarization
module's PAW-aware overlap helper and consistently remove excluded bands
(1220–1270). The external library route runs on the designated output process
and distributes transformation, window and spread data afterward (1849–1914).
Build selection, process ownership, neighbor ordering and complex conjugation
are part of the scientific interface. This is not evidence that every compiled
configuration can execute that route.

The older rotation code uses cell-metric weights and derives centers from
complex phases (`wannier.F` sampled ranges). Another optimizer evolves on a
unitary manifold through skew generators and matrix exponentials, with multiple
line-search and conjugate-gradient choices (`lie.F` 855–953). Its stopping
logic and optional success flag distinguish an exit from iteration exhaustion
(966–1027). Full objective derivations and stationarity checks remain open.
A further orbital optimizer seeds randomness from clock and process identity
(`umco.F` 811–827); reproduction requires more than matching the initial wave
file and nominal optimization settings.

The rotated Hamiltonian is the band-energy matrix contracted with the chosen
subspace transformation (`mlwf.F` 3605–3627). The interpolation driver can first
apply a band shift, then Fourier-transform the coarse operator to real space
and back onto the requested grid before diagonalization (`wannier_interpol.F`
267–285, 446–468). Agreement at original points alone would not establish
accuracy between them or for derivative observables.

The matrix-object route uses minimum-image phase factors, explicitly
Hermitian-symmetrizes the reconstructed operator and rejects failed
diagonalization (`wannier_mats.F` 590–668). A future derivation must connect
orbital centers, periodic images, phase conventions and operator derivatives
to the electron–phonon mode contractions. Hermitian projection can hide a
small anti-Hermitian interpolation error; raw residuals would be useful in
bounded experiments, without being a replacement for the derivation.

## Embedding and many-electron interfaces

Embedding dispatch includes several orbital-construction methods, a Hamiltonian
export and orbital reordering (`embed.F` 167–235). The sampled method computes
PAW overlaps and uses an SVD to organize entangled states and their complement
(615–718). This second method rejects multiple spin channels or reciprocal
points; the local guard does not check that the single point is Gamma
(439–444). It uses the SVD only when occupied states outnumber selected
embedding states, otherwise selecting an identity transformation (493–500).
After orbital/projector output and cleanup it explicitly terminates execution
(550–605). Bath rank, occupancy assumptions, complex-build behavior and the
meaning of each embedding option remain to be derived. No claim of a complete
embedding solver follows from this fragment.

The interaction-matrix entry can remove spatial symmetry, rebuild reciprocal
sampling and wave layouts, restore Fermi energies, then select Bloch, projected
or Wannier target states (`dmft.F` 366–490). It allocates four-orbital tensors
and changes atomic augmentation settings before setting the interaction cutoff.
Target-space definition and screened-interaction frequency choices are explicit
dependencies on the many-body partition; the filename does not establish a
complete dynamical mean-field self-consistency cycle.

The four-orbital route rejects reciprocal-point group parallelism and also
rebuilds layouts (`twoelectron4o.F` 94–175). The integral-export entry rejects
more than one BLACS process, checks insulating occupations and prepares full
reciprocal mappings (`fcidump.F` 62–162). Its indexing, units, complex symmetry
and constant-energy terms still require body-level study before promising
interoperability with a downstream many-electron solver.

A capability boundary is explicit: `afqmc.F` rejects selection of the
auxiliary-field Monte Carlo route and contains no propagation operations;
`afqmc_struct.F` defaults its setting to inactive. This snapshot does not supply
an implemented solver through those files. Parity should distinguish exposed
placeholders from operational scientific capabilities.

## Populations, charge partitioning and interfaces

The sampled reciprocal projection sums squared plane-wave coefficients into
primitive-cell reciprocal classes and reduces the result; an unsupported
in-band process decomposition alerts and returns (`k-proj.F` 130–143,
243–274). Atomic augmentation is not added in that inspected active accumulation.
A later scientific interpretation must preserve this definition rather than
assuming a complete all-electron spectral weight.

Selected orbital-population helpers diagonalize small occupation matrices,
choose signs/order and use square roots of absolute eigenvalues in one helper;
neither sampled helper checks the eigensolver status locally (`sphpro.F`
1829–1915). Callers and admissible matrix properties need tracing before
inferring an observable defect.

The stockholder path instead iterates atom-centered radial densities against
the total density with core charge added. It mixes updates, checks a summed
radial difference, averages results by species and adjusts integrated norms to
match electron count (`stockholder.F` 998–1110). Charge conservation after that
adjustment does not independently validate the partition or its convergence.
The denominator used for the final adjustment requires a nonzero aggregate
norm; its physical domain remains a follow-up question.

The derivative dimension reader in `wap.F` extracts sizes and structural data
from HDF5, transposes a lattice and rejects unavailable HDF5 support
(3299–3357). This is another bridge to vibrations, with separate electronic
and phonon supercell dimensions. Complete shape validation and public format
attribution remain future work.

The local-projection parser has global result storage and foreign-call access,
with unchecked indexing in the selected accessor (`parser/locproj.y` 185–200).
The scanner silently ignores otherwise unmatched characters; numbers pass
through single-precision grammar/site values before double-precision record
storage (`locproj.l`, `locproj.y`, `sites.hpp`, `basis.hpp`). Site/function
combinations form a Cartesian product (`basis.cpp`). These facts motivate
precision, invalid-input and reentrancy questions, without adopting the grammar
or its protected text. Public documentation must establish compatibility tokens.
The build consumes generated scanner/parser files with regeneration rules
commented out (`parser/makefile`); generated-code provenance remains unread.

## Execution targets and useful revisits

CPU, NVIDIA GPU and AMD GPU acceptance must cover distributed waves, PAW
metric products, rank-revealing factorizations, complex small matrices,
interpolation, external-library calls and serialization. The inspected process
restrictions and random seeding mean parallel decomposition can change more
than speed. Source reading demonstrates no hardware execution or agreement.

Return with many-body methods for target-space screening and integral
conventions; with vibrations for gauge-consistent derivative interpolation;
and with numerical helpers for rank thresholds, complex SVD interfaces and
failure propagation. Public interfaces, complete generated-parser inspection,
all unread bodies and scientific workload selection remain follow-up work.
This report does not prescribe our replacement's architecture or dependencies.

## Independent review disposition

The [single independent review](reviews/localized.md) requested the immediate
workflow restrictions of the sampled embedding method. The author read its
guards, conditional SVD and termination, and incorporated them above. Other
checked claims were supported within the stated scope. No second review or
scientific experiment ran.
