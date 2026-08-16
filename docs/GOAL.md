# GOAL — conduit

## North star (machine-checkable)
Ship an open **control plane** that sits on top of Claude Code, Codex, Cursor, and similar agents:

1. **Policy kernel** — portable YAML: allow / ask / deny / budget / forbidden write globs; `conduit policy-check` is deterministic.
2. **Isolation runtime** — refuse writes to `.git/hooks`, `.git/config`, `.git/worktrees`; `conduit doctor` flags parallel-agent bleed; env fork gives unique `COMPOSE_PROJECT_NAME`.
3. **Handoff ledger** — packs record INTENDED vs LANDED side effects with idempotency keys; resume prompt refuses to assume unlanded work.
4. **Topology planner** — static import graph → hubs + partitions for multi-agent file ownership (`conduit topo`).
5. **Cost meter** — tokens / est USD / tool failure + denial retry ratio on each run snapshot.

## Win condition (v1 lab)
A single integration path where:
- two "agents" cannot poison parent git hooks through conduit-checked writes (tests green),
- a handoff pack with a completion gap is **not** marked trustworthy until LANDED,
- `conduit doctor` + `policy-check` + `topo` run on this repo and produce JSON,
- at least one real adapter hook doc for Claude Code **or** Codex is executable (script or documented hooks file consumed by tests),
- public README + COLLAB invite; CI-ready pytest.

## Kill / retarget
14 days with no multi-layer delta (code + tests + docs) → retarget GOAL or archive lab.

## Non-goals
- Not another coding agent / IDE clone.
- Not browser-use / RPA.
- Not personal-AI manifesto content.
