# Independent review: XC first pass

Reviewed 2026-09-24 against quarantined VASP 6.5.1. This is one review at
depth one. No subagents, compilation, numerical execution or private data
copying were used. The descriptions below are original prose.

## Findings

One narrow correction is warranted in the external-library section. The
statement that lack of an energy capability sets the energy contribution to
zero should identify that contribution as the direct library result. In the
sampled GGA exchange branch, the temporary library energy is zeroed, but the
subsequent exchange composition can retain a local-energy contribution when
the local and gradient exchange fractions differ (`xc_driver.F` 503–513).
The meta-GGA branch directly scales its zeroed library energy (2403–2411).
The report should avoid implying that the entire composed energy must vanish.
This is a correction to the report's scope, not a demonstrated runtime defect
or a claim that every possible combination is accepted by the selector.

No other substantive correction was identified in the sampled claims. The
report accounts for all ten files in the inventory and explicitly leaves most
elementary kernels and complete workflow combinations for subsequent study.

## Assessed claims

The component record supports the report's description of separate component
identities, coefficients, parameter arrays, mixing fractions and requests for
additional density fields (`setex_struct.F` 49–106). Weighted accumulation is
present in the sampled scalar GGA and meta-GGA drivers (`xc_driver.F`
567–577, 2465–2474). Functional push/pop changes the external exchange fraction
and screening state, reinitializes the screened helper and conditionally
replaces device state (`setex.F` 1619–1693). The report appropriately leaves
the callers and restoration of derived tables unresolved.

The local table setup constructs spline coefficients and preserves the
functional record used to build the table (`setex.F` 1029–1080). The sampled
validity check compares component count and identities only (`ldalib.F`
33–50). Its limited comparison does not establish a reachable stale-table
failure. Core inclusion, a density floor, polarization endpoint handling,
range monitoring and the communicator maximum are present in the local spin
evaluator (68–170, 211–279).

The sampled GGA kernel has several distinct enhancement branches and explicit
derivative expressions (`ggalib.F` 372–515). The regularized meta-GGA exchange
kernel combines density, gradient and kinetic density, then selects different
interpolation branches (`mggalib.F` 3297–3448). These source observations
support the stated complexity without validating the formulas. The report
does not claim that it derived those kernels or verified their limiting
behavior.

The grid derivative construction includes normalization, reciprocal-space
multiplication, frequency truncation and removal of unbalanced modes
(`fexcg.F` 221–267). Its noncollinear route projects gradients and kinetic
density along a magnetization direction with a bounded inverse magnitude
(558–619, 646–655). The pointwise boundary applies different conversions to
density, gradient, Laplacian and kinetic-density inputs and returned operator
coefficients (683–738). Energy accumulation, valence-potential contraction,
kinetic correction and the core-inclusive stress expression are distinct
(1233–1337). The local evaluator also accumulates a separate core contraction
(`ldalib.F` 211–279).

The inspected local higher-derivative helpers use finite differences with a
fixed relative step. In the polarized helper, both spin perturbations scale
with the larger spin density (`ldalib.F` 2716–2755, 2938–3020). This supports
the report's open questions about low-density domains, endpoints, step
sensitivity and mixed-derivative symmetry. It does not establish an observed
failure at a response consumer.

The potential-only mBJ branch supplies a separate local-density energy
expression (`xc_driver.F` 1962–1983). The distinction and the limitation on
energy-consistent ionic relaxation are also supported by the
[public meta-GGA documentation](https://vasp.at/wiki/METAGGA), consulted
2026-09-24. The global mBJ parameter update combines grid and one-center
contributions, bounds the result and resets accumulated values; the local
variant mixes auxiliary grid and atomic fields (`mbj.F` 421–558).

Libxc setup creates both spin variants, checks capability flags, rejects
selected choices and changes handling with the library version (`setex.F`
788–882). The meta-GGA evaluation bounds densities, gradients and kinetic
density, can enforce an additional gradient-related kinetic bound, and writes
bounded gradient values back to dummy arguments (`xc_driver.F` 2377–2420).
Its invariant-to-gradient derivative conversions support the report's
interface concern. Caller-dependent consequences and component ordering
remain open, as stated.

The Hubbard dispatcher constructs occupations using all-electron radial
overlaps and selects correction variants (`LDApU.F` 299–403). The sampled
effective-interaction variant adds an occupation-dependent operator and
returns its orbital energy less the operator contraction (911–1025).
Magnetic constraints rotate and integrate weighted moments, perform grid
reductions, distinguish target interpretations and treat small moments
separately (`constrmag.F` 37–133, 468–665). Penalty and band-sum correction
bookkeeping are distinct (714–772). The report correctly leaves derivatives
of the spatial weights for later work.

## Review limits

This review checked selected material claims and their citations. It did not
independently audit the author's entire reading history, derive all
functionals, validate a complete composite energy, establish force or stress
consistency, analyze every response consumer, build Libxc, or compare scalar,
SIMD, CPU, NVIDIA and AMD execution. The report's return conditions remain
appropriate. No additional review round is requested.
