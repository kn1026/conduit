from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from conduit.cost import CostMeter
from conduit.isolation import assert_write_allowed
from conduit.models import Decision, EffectStatus, HandoffPack, SideEffect, ToolCall
from conduit.policy import Policy, evaluate


@dataclass
class KernelResult:
    decision: Decision
    allowed: bool
    reason: str
    effect: SideEffect | None = None


@dataclass
class ConduitKernel:
    """Process-local control plane: policy + isolation + ledger + cost."""

    policy: Policy
    pack: HandoffPack
    meter: CostMeter = field(default_factory=CostMeter)
    agent_root: str | None = None

    def check(self, call: ToolCall) -> KernelResult:
        decision = evaluate(self.policy, call)
        if decision == Decision.DENY:
            self.meter.add_tool(failed=True, denial=True)
            return KernelResult(decision, False, "policy denied")
        if decision == Decision.ASK:
            return KernelResult(decision, False, "policy requires approval")
        # isolation on write-like
        if call.path and call.name.lower() in {"write", "edit", "delete", "bash", "shell"}:
            try:
                assert_write_allowed(call.path, agent_root=self.agent_root)
            except PermissionError as e:
                self.meter.add_tool(failed=True, denial=True)
                return KernelResult(Decision.DENY, False, str(e))
        return KernelResult(decision, True, "ok")

    def begin_effect(self, tool: str, target: str, *, key: str | None = None) -> SideEffect:
        effect = SideEffect.new(tool, target, EffectStatus.INTENDED, idempotency_key=key)
        self.pack.record_effect(effect)
        return effect

    def land_effect(self, key: str, *, detail: str = "") -> SideEffect:
        effect = SideEffect.new("confirm", key, EffectStatus.LANDED, idempotency_key=key, detail=detail)
        # preserve tool/target if known
        for e in self.pack.effects:
            if e.idempotency_key == key and e.status == EffectStatus.INTENDED:
                effect = SideEffect.new(
                    e.tool, e.target, EffectStatus.LANDED, idempotency_key=key, detail=detail
                )
                break
        self.pack.record_effect(effect)
        self.meter.add_tool(failed=False)
        return effect

    def fail_effect(self, key: str, *, detail: str = "") -> SideEffect:
        tool, target = "unknown", key
        for e in self.pack.effects:
            if e.idempotency_key == key:
                tool, target = e.tool, e.target
                break
        effect = SideEffect.new(tool, target, EffectStatus.FAILED, idempotency_key=key, detail=detail)
        self.pack.record_effect(effect)
        self.meter.add_tool(failed=True)
        return effect

    def snapshot(self) -> dict[str, Any]:
        return {
            "policy": self.policy.name,
            "pack": self.pack.to_dict(),
            "cost": self.meter.summary(),
            "completion_gap": len(self.pack.completion_gap()),
        }
