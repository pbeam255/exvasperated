# Machine-learned force fields: C++ first-pass review

Reviewed 2026-09-24 against quarantined VASP 6.5.1 and the
[first-pass report](../ml-cpp.md). This is the requested single independent
review at depth one. No child review, build, prediction, generator, test or
scientific experiment was run.

## Correction required

**Qualify the inverse-helper observation by compiler branch.** The report says
that the CBLAS-conditioned helper proceeds through factorization and inversion
without handling positive status values. This is accurate for its non-NEC
branch, but `Linalg.hpp` 614–615 throws in the NEC branch. State explicitly
that the unchecked factorization/inversion path is the non-NEC CBLAS branch.
The empty cuBLAS-conditioned alternative at 648–651 and the report's caution
about reachability are supported. This is a narrow qualification, not evidence
that the sampled prediction path fails.

## Material claims checked

Unless otherwise indicated, short C++ paths below are relative to
`src/vaspml/src/libvaspml/`.

- **Entry points and execution policy.** `InterfaceVASP.cpp` 20–32,
  97–148 supports opaque object lifetime operations, communicator import,
  model reading and unit conversion, CPU frame initialization, and the order
  of descriptor, kernel, prediction and stress updates.
  `src/vaspml/src/applications/vaspml-predict_nvidia.cpp` 114–130 explicitly
  selects the GPU policy for the frame and kernel. `ParallelEnvironemt.hpp`
  10–46 supports conditional removal of the parallel-policy bodies. These
  reads do not establish a working build or host-adapter GPU execution.
- **External neighbors.** `InterfaceLAMMPS.cpp` 211–246 rejects an unknown
  nonempty type name. Lines 397–478 support sorting and masking the supplied
  neighbor indices, the cutoff check, unit conversion and displacement
  normalization. That distance branch has no positive-distance guard.
  The report appropriately leaves host guarantees and ghost ownership open.
- **Internal geometry and radial functions.** `nearest_neighbor.cpp`
  144–235 supports image bounds, image/atom enumeration and exclusion of
  small squared distances. `Lattice.cpp` 119–151 supports a signed
  determinant in the inverse and an absolute determinant for volume.
  `BasisFunctionsRadialSpline.cpp` 290–340, 396–451 supports the sampled
  radial projection and spline construction. `cubic_spline.hpp` 164–214
  supports endpoint-condition selection and the required grid divisions.
  `cutoff.cpp` 114–196 supports the hard-cutoff derivative convention,
  analytic taper branches and debug-conditioned input checks. No general
  differentiability or cell-domain guarantee follows from these bodies.
- **Descriptors and normalization.** `Frame.cpp` 216–279 supports the
  standard/reduced dispatch. `DescriptorSHS3.cpp` 89–124 supports the
  magnetic-component contraction, species mapping and feature weights.
  `DescriptorSHS3ReducedLinElem.cpp` 101–130 supports the sampled sum
  over element blocks, without establishing loss of all species information.
  `DescriptorCollector.cpp` 136–183 forms the weighted Euclidean norm and
  uses the square root of a component's weight divided by that norm as its
  scale. The small-norm branch skips both packing and length advancement.
  `KernelPolynomial.cpp` 143–177 independently guards the inverse-norm
  derivative factor. The report correctly leaves their joint validity open.
- **Energy, forces and stress.** `Predictor.cpp` 647–754 supports mapped
  coefficient contractions and the two stated energy-offset conventions.
  Lines 677–699, 900–969 support force preparation before stress and the
  negative inverse-volume pair contribution with symmetric tensor copying.
  `src/vaspml.F` 433–455, 507–536 supports separate force, energy and
  stress conversion/reduction paths. Full conservative derivatives and
  cross-interface unit agreement remain unproved.
- **Coverage measure and statistics.** `SpillingFactor.cpp` 68–126
  supports inverse-kernel use, the quadratic contraction and absolute-value
  residual capped at unity. Lines 129–154 support the reported use of type
  averages for the overall extrema and unweighted mean. The report correctly
  avoids interpreting this measure as calibrated force uncertainty or claiming
  that a particular consumer displays these summaries.
- **Storage and model parsing.** `ShmemArray.hpp` 182–220,
  `MlMPI.hpp` 1051–1077 and `MlMPI.cpp` 174–202 support the allocation
  alternatives, shared-window query and ownership-flag handling. Collective
  lifetime and copy/move correctness remain open. `IoHandlerML_FF.cpp`
  45–76, 674–691 supports version checking and the impossible delimiter
  condition. The newer-version path calls the error policy, which throws
  at `Tutor.cpp` 15–20. Lines 782–795 support the cited unit rescaling.
  The report does not overstate malformed-file rejection completeness.
- **Builds and test evidence.** `src/vaspml/makefile` 1–55 supports the
  three build target groups. The directory and application source referenced
  by `src/vaspml/CMakeLists.txt` 50–64, 110–112 are absent from this tree;
  the machine-specific include locations are present. The NVIDIA compiler
  template does not itself enable the parallel-policy macros. Sampled
  descriptor and neighbor tests support the stated comparison shapes, and
  the model I/O assertions at `test_io_ML_FF.cpp` 360–363 support selected
  round-trip checks. The angular-data generator at
  `src/vaspml/test/tools/create-test-data-sphericalHarmonics.py` 42–75
  uses a special-function implementation and automatic differentiation with
  the reported coordinate-domain divisions. These observations establish
  neither fixture independence nor passing tests.

## Scope and limits

The inventory contains 162 files totaling 64,795 lines in this partition.
The report's register contains exactly those 162 paths, without missing,
duplicate or additional entries. Its distinctions between selected bodies,
maps and unread contents preserve the bounded nature of this pass.

This review sampled the report's substantive control-flow, numerical and
scientific claims; it did not deeply analyze every file, inspect the fixture
values or independently derive every descriptor and derivative. The report's
questions about species subsets, empty environments, parser robustness,
collective ownership and backend equivalence remain future work. Actual CPU,
NVIDIA and AMD execution remains unestablished. No proprietary source,
comments, diagnostic strings or datasets were copied into this artifact.
