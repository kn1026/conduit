# WORKFLOW — conduit lab

## Runtime
- **Only** Zinley's Computer (`device_id=zinley-computer`).
- Project: `/home/daytona/workspace/conduit`
- Public: `https://github.com/kn1026/conduit`
- Shell cwd resets to `/home/daytona/workspace` every Bash — always `cd` to project or use absolute paths.
- Never `git init` at workspace root. Never commit `.env`.

## Schedule (owner 2026-08-16)
- **R&D:** 7 deep slots/day America/Los_Angeles: 07:00, 09:30, 12:00, 14:30, 17:00, 19:30, 22:00
- **X progress:** 1–2 posts morning PT only (08:15 and optional 10:30) when there is real unposted delta
- Notify Khoi via **text_message only** (never email lab status)

## BEFORE work
Read WORKFLOW, GOAL, STATE, LOG, latest `docs/SESSIONS/session-*.md` → pick single highest-leverage next move from evidence. No hardcoded micro-task list.

## DURING
- Deep multi-layer ships: code + tests + docs + commit + push on real delta
- pytest green
- Autonomous; no mid-run owner questions for routine choices
- Research for real when stuck; try multiple approaches
- Ban: rename-only, docs-only thrash, toy dashboards, empty "still working"

## X rules (morning PT)
- Only real delta (new capability, adapter, benchmark number, honest negative that changes attack)
- Invite people/agents to try + open PRs
- Must say run is **Zinley agent** + model **Grok 4.5** (or actual model if different)
- Link repo
- Max 1–2/day morning PT; skip if nothing ship-worthy
- Via x-growth `x_client` as @khoi_danny
- No personal-AI spam templates

## BEFORE DONE (always)
1. Append `docs/LOG.md`
2. New `docs/SESSIONS/session-YYYYMMDD-HHmm-<slug>.md`
3. Update `docs/STATE.md`
4. Commit + push material changes
5. `text_message` Khoi one-liner
6. Morning X only if rules above match

## Full solve
When GOAL win condition met: `docs/PAPER.md` + STATE solved + climactic X + text.
