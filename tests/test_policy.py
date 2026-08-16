from conduit.models import ToolCall
from conduit.policy import DEFAULT_POLICY_YAML, evaluate, is_forbidden_write, load_policy_yaml


def test_forbidden_git_hooks():
    p = load_policy_yaml(DEFAULT_POLICY_YAML)
    assert is_forbidden_write(p, ".git/hooks/pre-commit")
    assert is_forbidden_write(p, ".git/config")
    assert is_forbidden_write(p, "src/foo.py") is False


def test_deny_hook_write():
    p = load_policy_yaml(DEFAULT_POLICY_YAML)
    d = evaluate(p, ToolCall(name="write", path=".git/hooks/pre-commit"))
    assert d.value == "deny"


def test_allow_src_read_pattern():
    p = load_policy_yaml(DEFAULT_POLICY_YAML)
    d = evaluate(p, ToolCall(name="read", path="src/conduit/cli.py"))
    assert d.value == "allow"
