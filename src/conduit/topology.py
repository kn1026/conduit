from __future__ import annotations

import ast
import re
from collections import defaultdict
from pathlib import Path

from conduit.models import FileNode, Partition, TopologyPlan

_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))",
    re.M,
)


def _module_name_from_path(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def scan_python_repo(root: str | Path, *, max_files: int = 4000) -> list[FileNode]:
    root = Path(root)
    nodes: list[FileNode] = []
    count = 0
    for path in sorted(root.rglob("*.py")):
        if any(p in {".venv", "venv", "node_modules", ".git", "dist", "build"} for p in path.parts):
            continue
        count += 1
        if count > max_files:
            break
        text = path.read_text(encoding="utf-8", errors="replace")
        imports: list[str] = []
        try:
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        imports.append(a.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split(".")[0])
        except SyntaxError:
            for m in _IMPORT_RE.finditer(text):
                mod = m.group(1) or m.group(2) or ""
                if mod:
                    imports.append(mod.split(".")[0])
        rel = str(path.relative_to(root)).replace("\\", "/")
        # keep local-looking imports only for edges later
        nodes.append(FileNode(path=rel, imports=sorted(set(imports))))
    return nodes


def build_edges(nodes: list[FileNode]) -> list[tuple[str, str]]:
    by_stem = {}
    for n in nodes:
        stem = Path(n.path).stem
        by_stem.setdefault(stem, []).append(n.path)
        # package folder name
        parts = Path(n.path).parts
        if len(parts) >= 2:
            by_stem.setdefault(parts[-2], []).append(n.path)

    edges: set[tuple[str, str]] = set()
    paths = {n.path for n in nodes}
    for n in nodes:
        for imp in n.imports:
            # map import root to files under src/<imp> or <imp>.py
            candidates = []
            for p in paths:
                if p == f"{imp}.py" or p.startswith(f"{imp}/") or f"/{imp}/" in f"/{p}":
                    candidates.append(p)
                if p.endswith(f"/{imp}.py"):
                    candidates.append(p)
            for c in candidates:
                if c != n.path:
                    edges.add((n.path, c))
    return sorted(edges)


def hub_scores(nodes: list[FileNode], edges: list[tuple[str, str]]) -> dict[str, float]:
    score: dict[str, float] = {n.path: 0.0 for n in nodes}
    for a, b in edges:
        score[a] = score.get(a, 0.0) + 1.0
        score[b] = score.get(b, 0.0) + 1.5  # imported-by weighs more
    return score


def partition_by_top_dir(nodes: list[FileNode], scores: dict[str, float]) -> list[Partition]:
    groups: dict[str, list[str]] = defaultdict(list)
    for n in nodes:
        top = n.path.split("/", 1)[0] if "/" in n.path else "_root"
        groups[top].append(n.path)
    parts: list[Partition] = []
    for name, files in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        hub = max((scores.get(f, 0.0) for f in files), default=0.0)
        parts.append(Partition(name=name, files=sorted(files), hub_score=hub))
    return parts


def plan_repo(root: str | Path, *, max_agents: int = 4) -> TopologyPlan:
    """Cohesion-aware-ish planner: static imports + directory communities.

    Not a full Louvain implementation in v0 — directory communities + hub isolation
    give a checkable schedule seed. Later sessions can deepen graph clustering.
    """
    nodes = scan_python_repo(root)
    edges = build_edges(nodes)
    scores = hub_scores(nodes, edges)
    hubs = [p for p, s in sorted(scores.items(), key=lambda kv: -kv[1])[:12] if s > 0]
    parts = partition_by_top_dir(nodes, scores)
    # merge tiny partitions if too many
    if len(parts) > max_agents:
        parts = sorted(parts, key=lambda p: -len(p.files))
        head = parts[: max_agents - 1]
        tail_files: list[str] = []
        for p in parts[max_agents - 1 :]:
            tail_files.extend(p.files)
        head.append(
            Partition(
                name="merged_tail",
                files=sorted(tail_files),
                hub_score=max((scores.get(f, 0.0) for f in tail_files), default=0.0),
            )
        )
        parts = head
    return TopologyPlan(partitions=parts, hubs=hubs, edges=edges)
