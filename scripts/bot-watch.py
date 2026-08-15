#!/usr/bin/env python3
"""Run on the Grok Bot computer. Watch orders. Ack finished work.

A Bot teammate (or a human) runs this so Hermes is not talking to a dead folder.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from hermes_grokbot.envelope import Envelope, parse
from hermes_grokbot.mailbox import init_mailbox
from hermes_grokbot.protocol import FROM_HERMES, TO_HERMES, sha256_bytes


def main() -> int:
    p = argparse.ArgumentParser(description="Watch FROM-HERMES on the Bot computer")
    p.add_argument("--home", default=".")
    p.add_argument("--ack", default="", help="write this as TO-HERMES and exit")
    p.add_argument("--once", action="store_true")
    args = p.parse_args()
    home = init_mailbox(Path(args.home))
    src = home / FROM_HERMES
    dest = home / TO_HERMES
    if args.ack:
        env = Envelope(body=args.ack, to="hermes", kind="reply", sender="grokbot")
        dest.write_text(env.render(), encoding="utf-8")
        print(f"acked {dest}")
        return 0
    last = ""
    while True:
        if src.is_file():
            data = src.read_bytes()
            digest = sha256_bytes(data)
            if digest != last and data.strip():
                last = digest
                env = parse(data.decode("utf-8", errors="replace"))
                print(f"ORDER id={env.id} to={env.to} kind={env.kind}")
                print(env.body)
                print("---")
        if args.once:
            return 0
        time.sleep(4)


if __name__ == "__main__":
    raise SystemExit(main())
