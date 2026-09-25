# Broad literature and reference campaign

2026-09-25. First acquisition expedition following the
[core program and routine outline](../core-program-outline.md), the
[first-pass source studies](../first-pass/README.md) and the user's request to
send parallel research agents. Three agents covered scientific families; the
coordinating agent covered computation, interfaces and synthesis.

## Scope and what comes next

**This broad pass informs the overall design. Before detailed design and
implementation of each individual subsystem, undertake a focused deep expedition
and scientific re-grounding for that subsystem.** Return to governing equations,
assumptions, errata, numerical methods, actual implementation bodies, interactions
and difficult scientific cases. References acquired here are starting material.
The focused work may be iterative and send us back to related areas.

No engine architecture, method or backend was selected. Researcher control of
calculation composition remains the boundary. Physical hysteresis, model memory,
algorithmic history and continuation need their own scientific treatment. CPU
and NVIDIA remain the alpha targets; AMD is the second wave.

## What was brought back

| Expedition | Outline coverage | Records | Local catalog assets | Report |
| --- | --- | ---: | ---: | --- |
| Computation and interfaces | Bucket 1; six core responsibilities | 23 | 23 | [Computation](computation.md) |
| Ground-state foundations | Buckets 2–8 | 29 | 47 | [Ground state](ground-state.md) |
| Dynamics, response and evolution | Buckets 9–11, 14 | 28 | 44 | [Dynamics and response](dynamics-response.md) |
| Localized, correlated and learned methods | Buckets 12, 13, 15 | 30 | 58 | [Advanced methods](advanced-methods.md) |
| **Total** | All 15 buckets have starting references | **110** | **172** | |

The catalog contains **59 acquired paper records, eight acquired documentation
records, 34 acquired implementation archives and two bounded dataset/reference
repository acquisitions**. Seven further records remain metadata-only or blocked.
There are **60 distinct acquired PDFs**: the paper full texts and a JTH validation
report classified as documentation. Other assets include license/README copies,
public documentation and limited dataset material. The 172 catalog assets total
about **1.20 GB**; unlisted local reading aids are additional.

Implementation examples include QE, ABINIT, GPAW, DFTK, Libxc, Spglib, DFT-D4,
i-PI, PLUMED, Phonopy, phono3py, Octopus, Wannier90, BerkeleyGW, Yambo, PySCF,
QUIP/GAP, MACE, NequIP and FLARE, alongside numerical and Rust/CUDA candidates.
The two dataset acquisitions are a small JTH hydrogen sample with generator
input, and the GW100 author repository. This is not a complete atomic-data or
benchmark collection. Not every acquired source is open source: the separately
licensed GAP snapshot has noncommercial terms, as detailed in the advanced report.

### Where things live

- Original reports and [JSON catalogs](catalogs/) are tracked in Git.
- Papers: ignored `papers/exvasperated/{area}/`.
- Inert source, public documents and limited data: ignored
  `quarantine/references/{area}/`.

Every catalog asset records its source URL, relative path, byte size and SHA-256.
Source records identify full commits or releases. Paper versions, journal DOIs,
inspection depth and observed terms are recorded separately. Future retrieval
should verify the hash; a live URL or branch may change. Auxiliary text
extractions are local reading aids, not additional references.

**No acquired program was installed, built or executed, and no scientific
calculation or benchmark was run.** Reading was selective; catalogs state the
sections and source paths examined. Downloading an archive does not establish
correctness, independence, reusable rights or subsystem readiness. No proprietary
VASP code or implementation text was incorporated into tracked artifacts.

## Findings that deserve to shape the next questions

1. **PAW needs formulation, atomic data and derivatives studied together.** The
   acquired formulation corrections and JTH validation identify overlap and
   density-domain issues that cannot be resolved by file-format compatibility.
   [Ground-state findings](ground-state.md#paw-correctness-spans-the-dataset-and-its-consuming-formulation)
2. **Errata can change the implemented equation.** Giustino's transport erratum
   corrects normalization and factors in the transport formulation. Keep the
   correction beside the review during the focused derivation.
   [Transport findings](dynamics-response.md#5-phonons-and-transport-depend-on-conventions-and-limiting-procedures)
3. **History and branch choices appear across routine families.** SCF,
   polarization, sampling, Wannier localization, quasiparticle roots and learned
   acquisition each have their own meanings. Similar final scalar values or
   coordinates can conceal a different calculation.
   [Dynamics](dynamics-response.md), [localized/correlated methods](advanced-methods.md)
4. **Numerical backends need operation-level evaluation.** Distributed FFT
   reshaping, generalized eigensolver metrics, stream/workspace behavior and
   wrapper API coverage are concrete questions. cuda-oxide provides enough
   specific capabilities to merit experiments; its label supplies no decision.
   [Computation findings](computation.md)
5. **Independent comparisons require matched science and known shared parts.**
   Codes can share XC libraries, atomic data or approximations. Observable-specific
   convergence and genuinely different constructions must accompany cross-code
   agreement. SSSP, the broad equation-of-state verification work and GW100 offer
   complementary starting points, with bounded coverage.
   [Ground-state comparisons](ground-state.md), [GW comparisons](advanced-methods.md)
6. **Code, datasets and models have different terms.** Current acquired Libxc is
   MPL-2.0; QUIP and GAP differ; pretrained models need separate assessment. License
   observations are tied to acquired versions and are not permission to adopt
   every bundled asset. [Ground-state terms](ground-state.md),
   [advanced-method terms](advanced-methods.md)

These are research findings and implications to investigate, not a completed
design or numerical acceptance criteria.

## Coverage and return order

All routine buckets have references, with very unequal depth. The core has
starting interface/execution references; restart semantics, downstream workflows,
external callback behavior and packaging need much more work. Quadrature, radial
numerics, root solving and random streams are lighter than FFT/eigensolvers.
Original PAW and stress derivations, relativistic/spin/orbital methods, several
XC/dispersion families, constrained motion, response extensions and correlated
force derivations remain substantial acquisition or reading work.

A useful dependency order for focused returns is representations/numerics and
atomic data; the stationary operator/electronic problem and derivatives; motion
and response; then specialized correlated/localized/learned methods, revisiting
shared pieces as needed. Execution and compatibility research should accompany
the scientific subsystem being studied. This is a proposed study order, not a
committed implementation sequence or an instruction to exhaust a topic in one pass.
The family reports identify concrete deeper readings, code paths and candidate
calculations. Beads epic **exv-8lk** tracks 15 routine-family expeditions and a core
interface/execution expedition; **exv-x34** retains the cuda-oxide evaluation.
The every-file VASP study remains
open independently of this acquisition.

## Acquisition gaps and verification

Full texts not acquired: original Blöchl PAW, Kresse–Joubert PAW,
Monkhorst–Pack, Nielsen–Martin stress, Hirshfeld partitioning, and the older
Castro–Marques–Rubio propagator article. Catalog notes distinguish unavailable
full text from fetch/TLS failures. Perturbo's source requires individual
registration; only public papers/documentation were acquired. No registration or
contact was performed. These gaps do not imply the references were fully read.

Checked: catalog structure and unique IDs; acquired-file existence, byte counts,
SHA-256, PDF headers and readable archive membership; ignored acquisition paths;
coverage of bucket numbers; local document links and whitespace. These establish
acquisition integrity and document consistency. Scientific verification awaits
the focused derivations and deliberately selected experiments.
