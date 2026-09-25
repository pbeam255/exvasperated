#!/usr/bin/env python3
"""Bounded storage protocol exploration; no numerical or filesystem simulation.

Run with Python 3.10+: python3 models/calculation_history.py
The assumptions and scope are in docs/design/calculation-history.md.
"""

from collections import deque
from dataclasses import dataclass, replace
from itertools import combinations
import json


# Two preexisting entries, then a fork from the root and a successor to that fork.
# A persisted block stands for complete immutable bytes and a durable name.
PARENTS = {0: None, 1: 0, 2: 0, 3: 2}
CONTENTS = {0: frozenset({0}), 1: frozenset({0, 1}),
            2: frozenset({0, 2, 3}), 3: frozenset({0, 2, 4})}
NEW_BLOCKS = {2: frozenset({2, 3}), 3: frozenset({4})}
BASE = frozenset({0, 1})
# Phases: absent, writing, prepared, visible, durable, acknowledged.
ABSENT, WRITING, PREPARED, VISIBLE, DURABLE, ACKNOWLEDGED = range(6)


@dataclass(frozen=True)
class State:
    phases: tuple[int, int] = (ABSENT, ABSENT)
    written: frozenset[int] = BASE
    persisted: frozenset[int] = BASE
    hint: int = 0
    stopped: bool = False


def phase(state, entry):
    return ACKNOWLEDGED if entry in BASE else state.phases[entry - 2]


def at_phase(state, entry, value):
    values = list(state.phases)
    values[entry - 2] = value
    return replace(state, phases=tuple(values))


def transitions(state):
    if state.stopped:
        return
    for entry in (2, 3):
        p = phase(state, entry)
        if p == ABSENT and phase(state, PARENTS[entry]) == ACKNOWLEDGED:
            yield f"begin {entry}", at_phase(state, entry, WRITING)
        if p == WRITING:
            for block in sorted(NEW_BLOCKS[entry]):
                if block not in state.written:
                    yield f"write block {block}", replace(
                        state, written=state.written | {block})
                elif block not in state.persisted:
                    yield f"persist block {block}", replace(
                        state, persisted=state.persisted | {block})
            if CONTENTS[entry] <= state.persisted:
                yield f"prepare manifest {entry}", at_phase(state, entry, PREPARED)
        if p == PREPARED:
            visible = at_phase(state, entry, VISIBLE)
            yield f"publish name {entry}", visible
            # A rename may have taken effect despite returning an error.
            yield f"publish {entry}, ambiguous error", replace(visible, stopped=True)
        if p == VISIBLE:
            yield f"persist directory {entry}", at_phase(state, entry, DURABLE)
        if p == DURABLE:
            yield f"acknowledge {entry}", at_phase(state, entry, ACKNOWLEDGED)
    latest = max(e for e in PARENTS if e != 1 and phase(state, e) == ACKNOWLEDGED)
    if state.hint != latest:
        yield f"hint {latest}", replace(state, hint=latest)
    # Stops at every boundary abstract rank loss or a reported IO failure.
    yield "stop after failure", replace(state, stopped=True)


def subsets(values):
    values = sorted(values)
    for size in range(len(values) + 1):
        for selected in combinations(values, size):
            yield frozenset(selected)


def recover(entries, blocks):
    """Find final entries whose recorded contents are available.

    The actual reader must also check encodings, dimensions and checksums.
    No hint participates in this selection and no temporary entry is promoted.
    Ancestry gaps are reported separately from missing recorded values.
    """
    return frozenset(e for e in entries if CONTENTS[e] <= blocks)


def ancestry_gaps(entries):
    return frozenset(e for e in entries
                     if PARENTS[e] is not None and PARENTS[e] not in entries)


def check(state):
    assert state.persisted <= state.written
    assert BASE <= state.persisted
    visible = BASE | {e for e in (2, 3) if phase(state, e) >= VISIBLE}
    durable = BASE | {e for e in (2, 3) if phase(state, e) >= DURABLE}
    acknowledged = BASE | {e for e in (2, 3) if phase(state, e) == ACKNOWLEDGED}
    for entry in visible:
        assert CONTENTS[entry] <= state.persisted
        assert PARENTS[entry] is None or PARENTS[entry] in durable
    assert acknowledged <= durable

    crash_cases = 0
    # Any not-yet-persisted final name may survive or disappear on a crash.
    for survivors in subsets(visible - durable):
        after_crash = durable | survivors
        restored = recover(after_crash, state.persisted)
        assert restored == after_crash
        assert acknowledged <= restored
        assert BASE <= restored  # Original future survives creation of the fork.
        assert not ancestry_gaps(restored)
        # Discovery must also work with an absent, stale or invalid hint.
        # Recovery deliberately takes no hint parameter.
        crash_cases += 1
    return crash_cases


def explore():
    initial = State()
    queue = deque([initial])
    paths = {initial: []}
    edges = crashes = 0
    witnesses = {}
    while queue:
        state = queue.popleft()
        try:
            crashes += check(state)
        except AssertionError as error:
            raise AssertionError({"trace": paths[state], "state": repr(state)}) from error
        if phase(state, 2) == VISIBLE:
            witnesses.setdefault("visible_but_unacknowledged", paths[state])
        if phase(state, 3) == ACKNOWLEDGED and state.hint == 0:
            witnesses.setdefault("two_entries_saved_with_stale_hint", paths[state])
        if state.stopped and phase(state, 2) == VISIBLE:
            witnesses.setdefault("uncertain_publication", paths[state])
        for action, successor in transitions(state):
            edges += 1
            if successor not in paths:
                paths[successor] = paths[state] + [action]
                queue.append(successor)
    assert len(witnesses) == 3, "Required crash/branch scenarios were unreachable"
    # Missing shared data rejects all affected entries; it is never filled in.
    assert recover(frozenset(PARENTS), frozenset({0, 1, 3, 4})) == BASE
    # Intact state is still readable if an unrelated ancestry manifest is lost.
    # Its missing parent is reported, never invented or silently ignored.
    partial = recover(frozenset({0, 1, 3}), frozenset(range(5)))
    assert partial == frozenset({0, 1, 3})
    assert ancestry_gaps(partial) == frozenset({3})
    return {"states": len(paths), "transitions": edges,
            "crash_recovery_cases": crashes, "witnesses": witnesses,
            "scope": "Two new entries, two independent payloads for the fork, one crash; "
                     "immutable blocks, durable-prefix assumptions, no physical IO or science."}


if __name__ == "__main__":
    print(json.dumps(explore(), indent=2))
