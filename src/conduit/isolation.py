from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DANGEROUS_SHARED = (
    ".git/hooks",
    ".git/config",
    ".git/worktrees",
)


@dataclass
class IsolationReport:
    ok: bool
    findings: list[str]
    agent_id: str
    worktree: str | None = None


def path_is_shared_git_state(path: str | Path) -> bool:
    p = Path(path).as_posix()
    for d in DANGEROUS_SHARED:
        if p == d or p.endswith("/" + d) or f"/{d}/" in f"/{p}/" or p.startswith(d + "/"):
            return True
    # also bare names
    if p in {".git/config"}:
        return True
    return False


def assert_write_allowed(path: str | Path, *, agent_root: str | Path | None = None) -> None:
    """Raise PermissionError if write targets shared git state.

    Worktrees alone are NOT isolation. Agents must not mutate parent hooks/config.
    """
    if path_is_shared_git_state(path):
        raise PermissionError(
            f"conduit isolation: refusing write to shared git state: {path}"
        )
    if agent_root is not None:
        root = Path(agent_root).resolve()
        target = Path(path).resolve()
        try:
            target.relative_to(root)
        except ValueError as e:
            raise PermissionError(
                f"conduit isolation: path escapes agent root {root}: {path}"
            ) from e


def doctor_repo(repo: str | Path, *, agent_id: str = "default") -> IsolationReport:
    """Scan a repo for common parallel-agent isolation failures."""
    repo = Path(repo)
    findings: list[str] = []
    git = repo / ".git"
    if not git.exists():
        findings.append("no .git directory (skip git shared-state checks)")
    else:
        hooks = git / "hooks"
        if hooks.is_dir():
            writable = []
            for h in hooks.iterdir():
                if h.is_file() and os_access_write(h):
                    writable.append(h.name)
            if writable:
                findings.append(
                    "git hooks are writable by agent process: "
                    + ", ".join(sorted(writable)[:12])
                    + " — parallel agents can poison parent hooks"
                )
        cfg = git / "config"
        if cfg.exists() and os_access_write(cfg):
            findings.append(".git/config is writable — agents can alter shared git behavior")
        wt = git / "worktrees"
        if wt.exists() and os_access_write(wt):
            findings.append(
                ".git/worktrees is writable — nested worktree bleed is possible"
            )

    # env bleed hint
    env = repo / ".env"
    if env.exists():
        findings.append(
            ".env present at repo root — copy/edit carefully per agent; never share live secrets across parallel agents"
        )

    ok = not any("writable" in f for f in findings)
    return IsolationReport(ok=ok, findings=findings, agent_id=agent_id, worktree=str(repo))


def os_access_write(path: Path) -> bool:
    import os

    return os.access(path, os.W_OK)


def make_agent_env(
    base_env: dict[str, str] | None,
    *,
    agent_id: str,
    docker_project: str | None = None,
) -> dict[str, str]:
    """Fork env for one agent: unique compose project, marker vars."""
    env = dict(base_env or {})
    env["CONDUIT_AGENT_ID"] = agent_id
    env["COMPOSE_PROJECT_NAME"] = docker_project or f"conduit_{agent_id}"
    # discourage accidental cross-talk
    env.setdefault("CONDUIT_ISOLATION", "1")
    return env
