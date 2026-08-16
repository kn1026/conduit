from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class EffectStatus(str, Enum):
    INTENDED = "intended"
    LANDED = "landed"
    FAILED = "failed"
    UNKNOWN = "unknown"


class Decision(str, Enum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any] = field(default_factory=dict)
    path: str | None = None
    network: str | None = None


@dataclass
class SideEffect:
    id: str
    tool: str
    target: str
    status: EffectStatus
    idempotency_key: str
    detail: str = ""
    at: str = field(default_factory=utc_now)

    @staticmethod
    def new(
        tool: str,
        target: str,
        status: EffectStatus,
        *,
        idempotency_key: str | None = None,
        detail: str = "",
    ) -> "SideEffect":
        key = idempotency_key or f"{tool}:{target}:{uuid.uuid4().hex[:8]}"
        return SideEffect(
            id=uuid.uuid4().hex[:12],
            tool=tool,
            target=target,
            status=status,
            idempotency_key=key,
            detail=detail,
        )


@dataclass
class Budget:
    max_usd: float | None = None
    max_tokens: int | None = None
    spent_usd: float = 0.0
    spent_tokens: int = 0

    def remaining_ok(self, add_tokens: int = 0, add_usd: float = 0.0) -> bool:
        if self.max_tokens is not None and self.spent_tokens + add_tokens > self.max_tokens:
            return False
        if self.max_usd is not None and self.spent_usd + add_usd > self.max_usd:
            return False
        return True


@dataclass
class Grant:
    """One capability grant with blast accounting hooks."""

    name: str
    pattern: str  # glob-ish tool or path pattern
    decision: Decision = Decision.ALLOW
    expiry: str | None = None
    owner: str | None = None
    blast_radius: str = ""
    notes: str = ""


@dataclass
class Policy:
    name: str
    version: str = "0.1"
    default: Decision = Decision.ASK
    grants: list[Grant] = field(default_factory=list)
    forbidden_write_globs: list[str] = field(
        default_factory=lambda: [
            ".git/hooks/**",
            ".git/config",
            ".git/worktrees/**",
            "**/.env",
            "**/.env.*",
        ]
    )
    budget: Budget = field(default_factory=Budget)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["default"] = self.default.value
        d["grants"] = [
            {**asdict(g), "decision": g.decision.value} for g in self.grants
        ]
        return d


@dataclass
class HandoffPack:
    """Completion-true handoff across agents."""

    id: str
    goal: str
    source_agent: str
    created_at: str = field(default_factory=utc_now)
    why: list[str] = field(default_factory=list)
    open_work: list[str] = field(default_factory=list)
    effects: list[SideEffect] = field(default_factory=list)
    files_touched: list[str] = field(default_factory=list)
    tests: list[dict[str, Any]] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(goal: str, source_agent: str, **meta: Any) -> "HandoffPack":
        return HandoffPack(
            id=uuid.uuid4().hex[:16],
            goal=goal,
            source_agent=source_agent,
            meta=dict(meta),
        )

    def record_effect(self, effect: SideEffect) -> None:
        self.effects.append(effect)

    def completion_gap(self) -> list[SideEffect]:
        """Effects that were intended but never confirmed landed."""
        landed_keys = {
            e.idempotency_key for e in self.effects if e.status == EffectStatus.LANDED
        }
        gaps = []
        for e in self.effects:
            if e.status == EffectStatus.INTENDED and e.idempotency_key not in landed_keys:
                gaps.append(e)
            elif e.status == EffectStatus.FAILED:
                gaps.append(e)
        return gaps

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "source_agent": self.source_agent,
            "created_at": self.created_at,
            "why": list(self.why),
            "open_work": list(self.open_work),
            "effects": [asdict(e) | {"status": e.status.value} for e in self.effects],
            "files_touched": list(self.files_touched),
            "tests": list(self.tests),
            "meta": dict(self.meta),
            "completion_gap": [
                asdict(e) | {"status": e.status.value} for e in self.completion_gap()
            ],
        }


@dataclass
class FileNode:
    path: str
    imports: list[str] = field(default_factory=list)


@dataclass
class Partition:
    name: str
    files: list[str]
    hub_score: float = 0.0


@dataclass
class TopologyPlan:
    partitions: list[Partition]
    hubs: list[str]
    edges: list[tuple[str, str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "hubs": list(self.hubs),
            "edges": [{"from": a, "to": b} for a, b in self.edges],
            "partitions": [
                {"name": p.name, "files": p.files, "hub_score": p.hub_score}
                for p in self.partitions
            ],
        }
