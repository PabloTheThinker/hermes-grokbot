"""Doctor the merge: net, SSH, mailbox, plugin. No host names baked in."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from . import __version__
from .mailbox import SEATS


def _ok(name: str, ok: bool, detail: str) -> dict:
    return {"check": name, "ok": ok, "detail": detail}


def _run(cmd: list[str], timeout: int = 12) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (r.stdout or r.stderr or "").strip()
        return r.returncode, out[:400]
    except FileNotFoundError:
        return 127, "not installed"
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def doctor(
    home: Path | None = None,
    ssh: str = "",
    remote_home: str = "",
    hermes_home: Path | None = None,
) -> list[dict]:
    home = Path(home or os.getenv("GROKBOT_HOME") or "./inbox")
    ssh = ssh or os.getenv("GROKBOT_SSH") or ""
    remote_home = remote_home or os.getenv("GROKBOT_REMOTE_HOME") or "."
    hermes_home = Path(hermes_home or os.getenv("HERMES_HOME") or (Path.home() / ".hermes"))
    rows = [_ok("version", True, __version__)]

    has_wire = bool(ssh) or home.exists()
    rows.append(_ok("wire", has_wire, "GROKBOT_SSH or GROKBOT_HOME"))

    ts = shutil.which("tailscale")
    if ssh:
        host = ssh.split("@", 1)[-1]
        if ts:
            code, _out = _run(["tailscale", "ping", "-c", "1", host], timeout=10)
            rows.append(_ok("tailscale-ping", code == 0, "reachable" if code == 0 else "unreachable"))
        else:
            rows.append(_ok("tailscale", False, "tailscale not on PATH — install on both machines"))
        if "@" not in ssh or " " in ssh:
            rows.append(_ok("ssh-target", False, "must look like user@host"))
        else:
            code, out = _run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", ssh, "echo", "OK"],
                timeout=15,
            )
            rows.append(_ok("ssh", code == 0, out or "BatchMode failed"))
    else:
        rows.append(_ok("local-home", home.is_dir(), str(home)))
        for rel in ["FROM-HERMES.txt", "TO-HERMES.txt"] + [f"seats/{s}.md" for s in SEATS]:
            p = home / rel
            rows.append(_ok(rel, p.is_file(), "ok" if p.is_file() else "run init"))

    plug = hermes_home / "plugins" / "grokbot" / "adapter.py"
    rows.append(_ok("plugin", plug.is_file(), str(plug)))

    cfg = hermes_home / "config.yaml"
    enabled = False
    if cfg.is_file():
        text = cfg.read_text(encoding="utf-8", errors="replace")
        enabled = "grokbot" in text and "enabled: true" in text
    rows.append(_ok("config-hint", True, "grokbot enabled in config.yaml" if enabled else "run enable-plugin after install"))
    return rows


def format_report(rows: list[dict]) -> str:
    lines = []
    for r in rows:
        mark = "ok" if r["ok"] else "FAIL"
        lines.append(f"{mark:4}  {r['check']}: {r['detail']}")
    return "\n".join(lines) + "\n"


def failed(rows: list[dict]) -> bool:
    return any(not r["ok"] and r["check"] in {"ssh", "tailscale-ping", "ssh-target", "local-home", "wire"} for r in rows)
