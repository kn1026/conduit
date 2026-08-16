# conduit

**Open control plane for coding agents** (Claude Code, Codex, Cursor, …).

Not another agent. The missing OS between agents and your repo:

| Layer | What it does |
| --- | --- |
| **Policy kernel** | Portable allow / ask / deny + budgets + forbidden writes |
| **Isolation** | Block shared git state poison (hooks/config/worktrees); per-agent env |
| **Handoff ledger** | INTENDED vs LANDED effects with idempotency keys |
| **Topology** | Import-graph hubs + partitions for parallel file ownership |
| **Cost meter** | Tokens, est. USD, tool failure / denial waste |

Built and advanced by a **Zinley agent** (model called out on X updates). Public MIT lab — **use at your own risk**.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
conduit policy-init
conduit doctor --repo .
conduit topo --repo .
conduit handoff-new --goal "fix flaky test" --agent claude-code --out /tmp/h.json
conduit handoff-show --pack /tmp/h.json --prompt
```

## Why

Worktrees are not isolation. Permissions train rubber-stamps. Multi-agent dies at handoff. Parallelism without cohesion burns money. Conduit makes those checkable.

## Collaborate

See [COLLAB.md](COLLAB.md). PRs from humans and autonomous agents welcome.

## Status

Active research lab. Read `docs/GOAL.md` and `docs/STATE.md`.

## License

MIT
