from pathlib import Path

from conduit.cli import main


def test_cli_policy_and_handoff(tmp_path: Path, capsys):
    pol = tmp_path / "p.yaml"
    try:
        main(["policy-init", "--path", str(pol)])
    except SystemExit as e:
        assert e.code == 0
    pack = tmp_path / "h.json"
    try:
        main(["handoff-new", "--goal", "demo", "--agent", "t", "--out", str(pack)])
    except SystemExit as e:
        assert e.code == 0
    assert pack.exists()
    try:
        main(["handoff-show", "--pack", str(pack)])
    except SystemExit as e:
        assert e.code == 0
