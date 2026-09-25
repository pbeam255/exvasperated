# Agent instructions

Read the current Exvasperated section of `INERTIA.md` before working. Its imported
Forge history is background, not an implementation plan for this repository.

## Design and working style

No certification, evidentiary, authority or ADR theater in the product or working
process. Do not build certificate/evidence objects, approval rituals, authority
hierarchies or ADR machinery. Put rigor into equations, types, representations,
algorithms and discriminating tests. Keep useful reasoning, sources, measurements
and counterexamples in ordinary revisable notes. Extensive verification does not
justify administrative scaffolding.

Use **teeth tests** in place of ADR prescriptions: for a proposed "shall" or
"shall not", build a substantive check, demonstrate red for a relevant violation,
then make it green through adherence. Code tests, compiler guards and other
executable checks qualify. A failure must concern the intended behavior, not a
missing document, arbitrary assertion or broken harness. Keep the check able to
catch regression. If no meaningful red demonstration is possible, the statement
is at best a good intention; do not present it as enforced. This practice adds no
registry, certificate or approval process.

## Engineering tenets

1. Systems interact only through interfaces. Never reach into another system's
   private state, implementation or storage. Interfaces may be in-process
   functions or ownership handoffs; this does not require copies or services.
2. Use the database for work it handles better. Evaluate its constraints,
   transactions and query operations before duplicating them in application code.
3. No object-oriented programming. Use algebraic data types, explicit data
   structures and operations; do not organize our systems as object hierarchies.
4. No JVM or JVM application components. The narrow exception is a needed
   verification tool such as Apalache that we have no time to reimplement. Run
   it in an extremely lightweight container with programmatic teardown when done,
   including failure and interruption cleanup. Never rely on manual cleanup.
5. Correct operation must not depend on a human or model remembering a step.
   Encode the requirement structurally or automate it, with substantive teeth.
6. Never hot patch. Study the system, analyze the problem, plan the fix, then
   implement it through the normal testing and review cycle.
7. Trigger required work through automation. Do not substitute reminders such
   as "remember to run tests" for executable workflow triggers.
8. Always work from a plan. Revisit it when findings change the problem. Language
   like "easiest" or "quickest done" is a reason to examine whether convenience
   is displacing the intended design and correctness requirements.
9. For each implementation section/tranche: substantive tests red with real
   errors; implement; tests green; adversarial tribunal code review; address
   findings and rerun affected checks; then proceed to the next planned tranche.
   Tautological tests do not count. Reviews challenge actual code and tests;
   do not turn them into certificates or approval theater.

These instructions describe the required practice. Do not claim a requirement
is mechanically enforced until its teeth have been demonstrated.

## Research boundary

VASP source inspection and execution are authorized. Independently write our
implementation; never copy proprietary source or implementation text into project
artifacts. Publicly documented interface names and format tokens are allowed.
Keep quarantined source, datasets, test fixtures and private run artifacts out of
Git and releases. Document findings in original prose with references.

The source partition is a research navigation aid. Inventory membership and
source hashes do not establish completed analysis or scientific correctness.
Deep studies are bounded and follow the recorded study order, subject to findings
and user direction. A useful pass may leave open questions: report them, work on
related areas, and return when new context helps. Preserve follow-up without
forcing complete closure of each area before progressing. Do not import the
reference architecture by default.

## Work tracking and delivery

Use beads for work tracking: `bd ready --json`, `bd show <id> --json`,
`bd update <id> --claim --json` and `bd close <id> --reason ... --json`.
Keep research findings in documents and actionable work in beads.

The installed beads version uses Dolt and does not provide `bd sync`.
Use `bd export -o .beads/issues.jsonl` before committing to preserve issue state
with the repository. The local database and runtime files stay ignored.

For changes to the inventory or partition, run
`python3 scripts/inventory-vasp.py --check`. This checks reference identity and
partition coverage; it is not a scientific test. Run appropriate checks for other
changes and record what actually ran.

Inspect staged paths to ensure no quarantined material is included. Commit and
push completed authorized work to the configured remote, following the parent
workspace delivery instructions. Use noninteractive shell commands. Do not
remove unrelated user changes or run downloaded programs without selecting a
bounded experiment.
