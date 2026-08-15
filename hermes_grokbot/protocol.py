"""Shared file names and safe path rules. No host names, no secrets."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

FROM_HERMES = "FROM-HERMES.txt"
TO_HERMES = "TO-HERMES.txt"
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]{1,80}$")


def inbox_path(home: Path, name: str) -> Path:
    if not SAFE_NAME.match(name):
        raise ValueError("unsafe file name")
    home = Path(home).expanduser().resolve()
    dest = (home / name).resolve()
    if not str(dest).startswith(str(home)):
        raise ValueError("path escape")
    return dest


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def normalize_body(text: str) -> str:
    text = text.replace("\r\n", "\n").strip() + "\n"
    if len(text.encode()) > 200_000:
        raise ValueError("body too large")
    return text
