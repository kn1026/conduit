from pathlib import Path

from conduit.handoff import load_pack, resume_prompt, save_pack, summarize
from conduit.models import EffectStatus, HandoffPack, SideEffect


def test_completion_gap(tmp_path: Path):
    pack = HandoffPack.create("ship feature", "claude-code")
    e = SideEffect.new("edit", "src/a.py", EffectStatus.INTENDED, idempotency_key="k1")
    pack.record_effect(e)
    assert len(pack.completion_gap()) == 1
    pack.record_effect(
        SideEffect.new("edit", "src/a.py", EffectStatus.LANDED, idempotency_key="k1")
    )
    assert pack.completion_gap() == []
    path = save_pack(pack, tmp_path / "p.json")
    loaded = load_pack(path)
    assert summarize(loaded)["trustworthy_resume"] is True
    text = resume_prompt(loaded)
    assert "Conduit handoff" in text
    assert "ship feature" in text
