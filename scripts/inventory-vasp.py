#!/usr/bin/env python3
"""Inventory the quarantined reference without exporting source text.

Partition membership is an initial research judgment, not an architecture.
The CSV records file identities and sizes only. Missing or multiply assigned
top-level files fail rather than silently falling into an unexamined category.
"""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO / "quarantine/vasp.6.5.1/src"
DEFAULT_OUTPUT = REPO / "docs/research/vasp-source-inventory.csv"
DEFAULT_LINKS = REPO / "docs/research/vasp-partition-links.csv"

# Explicit assignments for the flat Fortran source tree. File names identify
# reference locations; no implementation text is retained here.
GROUPS = {
    "execution": (
        "Build selection, orchestration and diagnostics",
        """.objects main.F main_mpi.F command_line.F version.F build_info.F
        build_info.inc makefile makedeps.awk makeparam.F param.inc symbol.inc
        tutor.F vasp.cfg profiling.F""",
    ),
    "foundations": (
        "Shared state, units and small utilities",
        """base.F constant.F string.F smart_allocate.F""",
    ),
    "io": (
        "Inputs, outputs and continuation",
        """incar_reader.F incar_reader.inc reader.F reader_base.F reader_base.inc
        poscar.F poscar_struct.F fileio.F writer.F xml.F xml_writer.F
        vhdf5.F vhdf5_base.F""",
    ),
    "geometry": (
        "Geometry, symmetry and reciprocal sampling",
        """lattice.F lattice.inc lattlib.F mkpoints.F mkpoints_change.F
        mkpoints_full.F mkpoints_struct.F rot.F spinsym.F stufak.F supercell.F
        sym_grad.F symlib.F symmetry.F""",
    ),
    "representation": (
        "Grids, transforms and wave representations",
        """fft_base.F fft_comm.F fft_wrappers.F ffttest.F fftw.F gridq.F
        mgrid.F mgrid_struct.F opergrid.F wave.F wave_cacher.F wave_high.F
        wave_interpolate.F wave_mpi.F wave_rotator.F wave_struct.F wave_window.F
        wavpre.F wavpre_noio.F dfast.F""",
    ),
    "paw": (
        "Atomic data, PAW and projectors",
        """aedens.F asa.F core_rel.F fast_aug.F nl_struct.F nonl.F nonl_high.F
        nonlr.F optreal.F paw.F paw_base.F pawsym.F pseudo.F pseudo_struct.F
        radial.F radial_struct.F relativistic.F rhfatm.F setlocalpp.F us.F""",
    ),
    "electrostatics": (
        "Charge, potentials and Hamiltonian assembly",
        """bext.F charge.F coulomb_cutoff.F coulomb_cutoff_gradients.F dipol.F
        ebs.F extpot.F hamil.F hamil_rot.F hamil_struct.F pot.F pot_electrostat.F
        pot_struct.F scpc.F solvation.F tau_mu.F""",
    ),
    "xc": (
        "Semilocal functionals and on-site corrections",
        """LDApU.F constrmag.F fexcg.F ggalib.F ldalib.F mbj.F mggalib.F
        setex.F setex_struct.F xc_driver.F""",
    ),
    "nonlocal_interactions": (
        "Exact exchange and dispersion",
        """fock.F fock_ace.F fock_dbl.F fock_frc.F fock_glb.F fock_multipole.F
        libmbd.F parsD3.inc pawfock.F pawlhf.F pwlhf.F subdftd3.F subdftd4.F
        vdw_nl.F vdwforcefield.F vdwforcefield_glb.F wpbe.F""",
    ),
    "electronic_solution": (
        "Electronic optimization, occupations and state observables",
        """bandgap_struct.F bandgap_tools.F broyden.F broyden.inc david_full.F
        david_inner.F davidson.F diis.F dos.F electron.F electron_OEP.F
        electron_all.F electron_common.F electron_lhf.F elf.F fermi_energy.F
        ini.F mix.F pardens.F rmm-diis.F steep.F stm.F subrot.F subrot_cluster.F
        subrot_scf.F tet.F""",
    ),
    "ions": (
        "Forces, ionic optimization, dynamics and sampling",
        """chain.F constr_cell_relax.F dimer_heyden.F dvvtrajectory.F dyna.F
        dynbr.F dynconstr.F force.F gadget.inc hills.inc internals.F
        npt_dynamics.F paircorrection.F random.F stepver.F""",
    ),
    "response": (
        "Response equations, fields and spectroscopy",
        """cl_shift.F core_con_mat.F dmatrix.F egrad.F elinear_response.F
        elpol.F hamil_lr.F hamil_lrf.F hyperfine.F ilinear_response.F
        linear_optics.F linear_response.F linear_response_NMR.F lr_helper.F
        nmr.F optics.F pead.F rmm-diis_lr.F rmm-diis_mlr.F subrot_lr.F""",
    ),
    "many_body": (
        "Screening, correlation and excited states",
        """GG_base.F acfdt.F acfdt_GG.F auger.F bse.F bse.inc bse_driver.F
        bse_lanczos.F bse_struct.F bse_te.F chi.F chi_GG.F chi_base.F chi_glb.F
        chi_super.F crpa.F esf.F esf_struct.F greens_orbital.F greens_real_space.F
        gw_model.F local_field.F lt_mp2.F minimax.F minimax_dependence.F
        minimax_functions1D.F minimax_functions2D.F minimax_ini.F minimax_struct.F
        minimax_varpro.F mp2.F pade_fit.F rnd_orb_mp2.F rpa_force.F rpa_high.F
        rpax.F screened_2e.F time_propagation.F ump2.F ump2kpar.F ump2no.F wpot.F""",
    ),
    "vibrations": (
        "Phonons, electron-phonon interactions and transport",
        """elphon.F elphon_accumulators.F elphon_base.F elphon_common.F
        elphon_derivative.F elphon_driver.F elphon_kgrid.F elphon_mels.F
        elphon_potential.F elphon_potential_struct.F elphon_selfen_ph.F
        elphon_triplets.F finite_diff.F phonon.F sydmat.F transport.F""",
    ),
    "localized": (
        "Localized orbitals, embedding and scientific interchange",
        """afqmc.F afqmc_struct.F dmft.F embed.F fcidump.F k-proj.F lcao_bare.F
        lie.F locproj.F locproj_struct.F mlwf.F sphpro.F stockholder.F
        twoelectron4o.F umco.F wannier.F wannier_interpol.F wannier_mats.F wap.F""",
    ),
    "ml_fortran": (
        "Fortran learned-force-field system",
        """ml_asa2.F ml_ff_abinitio.F ml_ff_c2f_interface.F ml_ff_constant.F
        ml_ff_ff.F ml_ff_ff2.F ml_ff_ff3.F ml_ff_helper.F ml_ff_iohandle.F
        ml_ff_logfile.F ml_ff_math.F ml_ff_memory.F ml_ff_mlff.F ml_ff_mpi.F
        ml_ff_mpi_help.F ml_ff_mpi_shmem.F ml_ff_neighbor.F ml_ff_prec.F
        ml_ff_string.F ml_ff_struct.F ml_ff_taglist.F ml_ff_tutor.F
        ml_interface.F ml_interface_writer.F ml_reader.F ml_reader.inc""",
    ),
    "ml_cpp": (
        "C++ learned-force-field library, applications and tests",
        "vaspml.F",
    ),
    "plugins": (
        "Python plugin and language boundaries",
        "plugins.F c2f_interface.F",
    ),
    "parallel": (
        "Parallel ownership, accelerators and runtime support",
        """crayhip.F intelmkl.F mpi.F mpi_shmem.F nvcuda.F offload.F
        offload_struct.F openacc.F openacc_struct.F openmp.F openmp_struct.F
        pm.inc shm.F simd.F simd.inc""",
    ),
    "numerics": (
        "Numerical libraries, algebra and quadrature",
        """Lebedev-Laikov.F blas_wrappers.F brent.F choleski2.F dgemmtest.F
        gauss_quad.F jacobi.F lapack_wrappers.F m_unirnk.F mathtools.F mymath.F
        ratpol.F root_find.F scala.F scala_struct.F scalapack_wrappers.F zgemmtest.F""",
    ),
}

# Subtrees stay together initially, including their tests, docs, build files,
# generated sources and empty placeholders. Deep study may refine a partition.
SUBTREES = {
    "HIP": "parallel",
    "oneapi": "parallel",
    "fftlib": "representation",
    "lib": "numerics",
    "parser": "localized",
    "plugins": "plugins",
    "vaspml": "ml_cpp",
}

OVERRIDES = {
    "lib/diolib.F": "io",
    "lib/dlexlib.F": "io",
    "lib/drdatab.F": "io",
    "lib/preclib.F": "foundations",
    "lib/makefile": "execution",
    **{f"lib/{name}": "parallel" for name in (
        "dclock.c", "dclock_.c", "dclock_ds20.c", "dclock_simple.c",
        "getshmem.c", "ptimers.f", "sclock_cray.F", "sclock_nec.F",
        "sclock_t3d.F", "timing.c", "timing.fujitsu.F", "timing_.c", "timing_ds20.c",
    )},
}


def collect(source):
    assignments = {}
    for group, (_, names) in GROUPS.items():
        for name in names.split():
            if name in assignments:
                raise ValueError(f"Duplicate assignment: {name}")
            assignments[name] = group
    if not source.is_dir():
        raise ValueError(f"Source directory is absent: {source}")
    rows = []
    found_top = set()
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Review symlink before inventorying: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if len(relative.parts) == 1:
            group = assignments.get(relative.name)
            found_top.add(relative.name)
        else:
            group = SUBTREES.get(relative.parts[0])
        group = OVERRIDES.get(relative.as_posix(), group)
        if group is None:
            raise ValueError(f"Unassigned file: {relative}")
        raw = path.read_bytes()
        rows.append({
            "path": relative.as_posix(),
            "partition": group,
            "bytes": len(raw),
            "lines": raw.count(b"\n") + int(bool(raw) and not raw.endswith(b"\n")),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
    missing = set(assignments) - found_top
    missing.update(set(OVERRIDES) - {row["path"] for row in rows})
    if missing:
        raise ValueError(f"Assigned files are absent: {sorted(missing)}")
    return rows


def import_links(source, rows):
    """Approximate Fortran imports, without retaining module names or source.

    Includes all preprocessor branches. Does not resolve calls, include expansion,
    dynamic dispatch or imports in other languages. Multiple providers contribute
    candidate edges; these counts are research navigation aids only.
    """
    providers = defaultdict(set)
    imports = {}
    for row in rows:
        path = source / row["path"]
        if path.suffix.lower() not in (".f", ".f90", ".inc"):
            continue
        content = "\n".join(
            line for line in path.read_text(errors="replace").splitlines()
            if not line.lstrip().startswith("!")
        )
        for name in re.findall(r"^\s*module\s+(?!procedure\b|function\b|subroutine\b)(\w+)", content, re.M | re.I):
            providers[name.lower()].add(row["path"])
        imports[row["path"]] = {
            name.lower() for name in re.findall(
                r"^\s*(?:[A-Z]+\s+)?use\s+(?:,\s*(?:non_intrinsic|intrinsic)\s*::\s*|::\s*)?(\w+)",
                content, re.M | re.I,
            )
        }
    edges = {
        (consumer, provider)
        for consumer, names in imports.items()
        for name in names
        for provider in providers.get(name, ())
        if consumer != provider
    }
    owners = {row["path"]: row["partition"] for row in rows}
    counts = Counter((owners[a], owners[b]) for a, b in edges if owners[a] != owners[b])
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["consumer", "provider", "candidate_file_pairs"])
    for (consumer, provider), count in sorted(counts.items()):
        writer.writerow([consumer, provider, count])
    print(f"Approximate Fortran import scan: {len(imports)} files; {len(edges)} file pairs")
    return output.getvalue()


def render(rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, ["path", "partition", "bytes", "lines", "sha256"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--links-output", type=Path, default=DEFAULT_LINKS)
    parser.add_argument("--check", action="store_true", help="Compare the inventory without writing")
    args = parser.parse_args()
    rows = collect(args.source)
    content = render(rows)
    links = import_links(args.source, rows)
    for path, data in ((args.output, content), (args.links_output, links)):
        if args.check:
            if not path.is_file() or path.read_text() != data:
                raise SystemExit(f"Inventory differs: {path}; inspect changes before regenerating")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data)
    print(f"{len(rows)} files; {sum(r['lines'] for r in rows):,} lines; {len(GROUPS)} partitions")
    for group, (title, _) in GROUPS.items():
        members = [row for row in rows if row["partition"] == group]
        print(f"{group}: {len(members)} files, {sum(r['lines'] for r in members):,} lines — {title}")


if __name__ == "__main__":
    main()
