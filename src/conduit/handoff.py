from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from conduit.models import EffectStatus, HandoffPack, SideEffect


PACK_VERSION = 1


def save_pack(pack: HandoffPack, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "conduit_pack_version": PACK_VERSION,
        "pack": pack.to_dict(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def load_pack(path: str | Path) -> HandoffPack:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    raw = data.get("pack") or data
    pack = HandoffPack(
        id=raw["id"],
        goal=raw["goal"],
        source_agent=raw["source_agent"],
        created_at=raw.get("created_at") or "",
        why=list(raw.get("why") or []),
        open_work=list(raw.get("open_work") or []),
        files_touched=list(raw.get("files_touched") or []),
        tests=list(raw.get("tests") or []),
        meta=dict(raw.get("meta") or {}),
    )
    for e in raw.get("effects") or []:
        pack.effects.append(
            SideEffect(
                id=e.get("id") or "",
                tool=e.get("tool") or "",
                target=e.get("target") or "",
                status=EffectStatus(e.get("status") or "unknown"),
                idempotency_key=e.get("idempotency_key") or "",
                detail=e.get("detail") or "",
                at=e.get("at") or "",
            )
        )
    return pack


def resume_prompt(pack: HandoffPack) -> str:
    """Seed prompt for the next agent — explicit artifact, not chat paste."""
    gaps = pack.completion_gap()
    lines = [
        f"# Conduit handoff {pack.id}",
        f"Source agent: {pack.source_agent}",
        f"Goal: {pack.goal}",
        "",
        "## Why (survives compaction)",
    ]
    lines.extend(f"- {w}" for w in (pack.why or ["(none recorded)"]))
    lines.extend(["", "## Open work"])
    lines.extend(f"- {w}" for w in (pack.open_work or ["(none)"]))
    lines.extend(["", "## Files touched"])
    lines.extend(f"- {f}" for f in (pack.files_touched or ["(none)"]))
    lines.extend(["", "## Completion gaps (intended but not landed)"])
    if not gaps:
        lines.append("- none")
    else:
        for g in gaps:
            lines.append(f"- {g.tool} {g.target} [{g.status.value}] key={g.idempotency_key}")
    lines.extend(
        [
            "",
            "## Rules",
            "- Do not assume intended side effects completed.",
            "- Re-read files before edit.",
            "- Record LANDED effects with the same idempotency_key.",
        ]
    )
    return "\n".join(lines) + "\n"


def mark_landed(pack: HandoffPack, idempotency_key: str, *, detail: str = "") -> SideEffect:
    # find intended
    target = ""
    tool = ""
    for e in pack.effects:
        if e.idempotency_key == idempotency_key:
            target = e.target
            tool = e.tool
            break
    effect = SideEffect.new(
        tool=tool or "unknown",
        target=target or idempotency_key,
        status=EffectStatus.LANDED,
        idempotency_key=idempotency_key,
        detail=detail,
    )
    pack.record_effect(effect)
    return effect


def summarize(pack: HandoffPack) -> dict[str, Any]:
    gaps = pack.completion_gap()
    return {
        "id": pack.id,
        "goal": pack.goal,
        "source_agent": pack.source_agent,
        "effects": len(pack.effects),
        "gaps": len(gaps),
        "files": len(pack.files_touched),
        "open_work": len(pack.open_work),
        "trustworthy_resume": len(gaps) == 0,
    }
