from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from conduit import __version__
from conduit.handoff import load_pack, resume_prompt, save_pack, summarize
from conduit.isolation import doctor_repo
from conduit.models import EffectStatus, HandoffPack, SideEffect
from conduit.policy import DEFAULT_POLICY_YAML, evaluate, load_policy_file, load_policy_yaml
from conduit.models import ToolCall
from conduit.topology import plan_repo


def cmd_version(_: argparse.Namespace) -> int:
    print(f"conduit {__version__}")
    return 0


def cmd_policy_init(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if path.exists() and not args.force:
        print(f"exists: {path} (use --force)", file=sys.stderr)
        return 2
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DEFAULT_POLICY_YAML.strip() + "\n", encoding="utf-8")
    print(f"wrote {path}")
    return 0


def cmd_policy_check(args: argparse.Namespace) -> int:
    policy = load_policy_file(args.policy)
    call = ToolCall(name=args.tool, path=args.path, args={})
    d = evaluate(policy, call)
    print(d.value)
    return 0 if d.value != "deny" else 1


def cmd_doctor(args: argparse.Namespace) -> int:
    report = doctor_repo(args.repo, agent_id=args.agent_id)
    print(json.dumps({
        "ok": report.ok,
        "agent_id": report.agent_id,
        "worktree": report.worktree,
        "findings": report.findings,
    }, indent=2))
    return 0 if report.ok else 1


def cmd_handoff_new(args: argparse.Namespace) -> int:
    pack = HandoffPack.create(args.goal, args.agent, lab="conduit")
    if args.why:
        pack.why.append(args.why)
    path = save_pack(pack, args.out)
    print(path)
    return 0


def cmd_handoff_intend(args: argparse.Namespace) -> int:
    pack = load_pack(args.pack)
    effect = SideEffect.new(args.tool, args.target, EffectStatus.INTENDED, idempotency_key=args.key)
    pack.record_effect(effect)
    save_pack(pack, args.pack)
    print(effect.idempotency_key)
    return 0


def cmd_handoff_land(args: argparse.Namespace) -> int:
    pack = load_pack(args.pack)
    effect = SideEffect.new(args.tool or "confirm", args.target or args.key, EffectStatus.LANDED, idempotency_key=args.key)
    pack.record_effect(effect)
    save_pack(pack, args.pack)
    print("landed", args.key)
    return 0


def cmd_handoff_show(args: argparse.Namespace) -> int:
    pack = load_pack(args.pack)
    print(json.dumps(summarize(pack), indent=2))
    if args.prompt:
        print("---")
        print(resume_prompt(pack), end="")
    return 0


def cmd_topo(args: argparse.Namespace) -> int:
    plan = plan_repo(args.repo, max_agents=args.max_agents)
    print(json.dumps(plan.to_dict(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="conduit", description="Control plane for coding agents")
    p.add_argument("--version", action="store_true")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("version")
    s.set_defaults(func=cmd_version)

    s = sub.add_parser("policy-init", help="Write default policy YAML")
    s.add_argument("--path", default="conduit.policy.yaml")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_policy_init)

    s = sub.add_parser("policy-check", help="Evaluate tool+path against policy")
    s.add_argument("--policy", required=True)
    s.add_argument("--tool", required=True)
    s.add_argument("--path", default=None)
    s.set_defaults(func=cmd_policy_check)

    s = sub.add_parser("doctor", help="Scan repo for parallel-agent isolation issues")
    s.add_argument("--repo", default=".")
    s.add_argument("--agent-id", default="default")
    s.set_defaults(func=cmd_doctor)

    s = sub.add_parser("handoff-new", help="Create empty handoff pack")
    s.add_argument("--goal", required=True)
    s.add_argument("--agent", default="human")
    s.add_argument("--why", default=None)
    s.add_argument("--out", default="handoff.conduit.json")
    s.set_defaults(func=cmd_handoff_new)

    s = sub.add_parser("handoff-intend", help="Record intended side effect")
    s.add_argument("--pack", required=True)
    s.add_argument("--tool", required=True)
    s.add_argument("--target", required=True)
    s.add_argument("--key", default=None)
    s.set_defaults(func=cmd_handoff_intend)

    s = sub.add_parser("handoff-land", help="Record landed side effect")
    s.add_argument("--pack", required=True)
    s.add_argument("--key", required=True)
    s.add_argument("--tool", default=None)
    s.add_argument("--target", default=None)
    s.set_defaults(func=cmd_handoff_land)

    s = sub.add_parser("handoff-show", help="Summarize pack / emit resume prompt")
    s.add_argument("--pack", required=True)
    s.add_argument("--prompt", action="store_true")
    s.set_defaults(func=cmd_handoff_show)

    s = sub.add_parser("topo", help="Cohesion-ish partition plan for a python repo")
    s.add_argument("--repo", default=".")
    s.add_argument("--max-agents", type=int, default=4)
    s.set_defaults(func=cmd_topo)

    return p


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "version", False) and not getattr(args, "cmd", None):
        raise SystemExit(cmd_version(args))
    if not getattr(args, "cmd", None):
        parser.print_help()
        raise SystemExit(2)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
