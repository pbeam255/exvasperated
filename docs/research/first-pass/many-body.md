# Screening, quasiparticles and many-body response: first pass

Reference: quarantined VASP 6.5.1, inspected 2026-09-24. The `many_body`
partition contains 42 files and 157,269 lines, identified in the
[inventory](../vasp-source-inventory.csv). This is original source analysis.
No correlation-energy, quasiparticle, spectrum or force calculation ran.

## Reading scope

This large partition needs several later scientific passes. Procedure searches
provided navigation; selected bodies establish the connected observations below.
Coefficient tables, complete solver derivations and several major kernels remain
unread. None of the reference coefficients have been adopted.

| Files | Body scope and limits |
| --- | --- |
| `chi_glb.F` | Method reset/dispatch 911–965, 980–1043. Remaining method combinations and input defaults partial. |
| `chi.F` | Preparation 477–571; BSE dispatch 1200–1281; self-energy/update flow 2045–2128; dielectric conversion 3870–3921; inversion 4356–4437. Most driver and local-field bodies unread. |
| `chi_base.F` | Transition-density fragment 335–403; frequency weights 689–776; thresholded inverse 2850–2895. Full response accumulation and thermal kernels unread. |
| `chi_GG.F`, `chi_super.F` | Entry restrictions/preparation 220–305 and 230–286 respectively. Distributed real-space algorithms remain mostly unread. |
| `GG_base.F` | Time/frequency process selection 541–601. Complete descriptors, memory sizing, transforms and communication unread. |
| `greens_real_space.F` | Green-function dispatch 157–266. Full real-space products and self-consistent construction unread. |
| `greens_orbital.F` | Selected transform helpers 130–183. Caller reachability and full orbital Green-function solver unread. |
| `screened_2e.F` | Mapped accumulation 382–434. Storage selection, self-energy contraction and restart mostly unread. |
| `wpot.F` | Lazy screened-potential loading, scaling and symmetry reconstruction 311–443. Full cache lifecycle and file contracts partial. |
| `acfdt.F` | Trace-log eigenvalue evaluation 467–526. Full coupling/frequency integration, exchange corrections and energy assembly unread. |
| `acfdt_GG.F` | Distributed correlation entry/declarations 127–185. Trace-log and force bodies mostly unread. |
| `esf.F`, `esf_struct.F` | Eigenvalue trace 698–722 and all 68 structure lines. Structure-factor interpolation/integration mostly unread. |
| `crpa.F` | Projected target weights 1493–1586. Disentanglement, target subtraction and complete constrained screening unread. |
| `local_field.F` | Entry/interface declarations 219–260 and procedure map only. Vertex/kernel construction unread. |
| `gw_model.F` | Local density-dependent model 476–513. Full model self-energy and reciprocal kernel unread. |
| `pade_fit.F` | Linearized fractional-Pade quasiparticle estimate 1543–1610; bracket/root selection 1694–1780. Coefficient fits, SVD alternative and higher-level fallback partial. |
| `minimax.F` | Imaginary-grid setup/transforms 61–180. Interval normalization, actual fitting and transform-error use unread. |
| `minimax_struct.F` | Selected quadrature function/table/communicator declarations 28–80. Remaining types and dispatch partial. |
| `minimax_functions1D.F`, `minimax_functions2D.F` | Reciprocal helper/derivative 42–70 and exponential helper/derivative 37–69. Other basis families unread. |
| `minimax_varpro.F` | Selected fitting interface declarations 320–353 and procedure map; solver body unread. |
| `minimax_dependence.F`, `minimax_ini.F` | Procedure maps and selected leading declarations/table structure, 24–57 and 1–45. The 46,260 combined lines, principally coefficient/initialization material, are not deeply analyzed. |
| `bse.F` | Earlier driver preparation/reconstruction 345–401. Most kernel/eigensolver bodies unread. |
| `bse_driver.F` | Input availability/device sizing 552–584; coupled-block diagonalization 1390–1480; dispatch searches. Full accelerated kernels unread. |
| `bse_struct.F`, `bse.inc` | Complete 72-line descriptor file; precision-dispatch fragment 1–55. Remaining macro branches partial. |
| `bse_lanczos.F` | Method setup 255–305; recurrence/stop fragment 472–522; continued fraction and convergence measure 627–691. Full initial vectors, breakdown and reorthogonalization unread. |
| `bse_te.F` | Time-grid option/setup fragments 499–645. Evolution integrator and spectrum construction mostly unread. |
| `time_propagation.F` | Electronic preparation and field selection 153–283. Actual propagation/orthogonality control unread. |
| `mp2.F`, `ump2kpar.F` | Occupation, denominator and long-wave fragments 527–570 and 646–689. Complete energy/prefactor contracts unread. |
| `ump2.F` | Procedure/branch map only in this pass; distributed integral and energy bodies unread. |
| `ump2no.F` | Selected virtual-state denominator/filter 687–749. Natural-orbital diagonalization, truncation and output unread. |
| `lt_mp2.F` | Basis-cutoff extrapolation 1545–1573. Laplace-transformed overlap and energy kernels unread. |
| `rnd_orb_mp2.F` | Statistics reset 88–125; aggregation/extrapolation 156–204. Sampling law, independence and variance estimation unread. |
| `rpax.F` | Conditional empty entry 75–107 plus build/procedure map. Compiled correlated solver bodies unread. |
| `rpa_force.F`, `rpa_high.F` | Build-dependent stubs and storage 60–187; band restoration 485–549. Full analytic correlation forces unread. |
| `auger.F` | Carrier-density calculation 2552–2591. Four-state rate kernel, energy conservation and sampling unread. |

## State preparation and screening are method-dependent

Method selection resets and sets several independent state flags, separating
response construction, screened-interaction updates, quasiparticle changes,
real-space methods and electron–hole calculations (`chi_glb.F` sampled ranges).
A method label alone does not define what is held fixed between iterations.
The conventional driver recalculates occupations in selected branches, adjusts
the chemical potential under explicit conditions, synchronizes waves and can
merge near-degenerate eigenvalues before forming Hartree/kinetic and exchange
components (`chi.F` 477–571). Later quasiparticle paths can rebuild reciprocal
layouts and wave storage (2045–2128).

The response kernel selects occupied/unoccupied or positive/negative imaginary-
time states, forms pair densities including optional one-center contributions,
applies phases and extracts reciprocal coefficients (`chi_base.F` 335–403).
Its frequency helper distinguishes complex-frequency and broadened real-axis
weights; compile-time response conventions also change denominator signs
(689–776). The sampled later purely imaginary-frequency branch is subsumed by
the earlier condition, so comments near it cannot establish a separate active
integration method.

Dielectric conversion multiplies response rows and columns by square roots of
the Coulomb factor and adds the identity, with separate long-wave head/wing
handling (`chi.F` 3870–3921). At Gamma, the sampled inversion constructs and
inverts direction-specific matrices before averaging; elsewhere it directly
inverts the reciprocal matrix with checked factorization/inversion status
(4356–4437). A separate Hermitian response inverse discards eigenvalues below
an absolute threshold (`chi_base.F` 2850–2895). That restricted inverse and an
ordinary matrix inverse have different meanings.

A local tensor-index concern is visible in the Gamma inversion: the six
assignments intended to clear off-diagonal head entries repeat one index pair
and omit its transpose (`chi.F` 4417–4418). Initialization and subsequent
consumers must establish whether the omitted slot matters. This is not an
observed anisotropic-response failure.

Screened-interaction storage maps reciprocal and band indices and accumulates
higher-precision input into a lower-precision complex array (`screened_2e.F`
382–434). The potential cache loads on demand, validates reciprocal coordinates
and sizes, applies grid and long-wave scaling and reconstructs symmetry-related
matrices with phases and optional shared-memory synchronization (`wpot.F`
311–443). Restart compatibility therefore depends on more than matrix dimensions.

## Imaginary-time methods and analytic continuation

The two sampled real-space drivers reject noncollinear calculations and impose
method-specific reciprocal-group restrictions. Finite-temperature paths also
restrict occupation smearing and constrained spin populations (`chi_GG.F`
262–282; `chi_super.F` 251–282). These restrictions should remain specific to
those routes. The Green-function dispatcher distinguishes independent-particle
and correlated construction and rejects self-consistent constrained screening
in its sampled branch (`greens_real_space.F` 157–266).

Imaginary grids have separate time, bosonic and fermionic components, with
transform and conjugate-transform matrices and associated error quantities
(`minimax.F` 61–180; `minimax_struct.F` 28–80). Process selection uses divisibility
and layout constraints (`GG_base.F` 541–601). The interval fitting machinery and
large coefficient tables need their own derivation/provenance study. Neither
the tables' size nor recorded fit errors establish physical observable accuracy.
The inspected scalar reciprocal helper explicitly returns zero near its origin,
including in the derivative helper (`minimax_functions1D.F` 42–70); active
caller domains remain to be traced.

The sampled quasiparticle estimate evaluates a rational continuation near a
reference energy, differentiates using a fixed energy step and one of three
stencils, and forms a renormalization factor from one minus that derivative
(`pade_fit.F` 1543–1610). Ill-conditioning can enter both the continuation and
that denominator. Agreement at imaginary-frequency samples does not establish
stable real-axis poles or derivatives.

The alternative root helper expands a bounded bracket search, uses Brent
roots, selects the root nearest its supplied reference and returns sentinel
values if it finds no candidate (1694–1780). It then evaluates the continued
self-energy and slope at the selected root. This is a concrete root-selection
policy, not a proof of a unique physical quasiparticle. Causality, pole artifacts,
multiple roots and propagation of the failure sentinel are later questions.

## Correlation energies and target spaces

The sampled RPA trace is computed from response eigenvalues through a logarithm
plus its linear correction; a second-order or linear contribution is accumulated
alongside it (`acfdt.F` 467–526). In the non-second-order branch, eigenvalues
that make one minus the eigenvalue too small are reported and their terms
skipped. The structure-factor helper has the same local omission behavior
(`esf.F` 698–722). Thus a finite reported sum does not by itself establish an
admissible dielectric spectrum. Coupling-constant scaling and the domain check
also need to be considered together.

Constrained-screening weights come from diagonal entries of a correlated-space
projector, with threshold-selected band bounds (`crpa.F` 1493–1586). The sampled
trace diagnostic only checks whether the trace is near zero; it does not check
equality to the intended target rank. The full projector, disentanglement and
subtraction algorithms remain unread. This connects directly to the localized
study's rank and gauge questions.

The local model self-energy takes the density magnitude and floors it before
evaluating its density-dependent expression (`gw_model.F` 476–513). The required
dielectric/model-parameter domain remains unproved. This approximation should
be distinguished from a calculated frequency-dependent screened interaction.

## Electron–hole spectra and time evolution

The main driver selects older and newer BSE implementations according to solver
choice, with separate spin dispatch (`chi.F` 1206–1270). The newer driver has
an explicit device-memory decision and branches for resonant/antiresonant
blocks. Its coupled route diagonalizes one block combination, transforms the
other, diagonalizes again and takes square roots (`bse_driver.F` 552–584,
1390–1480). Stability and positive-domain assumptions in those helpers remain
unread. Precision is also a build choice in `bse.inc`.

The sampled Lanczos entry resets a requested beyond-resonant approximation to
its supported resonant treatment (`bse_lanczos.F` 277–298). The recurrence checks
consecutive-vector orthogonality and periodically compares spectra at successive
recurrence lengths; it stops based on an average error over the first three
components (472–522). The measure is RMS change in the imaginary spectrum
(671–686), not a direct eigenpair residual or error bound for every tensor
component. Continued fractions include spectral broadening (627–664).
Exact Krylov breakdown and zero initial oscillator-strength cases remain open.

There are distinct BSE time-evolution and electronic time-propagation files.
Only setup was sampled. The electronic route reconstructs charge/potential
and, if either Hartree or XC feedback is requested, enables both in the sampled
selection (`time_propagation.F` 208–245). Its local restrictions and complete
propagator deserve a separate pass; a time-evolution name cannot imply a common
integrator or the same physical approximation as the BSE route.

## Perturbation theory, statistics and derivative workflows

Sampled second-order kernels filter occupied/virtual states, apply negative
excitation-energy denominators and construct long-wave corrections from
interband derivatives (`mp2.F` 527–570; `ump2kpar.F` 646–689). Their occupation
indices differ locally between the two implementations; equivalence requires
tracing the caller's reciprocal mappings and spin conventions, not assuming
that the files are interchangeable. Natural-orbital preparation adds virtual-
state filters before denominator application (`ump2no.F` 687–749).
Small-gap and fractional-occupation domains remain unresolved.

The Laplace-route extrapolator fits energy linearly against cutoff to the power
minus three halves and takes the intercept (`lt_mp2.F` 1545–1573). Its local
formula requires distinct effective abscissae; extrapolation is an asymptotic
model whose applicability needs evidence. The stochastic route sums energy
samples over time/transfer indices and adds reported error estimates in
quadrature, including the direct and exchange totals (`rnd_orb_mp2.F`
156–204). Independence, covariance and estimator bias were not established;
statistical error is separate from basis and quadrature error.

The `rpax.F` entry is empty in the sampled build branch for Gamma-real builds
or missing MPI/ScaLAPACK support (75–107). The actual correlated solver in its
other branch is unread. Likewise, `rpa_force.F` contains empty interfaces when
ScaLAPACK support is absent (73–156), while band restoration in the supported
workflow rebuilds descriptors, copies waves and resets exchange data
(`rpa_high.F` 485–549). Complete correlation forces remain a substantial future
study. The sampled Auger helper establishes carrier-density conventions only:
energy or occupation selection, Fermi factors, reciprocal weights, spin factor
and volume normalization (`auger.F` 2552–2591); it does not establish the rate.

## Execution targets and returns

CPU, NVIDIA GPU and AMD GPU acceptance will need distinct workloads for each
algorithm actually selected. The sampled code combines FFT pair densities,
large response matrices, distributed eigensolvers, mixed storage precision,
analytic continuation, shared-memory caches and device-memory decisions.
A successful ground-state run proves none of these workflows. No all-target
capability, performance or agreement is demonstrated here.

Useful later passes separate screening/long-wave limits, Green-function grids
and continuation, electron–hole solvers, deterministic/stochastic correlation,
and analytic forces. Return questions include the head index assignment,
skipped trace terms, constrained-projector rank, quasiparticle failures and
root identity, Krylov breakdown, occupation mappings and statistical covariance.
Public contracts, complete tables and every unread body remain follow-up work.
The broad reference campaign and replacement design still follow these reports.

## Review disposition

The [single independent review](reviews/many-body.md) checked representative
scientific, control-flow and build claims and found no warranted correction.
It confirmed the inventory scope without treating it as completed analysis.
The unresolved questions above remain open; no calculation was run.
