# WORKFLOW — conduit lab

## Runtime
- **Only** Zinley's Computer (`device_id=zinley-computer`).
- Project: `/home/daytona/workspace/conduit`
- Public: `https://github.com/kn1026/conduit`
- Shell cwd resets to `/home/daytona/workspace` every Bash — always `cd` to project or use absolute paths.
- Never `git init` at workspace root. Never commit `.env`.

## Schedule (owner 2026-08-16)
- **R&D:** 7 deep slots/day America/Los_Angeles: 07:00, 09:30, 12:00, 14:30, 17:00, 19:30, 22:00
- **X progress:** 1–2 posts morning PT only (08:15 and optional 10:30) when there is a **synthesized takeaway**
- Notify Khoi via **text_message only** (never email lab status)

## Continuity law (owner 2026-08-16 — non-negotiable)
Each turn MUST leave durable notes so the **next** turn knows:
1. what prior turn did
2. **where** (paths/files)
3. what is left
4. the single recommended next move

Source of truth = `docs/SESSIONS/` + `STATE` + `LOG` + git. Not chat memory.
Fail the run if you ship code but skip a new session file.

## BEFORE work
1. Read WORKFLOW, GOAL, STATE, LOG (recent), **latest** `docs/SESSIONS/session-*.md`, TEMPLATE if unsure of shape.
2. Record `git_head_before` (`git rev-parse --short HEAD`).
3. Pick **one** highest-leverage next move from that evidence. No hardcoded micro-task list.
4. If latest session "What left" / "Recommended next" is still open, prefer that unless STATE says otherwise.

## DURING
- Deep multi-layer ships: code + tests + docs + commit + push on real delta
- pytest green via `/home/daytona/workspace/conduit/.venv/bin/pytest`
- Autonomous; no mid-run owner questions for routine choices
- Research for real when stuck; try multiple approaches
- Ban: rename-only, docs-only thrash, toy dashboards, empty "still working"
- Touch files with absolute paths; keep a mental "Where" list for the session file
- When finishing product work, write **Takeaway** (one sharp sentence + proof path/sha) in the session file

## X rules (morning PT jobs only — owner 2026-08-16)
X is a **takeaway post**, not a diary.

**Must synthesize before posting:**
1. Read STATE + LOG recent + last 1–3 session files + `git log -5 --oneline`
2. Extract **one** stranger-facing takeaway (what changed, why it matters for people using Claude Code/Codex/agents)
3. Prefer sessions with non-empty **Takeaway** + proof (commit/path/test). If only vibes / "still building" / no proof → **skip**
4. Draft clean short copy (~420 chars): takeaway first · optional one proof crumb · try/PR invite · agent-run no human in loop · Zinley agent use at own risk · full repo URL · `model: Grok 4.5 · Zinley agent`
5. No spam templates, no personal-AI sermons, no browser-use clone vibes, no dump of raw LOG bullets
6. Max 1–2/day morning PT (08:15 + optional 10:30). Cap 2/day.
7. Via x-growth `x_client` as @khoi_danny; never print secrets
8. text_message Khoi post URL or `skipped: no clean takeaway`
9. Do not heavy R&D in X slots

## BEFORE DONE (always — even fail/lock/skip)
1. Append `docs/LOG.md` (tried / worked / failed / artifacts / shas / X yes-no)
2. **NEW** `docs/SESSIONS/session-YYYYMMDD-HHmm-<slug>.md` using `TEMPLATE.md`:
   - Did + **Where table (paths)** + Results + **What left** + **Recommended next** + **Takeaway** + Do NOT redo + Blockers
   - Continuity checksum = yes before exit
3. Update `docs/STATE.md` (`next` must match Recommended next; status; claims; updated; last_session)
4. `git_head_after`; commit + push material changes (`Co-Authored-By: Uni <agent@zinley.com>`)
5. `text_message` Khoi one-liner (never email lab status)
6. R&D slots: do **not** post X (morning X jobs only)

## Full solve
When GOAL win condition met: `docs/PAPER.md` + STATE solved + climactic X + text.
