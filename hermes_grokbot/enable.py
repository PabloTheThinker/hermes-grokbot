"""Enable the grokbot platform without clobbering other Hermes plugins."""

from __future__ import annotations

import shutil
from pathlib import Path


def enable_in_config(config_path: Path) -> str:
    path = Path(config_path)
    if not path.is_file():
        return "missing-config"
    bak = path.with_suffix(path.suffix + ".bak-grokbot")
    if not bak.exists():
        shutil.copy2(path, bak)
    try:
        import yaml  # type: ignore
    except ImportError:
        return "need-pyyaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    plugins = data.setdefault("plugins", {})
    enabled = list(plugins.get("enabled") or [])
    if "grokbot-platform" not in enabled and "grokbot" not in enabled:
        enabled.append("grokbot-platform")
        plugins["enabled"] = list(dict.fromkeys(enabled))
    gw = data.setdefault("gateway", {})
    plats = gw.setdefault("platforms", {})
    grok = plats.setdefault("grokbot", {})
    grok["enabled"] = True
    grok.setdefault("extra", {})
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return "enabled"
