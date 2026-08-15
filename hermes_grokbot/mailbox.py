"""Mailbox layout on the shared Grok Bot computer.

One account = one computer. Named seats are files, not vaults.
"""

from __future__ import annotations

from pathlib import Path

from .envelope import Envelope
from .protocol import FROM_HERMES, TO_HERMES, inbox_path

SEATS = ("watch", "recon", "homework")
STATE = ".last-pull.sha256"


def init_mailbox(home: Path) -> Path:
    home = Path(home).expanduser()
    home.mkdir(parents=True, exist_ok=True)
    for name in ("routines", "seats", "approvals", "inbox", "outbox"):
        (home / name).mkdir(exist_ok=True)
    readme = home / "README.txt"
    if not readme.exists():
        readme.write_text(
            "Grok Bot mailbox (hermes-grokbot)\n"
            f"  {FROM_HERMES}  — latest order from Hermes\n"
            f"  {TO_HERMES}    — latest finished work back\n"
            "  seats/         — one job each (watch, recon, homework)\n"
            "  outbox/        — queued orders (do not clobber)\n"
            "  inbox/         — queued replies\n"
            "  routines/      — a run that happened twice becomes a file\n"
            "  approvals/     — human GO for spend, public, new logins\n"
            "One shared computer. Not a per-seat vault.\n"
        )
    for seat in SEATS:
        p = home / "seats" / f"{seat}.md"
        if not p.exists():
            p.write_text(f"# {seat}\n\nJob: one line.\nStatus: idle\nLast:\n")
    inbox_path(home, FROM_HERMES).touch()
    inbox_path(home, TO_HERMES).touch()
    return home.resolve()


def last_hash(state_dir: Path) -> str:
    p = state_dir / STATE
    return p.read_text().strip() if p.is_file() else ""


def write_hash(state_dir: Path, digest: str) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / STATE).write_text(digest + "\n")


def assign(home: Path, seat: str, body: str) -> Path:
    if seat not in SEATS and seat != "chief":
        raise ValueError("unknown seat")
    home = init_mailbox(home)
    env = Envelope(body=body, to=seat, kind="order", sender="hermes")
    rendered = env.render()
    from .drop import drop

    drop(home, rendered)
    if seat in SEATS:
        (home / "seats" / f"{seat}.md").write_text(
            f"# {seat}\n\nJob: {body.strip()}\nStatus: assigned\nLast: {env.id}\n"
        )
    queued = home / "outbox" / f"{env.id}.txt"
    queued.write_text(rendered, encoding="utf-8")
    return queued
