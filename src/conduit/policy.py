from __future__ import annotations

import fnmatch
from pathlib import PurePosixPath
from typing import Any

import yaml

from conduit.models import Budget, Decision, Grant, Policy, ToolCall


def _norm(path: str | None) -> str:
    if not path:
        return ""
    p = path.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def path_matches(pattern: str, path: str) -> bool:
    path = _norm(path)
    pattern = pattern.replace("\\", "/")
    if pattern.endswith("/**"):
        root = pattern[:-3].rstrip("/")
        return path == root or path.startswith(root + "/")
    if "**" in pattern:
        # coarse: convert ** to * for fnmatch after norm
        return fnmatch.fnmatch(path, pattern.replace("**/", "*").replace("**", "*"))
    return fnmatch.fnmatch(path, pattern) or PurePosixPath(path).match(pattern)


def load_policy_dict(data: dict[str, Any]) -> Policy:
    grants = []
    for g in data.get("grants") or []:
        grants.append(
            Grant(
                name=g.get("name") or g.get("pattern") or "grant",
                pattern=g["pattern"],
                decision=Decision(g.get("decision", "allow")),
                expiry=g.get("expiry"),
                owner=g.get("owner"),
                blast_radius=g.get("blast_radius") or "",
                notes=g.get("notes") or "",
            )
        )
    b = data.get("budget") or {}
    budget = Budget(
        max_usd=b.get("max_usd"),
        max_tokens=b.get("max_tokens"),
        spent_usd=float(b.get("spent_usd") or 0),
        spent_tokens=int(b.get("spent_tokens") or 0),
    )
    return Policy(
        name=data.get("name") or "default",
        version=str(data.get("version") or "0.1"),
        default=Decision(data.get("default") or "ask"),
        grants=grants,
        forbidden_write_globs=list(
            data.get("forbidden_write_globs")
            or Policy().forbidden_write_globs
        ),
        budget=budget,
    )


def load_policy_yaml(text: str) -> Policy:
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError("policy root must be a mapping")
    return load_policy_dict(data)


def load_policy_file(path: str) -> Policy:
    with open(path, encoding="utf-8") as f:
        return load_policy_yaml(f.read())


def is_forbidden_write(policy: Policy, path: str | None) -> bool:
    if not path:
        return False
    for pat in policy.forbidden_write_globs:
        if path_matches(pat, path):
            return True
    # hard absolute denies for git shared state
    n = _norm(path)
    if n == ".git/config" or n.startswith(".git/hooks/") or n.startswith(".git/worktrees/"):
        return True
    if n.endswith("/.git/config") or "/.git/hooks/" in n or "/.git/worktrees/" in n:
        return True
    return False


def evaluate(policy: Policy, call: ToolCall) -> Decision:
    """Evaluate a tool call against policy. Deny beats allow."""
    name = (call.name or "").lower()
    path = call.path

    # budget gate (tokens optional pre-check)
    if not policy.budget.remaining_ok():
        return Decision.DENY

    writey = name in {
        "write",
        "edit",
        "bash",
        "shell",
        "delete",
        "rm",
        "git",
        "apply_patch",
        "str_replace",
    }
    if writey and is_forbidden_write(policy, path):
        return Decision.DENY

    matched: list[Grant] = []
    for g in policy.grants:
        if path and path_matches(g.pattern, path):
            matched.append(g)
        elif not path and fnmatch.fnmatch(name, g.pattern):
            matched.append(g)
        elif fnmatch.fnmatch(f"{name}:{_norm(path)}", g.pattern):
            matched.append(g)

    if any(g.decision == Decision.DENY for g in matched):
        return Decision.DENY
    if any(g.decision == Decision.ALLOW for g in matched):
        return Decision.ALLOW
    if any(g.decision == Decision.ASK for g in matched):
        return Decision.ASK
    return policy.default


DEFAULT_POLICY_YAML = """
name: conduit-default
version: "0.1"
default: ask
budget:
  max_usd: 25.0
  max_tokens: 2000000
forbidden_write_globs:
  - ".git/hooks/**"
  - ".git/config"
  - ".git/worktrees/**"
  - "**/.env"
  - "**/.env.*"
grants:
  - name: read-src
    pattern: "src/**"
    decision: allow
    owner: team
  - name: read-tests
    pattern: "tests/**"
    decision: allow
  - name: deny-git-hooks
    pattern: ".git/hooks/**"
    decision: deny
  - name: shell-readonly-ish
    pattern: "bash"
    decision: ask
"""
