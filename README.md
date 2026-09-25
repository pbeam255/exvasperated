# Exvasperated

Research toward an independently implemented, open-source replacement for VASP,
with broad scientific capability and compatibility interfaces that minimize
disruption to existing research workflows.

The project is in research and design. There is no electronic-structure engine
or usable compatibility implementation yet. Full capability parity is the goal;
the available VASP 6.5.1 source is the initial inspection reference.

The **v1-alpha end state must run on CPU and NVIDIA GPUs**. **AMD GPU execution
is a second-wave objective.** Backend candidates, including cuda-oxide, will be
evaluated on their capabilities and evidence from relevant workloads.

The project sequence is deep VASP studies and detailed reports, synthesis of
parity and improvement opportunities, an extensive research and reference
campaign, system design, specification and planning, then implementation,
validation and release.

- [Project direction and working preferences](INERTIA.md)
- [Source partition and proposed study order](docs/research/vasp-source-partition.md)
- [First-pass source studies and independent reviews](docs/research/first-pass/README.md)
- [Core program and scientific routine outline for the reference expedition](docs/research/core-program-outline.md)
- [Broad literature and reference acquisition campaign](docs/research/reference-campaign/README.md)
- [Initial parity reconnaissance](docs/research/vasp-parity-orientation.md)

VASP source may be read and executed for research. Our implementation and
documentation must be independently written. Publicly documented interface tokens
may be used for compatibility; proprietary implementation text may not be copied
into this project. Source, datasets, reference fixtures and private run artifacts
remain in the ignored `quarantine/` directory. Local papers live in `papers/`.

Original project contributions are licensed under [Apache-2.0](LICENSE). This
license does not apply to quarantined material or other third-party works.

Work is tracked with beads (`bd ready --json`).
