import pytest

from conduit.isolation import assert_write_allowed, make_agent_env, path_is_shared_git_state


def test_shared_git_state_detection():
    assert path_is_shared_git_state(".git/hooks/pre-commit")
    assert path_is_shared_git_state(".git/config")
    assert path_is_shared_git_state("foo/.git/worktrees/x")
    assert not path_is_shared_git_state("src/conduit/cli.py")


def test_assert_write_blocks_hooks():
    with pytest.raises(PermissionError):
        assert_write_allowed(".git/hooks/pre-commit")


def test_agent_env_unique_compose():
    env = make_agent_env({}, agent_id="a1")
    assert env["CONDUIT_AGENT_ID"] == "a1"
    assert env["COMPOSE_PROJECT_NAME"] == "conduit_a1"
