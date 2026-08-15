"""CLI: hermes-grokbot init|doctor|drop|pull|assign|status|install-plugin|enable-plugin|hash"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .drop import drop, drop_ssh
from .mailbox import assign, init_mailbox, last_hash, write_hash
from .protocol import sha256_file
from .pull import pull_local, pull_ssh


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="hermes-grokbot",
        description="Merge Hermes Agent with a Grok Bot computer",
    )
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="create mailbox: seats, inbox, outbox, approvals")
    i.add_argument("--home", default=os.environ.get("GROKBOT_HOME", "./inbox"))

    doc = sub.add_parser("doctor", help="check Tailscale, SSH, mailbox, plugin")
    doc.add_argument("--home", default=os.environ.get("GROKBOT_HOME", "./inbox"))
    doc.add_argument("--ssh", default=os.environ.get("GROKBOT_SSH", ""))
    doc.add_argument("--remote-home", default=os.environ.get("GROKBOT_REMOTE_HOME", "."))

    sub.add_parser("install-plugin", help="copy gateway plugin into $HERMES_HOME/plugins/grokbot")
    en = sub.add_parser("enable-plugin", help="merge grokbot into Hermes config.yaml (no clobber)")
    en.add_argument(
        "--config",
        default=os.environ.get("HERMES_CONFIG")
        or str(Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / "config.yaml"),
    )

    d = sub.add_parser("drop", help="write FROM-HERMES.txt")
    d.add_argument("--home", default=os.environ.get("GROKBOT_HOME", "./inbox"))
    d.add_argument("--body", default="")
    d.add_argument("--body-file", default="")
    d.add_argument("--ssh", default=os.environ.get("GROKBOT_SSH", ""))
    d.add_argument("--remote-home", default=os.environ.get("GROKBOT_REMOTE_HOME", "."))

    a = sub.add_parser("assign", help="envelope + seat file + outbox (the merge job)")
    a.add_argument("--home", default=os.environ.get("GROKBOT_HOME", "./inbox"))
    a.add_argument("--seat", default="watch", choices=["chief", "watch", "recon", "homework"])
    a.add_argument("--body", required=True)

    u = sub.add_parser("pull", help="copy TO-HERMES.txt")
    u.add_argument("--home", default=os.environ.get("GROKBOT_HOME", "./inbox"))
    u.add_argument("--dest", default="./TO-HERMES.txt")
    u.add_argument("--ssh", default=os.environ.get("GROKBOT_SSH", ""))
    u.add_argument("--remote-home", default=os.environ.get("GROKBOT_REMOTE_HOME", "."))
    u.add_argument("--state-dir", default=os.environ.get("GROKBOT_STATE", "."))
    u.add_argument("--force", action="store_true", help="ignore last hash")

    s = sub.add_parser("status", help="show mailbox files")
    s.add_argument("--home", default=os.environ.get("GROKBOT_HOME", "./inbox"))

    h = sub.add_parser("hash", help="sha256 a file")
    h.add_argument("path")

    args = p.parse_args(argv)
    if args.cmd == "init":
        print(f"ready {init_mailbox(Path(args.home))}")
        return 0
    if args.cmd == "doctor":
        from .doctor import doctor, failed, format_report

        rows = doctor(Path(args.home), ssh=args.ssh, remote_home=args.remote_home)
        sys.stdout.write(format_report(rows))
        return 1 if failed(rows) else 0
    if args.cmd == "install-plugin":
        from .install import install_plugin

        dest = install_plugin(Path(os.environ["HERMES_HOME"]) if os.environ.get("HERMES_HOME") else None)
        print(f"plugin {dest}")
        return 0
    if args.cmd == "enable-plugin":
        from .enable import enable_in_config

        print(enable_in_config(Path(args.config)))
        return 0
    if args.cmd == "assign":
        path = assign(Path(args.home), args.seat, args.body)
        print(f"assigned {args.seat} {path}")
        return 0
    if args.cmd == "drop":
        if args.body_file:
            body = Path(args.body_file).read_text(encoding="utf-8")
        else:
            body = args.body or sys.stdin.read()
        if getattr(args, "ssh", ""):
            digest = drop_ssh(args.ssh, args.remote_home, body)
            print(f"dropped ssh sha256={digest}")
            return 0
        path, digest = drop(Path(args.home), body)
        print(f"dropped {path} sha256={digest}")
        return 0
    if args.cmd == "pull":
        dest = Path(args.dest)
        if args.ssh:
            got = pull_ssh(args.ssh, args.remote_home, dest)
        else:
            got = pull_local(Path(args.home), dest)
        if not got:
            print("no message")
            return 1
        _data, digest = got
        state = Path(args.state_dir)
        if not args.force and digest == last_hash(state):
            print("unchanged")
            return 2
        write_hash(state, digest)
        print(f"pulled {dest} sha256={digest}")
        return 0
    if args.cmd == "status":
        home = Path(args.home)
        for rel in (
            "FROM-HERMES.txt",
            "TO-HERMES.txt",
            "seats/watch.md",
            "seats/recon.md",
            "seats/homework.md",
            "outbox",
            "inbox",
        ):
            pth = home / rel
            mark = "ok" if pth.exists() else "missing"
            print(f"{mark:8} {rel}")
        return 0
    print(sha256_file(Path(args.path)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
