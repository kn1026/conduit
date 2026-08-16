from pathlib import Path

from conduit.topology import plan_repo


def test_plan_self(tmp_path: Path):
    # minimal fake package
    pkg = tmp_path / "src" / "demo"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "a.py").write_text("from demo import b\n")
    (pkg / "b.py").write_text("x = 1\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("def test_ok():\n    assert True\n")
    plan = plan_repo(tmp_path, max_agents=3)
    assert plan.partitions
    names = {p.name for p in plan.partitions}
    assert "src" in names or "tests" in names or "_root" in names
