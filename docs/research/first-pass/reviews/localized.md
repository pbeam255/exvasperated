# Localized orbitals, interpolation and embedding first-pass review

Reviewed 2026-09-24 against quarantined VASP 6.5.1 and the
[first-pass report](../localized.md). This is the requested single independent
review at depth one. No child review, build or scientific experiment was run.

## Correction required

**Add the immediate restrictions and termination of the sampled embedding
method.** The helpers discussed in the report belong to the second embedding
method, selected at `embed.F` 204–207. Its entry rejects more than one spin
channel or more than one reciprocal point (439–444). Its body invokes the
entangled/complement SVD only when the occupied-state count exceeds the selected
embedding-state count; otherwise it uses an identity transformation (493–500).
After producing its orbital and projector outputs and cleaning up, it explicitly
terminates execution (550–605). Add these facts to the embedding paragraph and
extend its reading-scope entry accordingly. They materially qualify how this
particular construction participates in a workflow. The local guard checks
point count; it does not itself verify that the single point is Gamma. Keep
these observations specific to this method.

## Material claims checked

- **Trial states and subspace transformation.** `locproj.F` 124–161 supports
  automatic orbitals, full reciprocal sampling and the conditional polarization
  setup request. Lines 726–734 support the PAW-metric trial overlap. Lines
  1040–1108 support the band-count requirement, weighted overlap, SVD status
  checks and product of singular vectors without singular-value scaling.
  The stated polar-factor interpretation is consistent with that product.
  There is no small-singular-value rejection in this sampled body; the report
  appropriately leaves earlier checks and physical effects unresolved.
- **Separate orthogonalization.** `locproj.F` 2346–2424 supports selection of
  the first reciprocal point, PAW overlaps, inverse square-root scaling,
  thresholded zero directions and subsequent normalization. Its use of global
  band indices in arrays sized by the selected interval is visible at
  2348–2372. The callers at 1990 and 2177 both supply a lower band index of
  one. The report correctly describes a domain question without claiming a
  demonstrated error in those callers. `lcao_bare.F` 282–321 supports the
  separate radial density and atomic density-matrix iteration.
- **Localization adapter and gauge data.** `mlwf.F` 505–613 supports the
  projection alternatives, selected-column construction, excluded-band mapping
  and external/internal dispatch. Lines 542–553 support the spin-axis
  restriction for the sampled spin-matrix export. Lines 1233–1268 support
  reciprocal offsets, the polarization overlap helper and removal of excluded
  bands on both indices. Lines 1869–1909 support the compile guard, designated
  output-process call and distribution of transformation, window, center and
  spread data. The report does not claim this proves all build configurations.
- **Optimization and reproducibility.** `wannier.F` 849–865 and 989–1015
  support the cell-metric weights and phase-derived centers. `lie.F` 867–945
  supports skew-generator updates, matrix exponentials and the search choices;
  961–1024 supports the stopping branches and optional success result.
  `umco.F` 433–465 connects the seed helper to communicator process identity,
  and 816–825 combines that identity with a clock value. The stated
  reproducibility limitation is supported.
- **Operator interpolation.** `mlwf.F` 3612–3624 supports rotation of band
  energies into the chosen subspace. `wannier_interpol.F` 276–283 supports the
  optional band shift; 458–467 supports the coarse-to-real-to-requested-grid
  transformation and diagonalization. `wannier_mats.F` 609–619 supports the
  minimum-image phases, and 654–667 supports explicit Hermitian averaging and
  failure handling. Gauge, derivatives and between-grid accuracy remain
  correctly identified as unresolved scientific questions.
- **Embedding helpers and interaction exports.** `embed.F` 627–710 supports
  the SVD-based entangled/complement organization and PAW overlap helper, with
  the workflow qualifications above. `dmft.F` 417–490 supports conditional
  symmetry removal, layout reconstruction, Fermi-energy restoration, target
  alternatives, four-orbital allocations and augmentation/cutoff changes.
  `twoelectron4o.F` 99–109 and 164–172 supports the reciprocal-group parallel
  restriction and layout reconstruction. `fcidump.F` 90–123 supports the
  BLACS process restriction, insulating-occupation check and reciprocal
  mapping preparation. The report appropriately avoids inferring a complete
  many-electron solver or validated external format from these entries.
- **Inactive auxiliary-field route.** All of `afqmc.F` and `afqmc_struct.F`
  support the selection rejection, declaration-only propagation body and
  inactive default. No implemented solver through those files is established.
- **Population and density partitioning.** `k-proj.F` 135–139 and 244–274
  supports the unsupported-decomposition return and accumulation of squared
  plane-wave coefficients with communicator reduction. The active sampled
  accumulation contains no atomic augmentation. `sphpro.F` 1838–1846 and
  1894–1913 supports the occupation diagonalization, square-root absolute-value
  scaling in one helper and lack of local status checks. `stockholder.F`
  998–1041 supports core addition, iterative radial mixing and the summed
  convergence measure; 1077–1103 supports species averaging, core subtraction,
  integrated norms and their electron-count adjustment. The aggregate norm
  appears as an unguarded divisor locally; admissible inputs remain unproved.
- **Derivative import and parser.** `wap.F` 3299–3357 supports the separate
  structural dimensions, lattice transpose and HDF5 build restriction. The
  grammar's real-valued token field and the site's coordinate fields are
  single precision, while the final basis record's coordinates and radial
  width are double precision (`parser/locproj.y` 35–47,
  `parser/sites.hpp` 7–16, `parser/basis.hpp` 23–30). The scanner fallback
  ignores unmatched characters (`parser/locproj.l` 38–42). Global result
  storage, unchecked accessor indexing and Cartesian product assembly are
  visible in `parser/locproj.y` 138–200 and `parser/basis.cpp` 27–39.
  `parser/makefile` 3–22 confirms compilation of generated files with disabled
  regeneration rules. Equivalence of those generated bodies to the inspected
  grammar/scanner sources was not checked.

## Review limits

The inventory and reading-scope table cover the same 35 files, totaling 46,934
lines. This establishes navigation coverage only. The review checked the
substantive claims through selected bodies and immediate control flow; it did
not repeat every reported read or analyze all scientific methods, generated
parser bodies, serialization conventions or memory lifetimes.

No localization convergence, rank-deficient case, interpolation error,
embedding calculation, integral export, charge partition or CPU/NVIDIA/AMD
execution was tested. The report's open questions remain open. No proprietary
source, comments, diagnostics or datasets were copied into this review artifact.
