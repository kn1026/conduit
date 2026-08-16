# session-20260816-0745-bootstrap

## Goal snapshot
Bootstrap conduit control plane lab; public git; schedules.

## Did
- Scaffold package: policy, isolation, handoff, topology, cost, kernel, CLI
- Tests + docs GOAL/STATE/LOG/WORKFLOW
- (push + schedules + launch X in same bootstrap turn)

## Results
- pytest expected green on core units
- v0 API usable via `conduit` CLI

## Open
- Real Claude Code / Codex hook adapters
- Stronger graph partitioner
- Policy-graded sandbox runner
- GitHub Action for doctor on PRs

## Recommended next
Implement `scripts/claude_hooks_sample.json` + interceptor that maps tool events into kernel.check / begin_effect / land_effect; add integration test with temp repo + fake hook write attempt.

## Blockers
None.
