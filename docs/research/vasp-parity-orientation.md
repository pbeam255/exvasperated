# Initial VASP parity reconnaissance

2026-09-24. This is an orientation from a limited inspection, not an exhaustive
capability inventory, scientific validation, architecture or implementation plan.

## Reference and inspection scope

The local source identifies itself as VASP 6.5.1. Its source directory has 328
top-level files; its test collection has 428 top-level directories and one file.
These are filesystem counts, not counts of independent methods or covered claims.
The local executable directory is empty. No build or calculation was run.
Two local PAW dataset trees are present; their contents were not examined here.

The inspection covered the distribution and test-suite introductions, source and
test directory names, the version declaration, selected main-program dispatch
sites and electronic-failure handling, and the declarations at the beginning of
the electronic minimizer. The subsequent
[partitioning pass](vasp-source-partition.md) inventories the complete recursive
tree and adds selected source inspection and a coarse import scan. A filename
or branch establishes a lead for further
study; it does not establish scientific applicability or a working configuration.

Paths below are relative to `quarantine/vasp.6.5.1/`. Hashes identify inspected
files, not the integrity or provenance of the entire distribution.

| File | SHA-256 |
| --- | --- |
| `src/version.F` | `0ebb7e6c7c8ae422be69a765edbc2dbb6eac6c42bcbe4705384167ccc0abdec1` |
| `src/main.F` | `b764bee5a01c34e3b14933e7018033af9538cfe223e44adc3f798e7fecdb167f` |
| `src/electron.F` | `5fddfdf06a7d719c66129363007dc5fc35f525afaf62f268987fc48f6f374423` |
| `testsuite/README.md` | `b9489873c829208320359720e3ae32cabcf1c390f09917c3867cf509c4426cb7` |

The public [manual](https://vasp.at/wiki/index.php/The_VASP_Manual) and
[changelog](https://vasp.at/wiki/Changelog) were consulted on this date. The
changelog already describes 6.6.0 and 6.6.1. Thus the available source cannot by
itself define parity with current public capabilities. Keep behavior attributed
to a version; do not silently apply newer documentation to the older source.

## Breadth to investigate

The public manual supplies the following initial grouping. Local file and test
names support investigating these areas, but their full implementations have not
been read. This grouping is deliberately a research map, not a declaration that
each row is one feature or that the list is complete.

| Area | Methods and observables to distinguish |
| --- | --- |
| Electronic states | Ground-state energies, bands, densities, occupations |
| Functionals | Semilocal, Hubbard corrections, exact exchange, dispersion |
| Magnetism | Collinear and noncollinear spin, spin-orbit effects, constraints |
| Geometry | Forces, stress, relaxation, transition paths |
| Dynamics | Ensembles, constraints, enhanced sampling, transport |
| Learned interactions | Training, inference, uncertainty estimates, continuation |
| Vibrations | Phonons, electron-phonon coupling, resulting transport |
| Response | Dielectric, optical, magnetic and core spectroscopy |
| Correlation | GW, BSE, RPA, constrained RPA, MP2 |
| Localized representations | Projections, Wannier functions, external interfaces |
| Computing | Parallel execution, accelerators, memory and restart behavior |

Source: [VASP manual topic index](https://vasp.at/wiki/index.php/The_VASP_Manual).
Dataset meaning, basis construction, boundary conditions, symmetries and numerical
conventions also cross these areas; they need explicit treatment in the design.

Coverage must include scientifically meaningful combinations. For example, an
isolated force calculation does not establish forces with every supported
functional, spin treatment, boundary condition or execution backend. Conversely,
enumerating every syntactically possible input combination would not establish
useful scientific coverage. The intended domain and meaningful combinations need
to be understood and justified.

## Compatibility is a scientific and operational contract

The public [file index](https://vasp.at/wiki/Files) documents inputs such as
`INCAR`, `POSCAR`, `KPOINTS` and `POTCAR`, and outputs including `OUTCAR`,
`vasprun.xml` and HDF5 files. Their publicly documented names may be used under
the user's research rule. Their existence alone does not specify a parser or a
compatibility promise.

For an eventual compatibility profile, describe input meaning and defaults,
quantities and conventions, output structure expected by consuming tools,
continuation across jobs, invocation and resource behavior, and failure behavior.
Use independently authored examples and actual downstream consumers to exercise
the resulting contracts. Binary restart interchange, numerical equivalence and
textual compatibility are distinct claims needing their own examination.

Dataset file compatibility and access to suitable openly distributable datasets
are separate scientific and adoption questions. No dataset import, conversion,
redistribution or dataset choice was established by this survey.

## A concrete behavior requiring attention

In the inspected electronic-optimization control flow, electronic nonconvergence
causes a diagnostic, while disabling further ionic evolution depends on the
configured stop behavior or an explicit hard-stop request. This is visible in
`src/main.F` around lines 5875-5896. The main program's electronic-optimization
call and force/stress call appear around lines 3472 and 3679 respectively.

This is a source-level observation, not a reproduced run. It means we must study
what a consumer can infer from completion, diagnostics and saved quantities.
Neither producing a force table nor finishing a process independently establishes
electronic convergence. Our failure contract and compatibility behavior require
an explicit design decision and a runnable case. No proprietary diagnostic text
is reproduced here.

Version-specific reference defects matter too. For example, the public 6.6.1
notes describe a correction to spin-polarized meta-GGA forces introduced in
6.6.0. This is a documented reference limitation, not an independently confirmed
finding about the local 6.5.1 tree. See the
[changelog](https://vasp.at/wiki/Changelog#6.6.1).

## What would substantiate parity

For each scientific workload, derive the equations, assumptions, observable,
units and conventions, approximation choices and expected limits. Establish
numerical acceptance from the scientific question. Reference agreement, independent
derivations, analytic controls, convergence studies and comparison to measurements
provide different information. A VASP discrepancy needs investigation; agreement
alone cannot establish physical accuracy.

Develop the workload collection across the entire capability map, with explicit
cases for interactions, difficult convergence, malformed inputs, unsupported
combinations and continuation. The bundled test collection is useful research
material in quarantine. Its fixtures, comparison code and thresholds are not our
test suite, and its size does not demonstrate coverage of the full program.

The next research synthesis must connect capabilities and workflows to primary
scientific literature, source behavior and observables before it can justify the
system design. Architectural ownership, library choices, performance targets and
the implementation sequence remain open. Beads tracks that work; this document
records the present observations and their limits.

## License selection

The user delegated selection of a permissive project license that supports
adoption. Apache-2.0 was selected: it permits broad use and redistribution and
includes an express contributor patent grant subject to its terms. MIT is also
permissive and shorter. These are conclusions from the
[Apache-2.0 text](https://www.apache.org/licenses/LICENSE-2.0.html) and
[MIT text](https://opensource.org/license/mit), not a claim that licensing settles
scientific suitability or that a dependency is automatically compatible.

The project license covers our original contributions. Quarantined material is
outside the release and retains its own terms. External code and data choices
will be evaluated individually, as requested by the user.
