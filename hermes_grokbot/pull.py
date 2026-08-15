"""Copy TO-HERMES.txt from a remote inbox over SSH, or from a local path."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .protocol import TO_HERMES, inbox_path, sha256_bytes


def pull_local(src_home: Path, dest: Path) -> tuple[bytes, str] | None:
    src = inbox_path(src_home, TO_HERMES)
    if not src.is_file() or src.stat().st_size == 0:
        return None
    data = src.read_bytes()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return data, sha256_bytes(data)


def pull_ssh(ssh_target: str, remote_home: str, dest: Path, timeout: int = 20) -> tuple[bytes, str] | None:
    if "@" not in ssh_target or " " in ssh_target:
        raise ValueError("ssh target must look like user@host")
    remote = f"{remote_home.rstrip('/')}/{TO_HERMES}"
    r = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", ssh_target, "cat", remote],
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if r.returncode != 0 or not r.stdout:
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.stdout)
    return r.stdout, sha256_bytes(r.stdout)
