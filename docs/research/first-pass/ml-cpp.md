# Machine-learned force fields: C++ descriptors and prediction

Reference: quarantined VASP 6.5.1, inspected 2026-09-24. The `ml_cpp` partition
contains 162 files and 64,795 lines. The [inventory](../vasp-source-inventory.csv)
identifies the snapshot. No source, diagnostic prose or fixture was adopted;
no library build, prediction or test was executed.

## Scope and interpretation

This pass follows prediction from host adapters through environments,
descriptors, kernels and energy/force/stress assembly. It also samples shared
memory, numerical dispatch and existing tests. Much of the partition consists
of support files and large test-data headers; their presence does not establish
scientific coverage. The per-file scope register below explicitly leaves
unread bodies and fixture values for later study.

Unless otherwise stated, short C++ filenames below are under
`vaspml/src/libvaspml/`; `vaspml.F` is at the source root.

## Entry points do not imply the same execution path

The Fortran-facing C interface creates and destroys an opaque frame, imports
the host communicator, reads a model, converts its units, prepares radial and
angular basis objects, and initializes the frame with a CPU execution choice
(`InterfaceVASP.cpp` 20–32, 97–148). Each update rebuilds descriptors, then
kernel and predictions, then stress. The foreign interface passes dimensions,
arrays and type mappings explicitly (`vaspml.F` 58–196). Lifetime, indexing
and exceptions crossing that boundary need a complete caller audit.

A separate NVIDIA-oriented application explicitly chooses the GPU policy for
frame and kernel (`vaspml/src/applications/vaspml-predict_nvidia.cpp` 114–137).
That source is evidence of a distinct route, not proof that the host adapter
uses it or that the application runs successfully. Policy macros can remove
GPU-branch bodies when parallel-standard-library support is disabled
(`ParallelEnvironemt.hpp` 10–46). Build selection is therefore part of the
observable method path.

The external dynamics adapter has another contract. It maps host type names
to model types and rejects unknown nonempty names (`InterfaceLAMMPS.cpp`
178–246). It consumes externally supplied neighbor lists, masks and sorts
neighbor indices, applies its own cutoff, converts distances to internal units,
and normalizes displacement vectors (397–478). Its sampled distance branch
has no local positive-distance guard before normalization; the internal
neighbor builder does. Host guarantees about self pairs, coincident atoms,
ghosts, type subsets and communication must be established separately.

## Geometry and descriptor meaning

The internal direct-coordinate neighbor path computes image bounds from the
lattice, loops over images and atoms, and stores distances and displacement
vectors for pairs inside the cutoff and above a small-distance threshold
(`nearest_neighbor.cpp` 144–235). The lattice inverse divides by the signed
determinant, whereas volume is its absolute value (`Lattice.cpp` 119–151).
Singular and near-singular cells, orientation and image completeness require
caller/domain checks not established here.

The radial projection combines a grid, a broadened radial factor, spherical
Bessel functions, cutoff values and radial integration weights
(`BasisFunctionsRadialSpline.cpp` 290–340). It then builds splines using
origin-derivative information (396–451). The spline core supports endpoint
derivative or natural conditions through a sentinel policy and assumes enough
distinct abscissae for its divisions (`cubic_spline.hpp` 164–214). Grid,
root and interpolation errors are separate from regression error.

Cutoff choices alter differentiability. The sampled hard-cutoff branch returns
zero derivative even at its jump; other branches supply analytic taper
derivatives (`cutoff.cpp` 114–196). This describes the implemented convention,
not a proof of a differentiable energy at every neighbor-list transition.
Some input/size checks in this routine are compiled only at a debug level.

The frame dispatches between a standard and a reduced angular descriptor
(`Frame.cpp` 216–279). The standard single-atom contraction sums products over
magnetic components for selected radial/angular/species combinations and
applies feature weights (`DescriptorSHS3.cpp` 89–124). A sampled preparation
in the reduced route sums coefficient blocks over element types
(`DescriptorSHS3ReducedLinElem.cpp` 101–130). This does not establish that
the full reduced descriptor discards all species information. The full
feature definitions, sparsity lists and derivative contractions remain open.

The descriptor collector forms a norm from weighted squared component norms.
For a normalized component above the threshold, it scales by the square root
of the component weight divided by the combined norm. Below the threshold,
the sampled packing branch skips both transformation and length advancement
(`DescriptorCollector.cpp` 136–183). Buffer initialization and subsequent
consumers determine whether that case is valid; no stale-data failure is
claimed. The polynomial kernel separately guards its inverse-norm factor and
forms powers and derivative factors (`KernelPolynomial.cpp` 143–177).
Normalization, packing and differentiation must be checked together.

## Prediction quantities and statistics

Prediction uses type-mapped reference coefficients and restores energy offsets
according to the selected convention: species reference energy alone, or that
reference plus the mean training-energy contribution (`Predictor.cpp`
647–754). A matching raw kernel contraction does not establish matching total
energy unless offsets and normalization also match.

Force preparation builds derivative matrices and contractions before stress
is permitted. The CPU stress path uses pair-force/displacement contributions
with negative inverse volume, then copies symmetric tensor entries
(`Predictor.cpp` 677–699, 900–969). The host wrapper zeros and accumulates
local force contributions, rescales them, and sums across ranks; energy and
stress have separate conversions and reductions (`vaspml.F` 433–455,
507–536). Full sign/unit agreement and conservative derivatives remain to
be derived across the interfaces.

The local-environment coverage measure uses a kernel inverse and a quadratic
form, then takes the magnitude of the residual from unity and caps it at one
(`SpillingFactor.cpp` 68–126). That magnitude/cap can obscure the sign and
size of an inadmissible raw residual. It is not automatically a calibrated
force-error estimate.

The statistics helper computes per-type minima and maxima, but the sampled
overall minimum and maximum are taken from the vector of **type averages**;
the overall mean also averages those type averages without atom-count weights
(`SpillingFactor.cpp` 129–154). These are distinct from extrema and a mean
over all atoms. Which consumers expose or rely on those summaries remains
unresolved; this pass demonstrates the local definitions only.

## Numerical and storage obligations

The non-NEC CBLAS inverse helper continues through factorization and
inversion without active handling in its positive-status branches; the NEC
branch throws instead. Its
cuBLAS-conditioned alternative is empty (`Linalg.hpp` 610–651). Consequently,
the coverage-measure path cannot be assumed equivalent across those builds.
Reachability, library selection and callers need tracing before attributing
an observed prediction failure. These observations do not show that every
GPU prediction needs this inverse.

Shared arrays choose ordinary allocation or communicator-based storage and
release the corresponding resource (`ShmemArray.hpp` 182–220). In one MPI
branch only the shared-group root allocates bytes and other ranks query its
window (`MlMPI.hpp` 1051–1077). Explicit release clears the ownership flag;
the communicator object's destructor also checks that flag before freeing
(`MlMPI.cpp` 174–217). Copy/move behavior, collective destruction order,
window visibility and exception paths remain open. A C++ destructor alone
does not prove collective lifetime correctness.

The model reader compares text-header and binary versions and rejects an
unsupported newer version (`IoHandlerML_FF.cpp` 45–76, 674–691). A local
header-delimiter guard requires its position to equal both zero and the
not-found sentinel, so that particular condition cannot trigger. Parsing and
later checks may still reject bad input; their completeness is unproved.
Unit conversion also rescales model targets/weights (782–795). Full binary
format, truncation, endian and dimension contracts remain future work.

## Builds, existing tests and target requirements

The top-level Make route builds a library, applications and benchmarks from
separate subdirectories (`vaspml/makefile` 1–55). The sampled CMake file uses
machine-specific include locations and refers to a source directory and an
application source absent from this local tree (`vaspml/CMakeLists.txt`
50–64, 110–112). It is not sufficient evidence of a usable alternate build.
The NVIDIA compiler template alone also does not enable all the GPU-related
policy macros (`vaspml/arch/makefile.include.nvhpc`). No build was attempted.

Sampled tests compare angular descriptors against stored target arrays and
compare direct/Cartesian neighbor construction against stored indices,
distances and vectors (`vaspml/test/src/libvaspml/test_DescriptorSHS3.cpp`
31–114; `test_NeighborList.cpp` 23–87). A model I/O test checks selected
round-trip quantities (`test_io_ML_FF.cpp` 360–363). These are useful
comparison shapes, but the full fixtures, tolerances and target provenance
were not audited. Large expected-value headers are not independent validation.

One generator uses an external special-function implementation and automatic
differentiation for angular reference values
(`vaspml/test/tools/create-test-data-sphericalHarmonics.py` 42–75).
Its coordinate conversion divides by radial and transverse norms, leaving
origin/axis domains to examine. Neither generator nor generated fixture was
run or imported into this project.

CPU, NVIDIA and AMD alpha work will need actual prediction, derivative,
multi-species, model-reading and distributed-host workloads on each selected
backend. The sampled source demonstrates CPU/NVIDIA-specific mechanisms;
it does not establish AMD coverage, equivalent failure handling or performance.
This study chooses no replacement descriptor or execution technology.

## Returns

Return with the Fortran report to derive descriptor and force/strain equations,
compare unit and energy conventions, and trace identical models through each
entry point. Other questions are threshold/empty-environment behavior, species
subsets and ghost ownership, coverage-statistic consumers, inverse-helper
reachability, model parsing, build viability and collective lifetime. Complete
unread files and fixture provenance remain later per-file work. Public
interface contracts and independent references belong to the subsequent
research campaign.

## Review disposition

The [single independent review](reviews/ml-cpp.md) confirmed the representative
claims and all-file register. It identified one missing qualification: the
unchecked CBLAS inverse path excludes the NEC branch, which throws. That
qualification is now explicit. No second review or experiment was performed;
unresolved domains and unread material remain follow-up work.

## Per-file scope register

Paths in this register are relative to `src/`. “Map” means only the declaration
or procedure map was sampled; “inventory only” means contents were not read.
Neither establishes complete analysis. “Selected bodies” refers to the
locations discussed above, not to the whole file.

| File | Scope |
| --- | --- |
| `vaspml/.clang-format` | Inventory only; contents unread. |
| `vaspml/CMakeLists.txt` | Build contents read; not executed. |
| `vaspml/arch/makefile.include.gnu` | Inventory only; contents unread. |
| `vaspml/arch/makefile.include.intel` | Inventory only; contents unread. |
| `vaspml/arch/makefile.include.nec_aurora` | Inventory only; contents unread. |
| `vaspml/arch/makefile.include.nvhpc` | Compiler template read; not executed. |
| `vaspml/arch/makefile.include.vasp` | Inventory only; contents unread. |
| `vaspml/bin/.gitignore` | Empty file in inventory. |
| `vaspml/build/.gitignore` | Empty file in inventory. |
| `vaspml/doc/Doxyfile` | Inventory only; contents unread. |
| `vaspml/doc/header.html` | Inventory only; contents unread. |
| `vaspml/doc/makefile` | Inventory only; contents unread. |
| `vaspml/include/.gitignore` | Empty file in inventory. |
| `vaspml/lib/.gitignore` | Empty file in inventory. |
| `vaspml/makefile` | Build targets read; not executed. |
| `vaspml/res/makefile.common` | Inventory only; contents unread. |
| `vaspml/src/applications/makefile` | Inventory only; contents unread. |
| `vaspml/src/applications/mlab2json.cpp` | Inventory only; contents unread. |
| `vaspml/src/applications/test_MultiType.cpp` | Inventory only; contents unread. |
| `vaspml/src/applications/test_cublas.cpp` | Inventory only; contents unread. |
| `vaspml/src/applications/test_linalg.cpp` | Inventory only; contents unread. |
| `vaspml/src/applications/test_linalg2.cpp` | Inventory only; contents unread. |
| `vaspml/src/applications/test_mpiSHMEM.cpp` | Inventory only; contents unread. |
| `vaspml/src/applications/test_predict_mpi.cpp` | Inventory only; contents unread. |
| `vaspml/src/applications/test_scalapack.cpp` | Inventory only; contents unread. |
| `vaspml/src/applications/vaspml-predict.cpp` | Inventory only; contents unread. |
| `vaspml/src/applications/vaspml-predict_nvidia.cpp` | Selected setup and policy bodies. |
| `vaspml/src/benchmarks/linalg.cpp` | Inventory only; contents unread. |
| `vaspml/src/benchmarks/makefile` | Inventory only; contents unread. |
| `vaspml/src/libvaspml/ArrayResizing.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/ArrayResizing.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/BasisFunctions.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/BasisFunctions.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/BasisFunctionsAngular.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/BasisFunctionsAngular.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/BasisFunctionsRadialSpline.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/BasisFunctionsRadialSpline.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Descriptor.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Descriptor.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/DescriptorCollector.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/DescriptorCollector.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/DescriptorSHS2.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/DescriptorSHS2.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/DescriptorSHS3.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/DescriptorSHS3.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/DescriptorSHS3ReducedLinElem.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/DescriptorSHS3ReducedLinElem.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Frame.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/Frame.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/InterfaceLAMMPS.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/InterfaceLAMMPS.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/InterfaceVASP.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/InterfaceVASP.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/IoHandlerML_FF.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/IoHandlerML_FF.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Kernel.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Kernel.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/KernelPolynomial.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/KernelPolynomial.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Lattice.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/Lattice.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Linalg.hpp` | Selected bodies. |
| `vaspml/src/libvaspml/Matrix.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/MlMPI.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/MlMPI.hpp` | Selected bodies. |
| `vaspml/src/libvaspml/ParallelEnvironemt.hpp` | Policy definitions read. |
| `vaspml/src/libvaspml/Predictor.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/Predictor.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Record.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Record.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/ScaLapack.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/ScaLapack.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/SemanticVersion.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/SemanticVersion.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/ShmemArray.hpp` | Selected bodies. |
| `vaspml/src/libvaspml/SmartEnum.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/SphericalHarmonics.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/SphericalHarmonics.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/SpillingFactor.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/SpillingFactor.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Structure.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Structure.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/TagTranslator.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/TagTranslator.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/ThermodynamicIntegration.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/ThermodynamicIntegration.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Timer.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Timer.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Tutor.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/Tutor.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/TypeMap.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/TypeMap.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/constants.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/cubic_spline.hpp` | Selected bodies. |
| `vaspml/src/libvaspml/cutoff.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/cutoff.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/debug.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/io.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/io.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/makefile` | Inventory only; contents unread. |
| `vaspml/src/libvaspml/math.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/math.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/nearest_neighbor.cpp` | Selected bodies. |
| `vaspml/src/libvaspml/nearest_neighbor.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/scalapackInterface.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/types.hpp` | Map only; body unread. |
| `vaspml/src/libvaspml/utils.cpp` | Map only; body unread. |
| `vaspml/src/libvaspml/utils.hpp` | Map only; body unread. |
| `vaspml/test/build/.gitignore` | Empty file in inventory. |
| `vaspml/test/cov-html/.gitignore` | Empty file in inventory. |
| `vaspml/test/cov-xml/.gitignore` | Empty file in inventory. |
| `vaspml/test/include/.gitignore` | Empty file in inventory. |
| `vaspml/test/lib/.gitignore` | Empty file in inventory. |
| `vaspml/test/makefile` | Inventory only; contents unread. |
| `vaspml/test/src/common/Fixture.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/Fixture.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/FixtureNeighborList.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/FixtureNeighborList.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/FixtureStructure.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/FixtureStructure.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/SampleNeighborList.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/SampleNeighborList.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/SampleStructure.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/SampleStructure.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/TestCase.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/TestCase.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/TestCaseContainer.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/TestCaseFunction1D.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/TestCaseFunction1D.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/TestCaseSphericalHarmonics.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/boost_helpers.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/common/makefile` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/TestCase_BasisFunctionsRadialSpline.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/TestCase_DescriptorSHS2.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/TestCase_DescriptorSHS3.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/TestCase_DescriptorSHS3ReducedLinElem.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/TestCase_Linalg.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/TestCase_NeighborList.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/TestCase_cutoff.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/TestCase_math.hpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/makefile` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_BasisFunctionsRadialSpline.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_DescriptorSHS2.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_DescriptorSHS3.cpp` | Selected test bodies. |
| `vaspml/test/src/libvaspml/test_DescriptorSHS3ReducedLinElem.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_Lattice.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_Linalg.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_MultiType.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_NeighborList.cpp` | Selected test bodies. |
| `vaspml/test/src/libvaspml/test_SemanticVersion.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_SmartEnum.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_SphericalHarmonics.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_Tutor.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_TypeMap.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_cutoff.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_io_ML_FF.cpp` | Selected assertion map; fixture contents not audited. |
| `vaspml/test/src/libvaspml/test_math.cpp` | Inventory only; contents unread. |
| `vaspml/test/src/libvaspml/test_utils.cpp` | Inventory only; contents unread. |
| `vaspml/test/tools/create-test-data-clebschGordan.py` | Inventory only; contents unread. |
| `vaspml/test/tools/create-test-data-functions.py` | Inventory only; contents unread. |
| `vaspml/test/tools/create-test-data-sphericalHarmonics.py` | Generator body sampled; not executed. |
| `vaspml.F` | Interface declarations and force/energy/stress conversion bodies. |
