"""Write FROM-HERMES.txt into a local inbox directory."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from .protocol import FROM_HERMES, inbox_path, normalize_body, sha256_bytes


def drop(home: Path, body: str) -> tuple[Path, str]:
    dest = inbox_path(home, FROM_HERMES)
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = normalize_body(body).encode()
    dest.write_bytes(data)
    dest.chmod(0o644)
    return dest, sha256_bytes(data)


def drop_ssh(ssh_target: str, remote_home: str, body: str, timeout: int = 20) -> str:
    if "@" not in ssh_target or " " in ssh_target:
        raise ValueError("ssh target must look like user@host")
    with tempfile.TemporaryDirectory() as d:
        path, digest = drop(Path(d), body)
        remote = f"{remote_home.rstrip('/')}/{FROM_HERMES}"
        r = subprocess.run(
            [
                "scp",
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=8",
                str(path),
                f"{ssh_target}:{remote}",
            ],
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if r.returncode != 0:
            raise RuntimeError("scp failed")
        return digest
