from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CostMeter:
    """Track tokens / rough USD / failed tool loops for one run."""

    model: str = "unknown"
    input_tokens: int = 0
    output_tokens: int = 0
    usd_per_1m_input: float = 0.0
    usd_per_1m_output: float = 0.0
    tool_calls: int = 0
    tool_failures: int = 0
    denial_retries: int = 0
    notes: list[str] = field(default_factory=list)

    def add_usage(self, *, input_tokens: int = 0, output_tokens: int = 0) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def add_tool(self, *, failed: bool = False, denial: bool = False) -> None:
        self.tool_calls += 1
        if failed:
            self.tool_failures += 1
        if denial:
            self.denial_retries += 1

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def est_usd(self) -> float:
        return (
            self.input_tokens / 1_000_000.0 * self.usd_per_1m_input
            + self.output_tokens / 1_000_000.0 * self.usd_per_1m_output
        )

    def waste_ratio(self) -> float:
        if self.tool_calls == 0:
            return 0.0
        return (self.tool_failures + self.denial_retries) / float(self.tool_calls)

    def summary(self) -> dict:
        return {
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "est_usd": round(self.est_usd, 6),
            "tool_calls": self.tool_calls,
            "tool_failures": self.tool_failures,
            "denial_retries": self.denial_retries,
            "waste_ratio": round(self.waste_ratio(), 4),
            "notes": list(self.notes),
        }
