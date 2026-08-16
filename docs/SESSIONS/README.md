# Sessions — handoff chain (mandatory)

Owner rule: **every turn must leave notes** so the next turn knows what the previous turn did, **where** (paths), **what is left**, then iterate. Chat history is NOT the source of truth — these files are.

## Rules
1. **New file every run:** `session-YYYYMMDD-HHmm-<slug>.md` (never overwrite old sessions).
2. Copy structure from `TEMPLATE.md`. Fill every section; no empty "Did" / "What left".
3. **Where table is required** — list real paths under `/home/daytona/workspace/conduit`.
4. **What left** must be enough for a cold agent that only reads GOAL + STATE + latest session.
5. Update `docs/STATE.md` `next` to match **Recommended next**.
6. Append a short pointer line to `docs/LOG.md` (session filename + sha).
7. Commit + push session files with the code delta.
8. **Takeaway** section: one stranger-facing sentence + proof. Empty takeaway = not X-worthy (X jobs must skip).

## Read order (start of every R&D turn)
1. `docs/WORKFLOW.md`
2. `docs/GOAL.md`
3. `docs/STATE.md`
4. `docs/LOG.md` (recent)
5. **latest** `docs/SESSIONS/session-*.md` (by name/time)
6. Then work. Then write the new session before exit.
