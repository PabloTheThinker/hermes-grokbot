"""Copy the gateway plugin into $HERMES_HOME/plugins/grokbot."""

from __future__ import annotations

import shutil
from pathlib import Path


def plugin_src() -> Path:
    here = Path(__file__).resolve().parent
    bundled = here / "gateway_plugin"
    if (bundled / "adapter.py").is_file():
        return bundled
    return here.parent / "plugins" / "grokbot"


def install_plugin(hermes_home: Path | None = None) -> Path:
    home = Path(hermes_home or Path.home() / ".hermes")
    dest = home / "plugins" / "grokbot"
    src = plugin_src()
    if not src.is_dir():
        raise FileNotFoundError("plugins/grokbot missing from package")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    return dest
