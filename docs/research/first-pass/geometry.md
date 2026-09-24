# Geometry, reciprocal sampling and symmetry

First pass, 2026-09-24. Study area: `geometry`, 14 files. This pass follows
coordinate conventions, state-dependent symmetry and the information required to
reconstruct reciprocal-space data. It is source inspection, without a build,
reference calculation or proof of the lattice algorithms.

## Reading scope and file roles

The [inventory](../vasp-source-inventory.csv) fixes the reference snapshot.
All files received declaration/procedure scans; body reading is bounded below.

| File | Body reading | Role and remaining depth |
| --- | --- | --- |
| `lattice.F` | 1-249 | Basis, reciprocal basis, volume and coordinate transformations. Caller validation remains open. |
| `lattice.inc` | 1-15 | Historical lattice record; active lattice types also arrive through the structure definitions. Build use of this include is untraced. |
| `lattlib.F` | 2619-2710 | Primitive-cell construction with coupled positional/vector information. Other lattice classification and reduction algorithms remain largely unread. |
| `mkpoints.F` | 498-515, 1080-1190, 1220-1320, 1510-1565; targeted normalization, tolerance and allocation searches | Explicit/generated reciprocal sampling, integer mesh transformations and symmetry reduction. General mesh enumeration and tetrahedra need deeper work. |
| `mkpoints_change.F` | 25-95, 328-397 | Saved/current sampling aliases, switching and descriptor regeneration. Every ownership transition is not traced. |
| `mkpoints_full.F` | 27-155, 1022-1225 | Reduced/full sampling state, plane-wave reindexing, translational phases and distributed reconstruction. Most rotation applications remain open. |
| `mkpoints_struct.F` | 1-166 | Sampling records, representative maps, spin/conjugation information and saved global pointers. |
| `rot.F` | 1-160; procedure map | Electronic optimization driver and line-search helpers, despite its geometry inventory assignment. Detailed treatment belongs with electronic solution. |
| `spinsym.F` | 228-276, 312-375 | Spinor rotation construction and application. Axis construction and complete magnetic-group handling remain open. |
| `stufak.F` | 1-166 | Species structure factors, virtual-crystal weights and host/device update boundary. |
| `supercell.F` | 9-290 | Replication maps, cell transforms and atom records coupled to wave/response state. Later reciprocal assembly remains unread. |
| `sym_grad.F` | 42-177 | Symmetries preserving a selected wavevector and preparation of gradient transformations. Application kernels remain unread. |
| `symlib.F` | 1-45, 461-546 | Shared symmetry tolerance and species-aware position matching preparation. Force, tensor and magnetic operations need deeper reading. |
| `symmetry.F` | 133-190, 705-805, 1545-1785, 1808-1845, 1880-1930, 2030-2280, 3305-3386 | Minimum images, primitive-cell state, symmetry filtering, alternate external-library branch and tolerance sensitivity. Many other bodies remain unread. |

The lifecycle call site `main.F` 1130-1170 was also checked. Scope above does
not imply complete understanding of every statement or a complete per-file study.

## Coordinate conventions are part of the numerical contract

The active lattice routine stores direct basis vectors in columns and forms a
reciprocal basis without the angular factor: mathematically, if the direct basis
is \(A\), the stored reciprocal basis is \(A^{-T}\). The signed determinant
provides the volume used in that construction. Conversion routines apply the
appropriate basis or its transpose to real and complex coordinate data
(`lattice.F` 22-73, 139-248).

This means a physical reciprocal vector in a plane wave requires the angular
factor elsewhere. The independently stated convention
\(G=2\pi A^{-T}n\), for integer coordinates \(n\), must be kept distinct from
the stored basis. A factor or transpose error can survive visually reasonable
structures and only emerge in energies, phases or derivatives.

No singular-cell guard precedes division in the inspected lattice constructor.
This is an unresolved caller precondition, not evidence that accepted inputs
can reach division by zero. The small wrapping helper uses a finite offset and
Fortran remainder; its useful input range should not be generalized to arbitrary
unwrapped coordinates. Minimum-distance selection is a separate operation.

In particular, the minimum-image constructor in `symmetry.F` 133-190 enumerates
a bounded neighborhood of supercell translations, groups distances within a
tolerance and assigns equal weights to the retained images. It uses a fixed
temporary capacity. The admissible cell shapes and upper bound on degeneracy
are not established here. A general nearest-image guarantee for arbitrarily
skew cells would require additional reasoning or a caller restriction. This
matters later for interpolation and lattice dynamics, where degenerate images
can contribute different phases.

## Symmetry belongs to the declared calculation state

The examined internal symmetry path starts from the lattice, atomic species and
positions, then imposes further conditions from velocities, selective motion,
magnetic moments and selected response settings. A geometry-only space group
does not describe every operation usable by the calculation.

The selective-motion path constructs trial vectors, symmetrizes them and removes
forbidden components before further symmetry analysis (`symmetry.F` 1744-1785).
The role of random-number state and the sufficiency of this detection procedure
remain open; source calls alone do not establish a run-to-run discrepancy.
Collinear and noncollinear magnetic cases take different paths, with axis
transformations and field-related information entering the latter analysis
(1808-1930). The selected response mode can further restrict operations
(2030-2118). These are parity questions about combinations of settings, not just
whether spatial symmetry exists.

There are compile-time alternatives, including an external symmetry-library
branch (2145-2280). That branch receives a transposed lattice representation,
types, coordinates and a tolerance, then adapts returned maps and operations.
The rest of its magnetic/dynamic filtering has not been compared with the
internal branch. Interchangeability is not established by their common purpose.

Tolerance is not a single universal number. The shared symmetry state and the
mesh construction/lookups use distinct tolerances in the examined source.
Some comparisons concern positions; others concern closeness to integer mesh
relations. Their units, scaling and sensitivity need consumer-specific analysis.
The sensitivity helper rebuilds symmetry at three tolerance levels and restores
the scalar tolerance (`symmetry.F` 3305-3386). Its main-driver caller is inside a
debug build branch and immediately performs the final symmetry initialization
again (`main.F` 1140-1159). Consequently, the helper's mutation of symmetry state
does not by itself demonstrate stale final symmetry at that call site.

## Reduction must retain enough information for reconstruction

The sampling records retain considerably more than representative points and
weights: equivalence maps, real/reciprocal rotations, translations, spin action,
conjugation flags, phases and local/global plane-wave indices all appear in
`mkpoints_struct.F`. Time inversion and spatial inversion cannot be treated as
an interchangeable Boolean throughout the program.

For explicit points, the inspected reader rejects a zero total weight and
normalizes weights (`mkpoints.F` 498-515). Generated meshes additionally involve
commensurability with the reciprocal lattice, integer matrix normal forms,
rotation compatibility and possible enlargement of the operation set by time
inversion (1080-1320). Initial allocation sizes are not necessarily hard limits;
growth paths exist. The general integer algorithms and tetrahedron orientation
still need independent mathematical examination.

The full-zone reconstruction sample shows why equal final point counts are
insufficient evidence of correctness. For each reconstructed point it maps
rotated reciprocal indices onto the distributed grid, checks that destinations
exist, retains source indices and forms translation-dependent phases. It also
checks distributed plane-wave counts (`mkpoints_full.F` 1100-1225). These checks
can detect missing destinations while still leaving phase convention, spin
action and conjugation correctness as separate obligations.

Spinor rotations are built through a small eigenproblem and applied to paired
spin components with an adjoint action (`spinsym.F` 228-276, 312-375). One
eigensolver failure path stops directly. The sampled reciprocal application
rejects a particular spin-flip case; this does not establish which higher-level
workloads can reach it. Complete antiunitary handling needs the electronic,
noncollinear and response consumers.

## Geometry changes invalidate numerical state

Changing reciprocal sampling uses saved pointer sets and shallow descriptor
copies, followed by rebuilding selected grid/wavefunction information. The
sampled regeneration path requires a single rank in one band communicator and
has an early return in the real-only build (`mkpoints_change.F` 328-397).
These constraints must be interpreted at the caller before claiming support or
non-support for a user workflow.

The key unresolved lifetime question is which arrays, plans, maps and device
copies must be rebuilt together. Full-grid regeneration explicitly deletes and
recreates mapped data. The structure-factor path computes on the host and updates
device data when present. Spin rotation contains accelerator loops and temporary
storage. These observations identify CPU/NVIDIA/AMD obligations, but do not prove
that each path is built or correctly synchronized on all three targets.

The supercell helper is also method-coupled: its records contain wave, response
and augmentation state, and some operations depend on distributed linear algebra.
Its inspected construction uses either diagonal replication or an integer cell
transform, validates the number of distinct translations and preserves parent
atom indices and motion constraints (`supercell.F` 96-290). This is useful
evidence for downstream response/many-body studies; it is not a general-purpose
cell-construction contract to adopt unchanged.

## Scientific checks suggested by the reading

These are deductions and future study questions, not executed tests. Coordinate
round trips must respect the chosen basis convention. Integer lattice
translations leave species structure factors unchanged, and the zero reciprocal
component gives the species count times its virtual-crystal weight, following
the phase sum in `stufak.F`. Reduced and full-zone calculations should agree on
appropriate observables when phases, weights and spin transformations are used
consistently. Near a symmetry threshold, changing classification can be legitimate;
the question is whether downstream state stays internally consistent and the
observable converges under the declared physical model.

Useful later cases include skew cells, coincident minimum images, nonsymmorphic
operations, noncollinear states, constrained ions and sampling changes across
restart. Analytic identities, independent implementations and actual scientific
calculations will answer different parts of those questions.

## Return conditions

Return with representation for layouts, Fourier conventions and map lifetimes;
with electronic solution for `rot.F`, magnetic symmetry and wavefunction
transformation; with response/vibrations for selected-wavevector symmetry and
minimum-image phases; and with ions for moving-cell invalidation. The inventory
is left unchanged: the misplaced electronic optimization file is explicitly
cross-referenced rather than silently counted as deeply analyzed geometry.
Lattice classification, general mesh enumeration, all alternate symmetry builds
and complete per-file analysis remain open after this useful first pass.

## Review disposition

The [single independent review](reviews/geometry.md) checked the substantive
claims and reported no corrections. Its bounded scope is recorded separately.
No second review round was requested.
