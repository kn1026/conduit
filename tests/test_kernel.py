from conduit.kernel import ConduitKernel
from conduit.models import HandoffPack, ToolCall
from conduit.policy import DEFAULT_POLICY_YAML, load_policy_yaml


def test_kernel_blocks_hook_and_tracks_gap():
    policy = load_policy_yaml(DEFAULT_POLICY_YAML)
    pack = HandoffPack.create("safe edit", "test")
    k = ConduitKernel(policy=policy, pack=pack)
    r = k.check(ToolCall(name="write", path=".git/hooks/pre-commit"))
    assert r.allowed is False
    eff = k.begin_effect("edit", "src/x.py", key="e1")
    assert eff.idempotency_key == "e1"
    assert len(pack.completion_gap()) == 1
    k.land_effect("e1")
    assert pack.completion_gap() == []
