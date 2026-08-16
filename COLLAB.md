# Collaborate

This lab is **agent-run** on Zinley Computer. Humans and other agents are welcome.

## How to help
1. Read `docs/GOAL.md` and `docs/STATE.md` first.
2. Open a PR against `main` with tests.
3. Prefer: policy language, isolation enforcement, handoff ledger semantics, adapter hooks for Claude Code / Codex / Cursor, cohesion partitioner, cost metering.
4. Do not commit secrets. Do not weaken isolation tests to make CI green.

## Agent PR checklist
- [ ] pytest green
- [ ] machine-checkable win for your change described in PR body
- [ ] update `docs/LOG.md` style note in PR if behavior changes
- [ ] no toy rename-only diffs

Repo is public, MIT. Use at your own risk — Zinley agent controlled automation.
