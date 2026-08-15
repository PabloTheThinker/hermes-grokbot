"""Job envelopes. The merge is not a single overwrite of a text file."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field

SEATS = ("chief", "watch", "recon", "homework")
KINDS = ("order", "reply", "status", "approval")
HEAD = "---hgb-1"
SAFE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


@dataclass
class Envelope:
    body: str
    to: str = "chief"
    kind: str = "order"
    sender: str = "hermes"
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def render(self) -> str:
        to = self.to if SAFE.match(self.to) else "chief"
        kind = self.kind if self.kind in KINDS else "order"
        sender = self.sender if SAFE.match(self.sender) else "hermes"
        body = (self.body or "").replace("\r\n", "\n").strip()
        return (
            f"{HEAD}\n"
            f"id: {self.id}\n"
            f"from: {sender}\n"
            f"to: {to}\n"
            f"kind: {kind}\n"
            f"---\n"
            f"{body}\n"
        )


def parse(text: str) -> Envelope:
    raw = (text or "").replace("\r\n", "\n")
    if not raw.lstrip().startswith(HEAD):
        return Envelope(body=raw.strip(), to="chief", kind="order", sender="peer")
    lines = raw.lstrip().split("\n")
    meta: dict[str, str] = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            meta[k.strip()] = v.strip()
        i += 1
    body = "\n".join(lines[i + 1 :]).strip() if i < len(lines) else ""
    sender = meta.get("from") or "peer"
    dest = meta.get("to") or "chief"
    kind = meta.get("kind") or "order"
    eid = meta.get("id") or uuid.uuid4().hex[:12]
    if not SAFE.match(sender):
        sender = "peer"
    if dest not in SEATS:
        dest = "chief"
    if kind not in KINDS:
        kind = "order"
    return Envelope(body=body, to=dest, kind=kind, sender=sender, id=eid)
