"""Hermes gateway platform: Grok Bot computer.

Inbound: poll TO-HERMES.txt (local or SSH) → Hermes turn.
Outbound: write FROM-HERMES.txt (local or SSH).
Tools: grokbot_doctor, grokbot_assign.
This is the merge — same agent loop as Telegram, different body.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from gateway.config import Platform
    from gateway.platforms.base import (
        BasePlatformAdapter,
        MessageEvent,
        MessageType,
        SendResult,
    )
except ImportError:  # pragma: no cover — loaded only inside Hermes
    BasePlatformAdapter = object  # type: ignore
    MessageEvent = None  # type: ignore
    MessageType = None  # type: ignore
    SendResult = None  # type: ignore
    Platform = None  # type: ignore


def _home() -> str:
    return (os.getenv("GROKBOT_HOME") or "").strip()


def _ssh() -> str:
    return (os.getenv("GROKBOT_SSH") or "").strip()


class GrokBotAdapter(BasePlatformAdapter):
    def __init__(self, config, **kwargs):
        extra = getattr(config, "extra", None) or {}
        super().__init__(config=config, platform=Platform("grokbot"))
        self.local_home = Path(os.getenv("GROKBOT_HOME") or extra.get("home") or "")
        self.ssh = os.getenv("GROKBOT_SSH") or extra.get("ssh") or ""
        self.remote_home = os.getenv("GROKBOT_REMOTE_HOME") or extra.get("remote_home") or "."
        try:
            self.poll = float(os.getenv("GROKBOT_POLL_INTERVAL") or extra.get("poll_interval") or 8)
        except (TypeError, ValueError):
            self.poll = 8.0
        self._task = None
        self._last = ""

    @property
    def name(self) -> str:
        return "Grok Bot"

    async def connect(self, *, is_reconnect: bool = False) -> bool:
        if not self.ssh and not str(self.local_home):
            logger.error("Grok Bot: set GROKBOT_HOME or GROKBOT_SSH")
            return False
        self._task = asyncio.create_task(self._poll_loop())
        self._mark_connected()
        logger.info("Grok Bot: merged — polling mailbox")
        return True

    async def disconnect(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        from hermes_grokbot.drop import drop, drop_ssh
        from hermes_grokbot.envelope import Envelope

        text = (content or "").strip()
        if not text:
            return SendResult(success=False)
        env = Envelope(body=text, to=str(chat_id or "chief"), kind="order", sender="hermes")
        payload = env.render()
        try:
            if self.ssh:
                drop_ssh(self.ssh, self.remote_home, payload)
            else:
                drop(self.local_home, payload)
            return SendResult(success=True, message_id=env.id)
        except Exception as exc:
            logger.error("Grok Bot send failed: %s", exc)
            return SendResult(success=False)

    async def get_chat_info(self, chat_id):
        return {"name": chat_id or "chief", "type": "group"}

    async def _poll_loop(self) -> None:
        from hermes_grokbot.envelope import parse
        from hermes_grokbot.pull import pull_local, pull_ssh

        dest = Path(os.getenv("GROKBOT_STATE") or ".") / "TO-HERMES.poll.txt"
        while True:
            try:
                await asyncio.sleep(self.poll)
                if self.ssh:
                    got = await asyncio.to_thread(pull_ssh, self.ssh, self.remote_home, dest)
                else:
                    got = await asyncio.to_thread(pull_local, self.local_home, dest)
                if not got:
                    continue
                _data, digest = got
                if digest == self._last:
                    continue
                self._last = digest
                raw = dest.read_text(encoding="utf-8", errors="replace")
                env = parse(raw)
                if not env.body or not getattr(self, "_message_handler", None):
                    continue
                source = self.build_source(
                    chat_id=env.to or "chief",
                    chat_name="Grok Bot",
                    chat_type="group",
                    user_id=env.sender,
                    user_name=env.sender,
                )
                event = MessageEvent(
                    text=env.body,
                    message_type=MessageType.TEXT,
                    source=source,
                    message_id=env.id,
                    timestamp=datetime.now(),
                )
                await self.handle_message(event)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Grok Bot poll")


def check_requirements() -> bool:
    return bool(_home() or _ssh())


def validate_config(config) -> bool:
    extra = getattr(config, "extra", None) or {}
    return bool(_home() or _ssh() or extra.get("home") or extra.get("ssh"))


def _env_enablement():
    if not check_requirements():
        return None
    seed = {}
    if _home():
        seed["home"] = _home()
    if _ssh():
        seed["ssh"] = _ssh()
    rh = os.getenv("GROKBOT_REMOTE_HOME")
    if rh:
        seed["remote_home"] = rh
    seed["home_channel"] = {"chat_id": "chief", "name": "Grok Bot"}
    return seed


def _tool_doctor(_args=None, **_kw):
    from hermes_grokbot.doctor import doctor, format_report

    rows = doctor()
    return json.dumps({"report": format_report(rows), "rows": rows})


def _tool_assign(args=None, **_kw):
    from hermes_grokbot.mailbox import assign

    args = args or {}
    seat = args.get("seat") or "watch"
    body = args.get("body") or ""
    if not body:
        return json.dumps({"error": "body required"})
    home = Path(_home() or "./inbox")
    path = assign(home, seat, body)
    return json.dumps({"ok": True, "seat": seat, "path": str(path)})


def register(ctx):
    ctx.register_platform(
        name="grokbot",
        label="Grok Bot",
        adapter_factory=lambda cfg: GrokBotAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        env_enablement_fn=_env_enablement,
        cron_deliver_env_var="GROKBOT_HOME_CHANNEL",
        install_hint="pip install -e . && hermes-grokbot install-plugin && hermes-grokbot doctor",
        platform_hint=(
            "You are on the Grok Bot merge. First person. "
            "@mention seats (watch, recon, homework). One shared VM. "
            "No secrets in the mailbox. Finish as files. "
            "Use grokbot_doctor before claiming the wire is up."
        ),
        emoji="🖥️",
        max_message_length=8000,
    )
    ctx.register_tool(
        name="grokbot_doctor",
        toolset="grokbot",
        schema={
            "name": "grokbot_doctor",
            "description": "Check Tailscale, SSH, mailbox, and plugin for the Grok Bot merge.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=_tool_doctor,
        description="Doctor the Hermes × Grok Bot merge.",
    )
    ctx.register_tool(
        name="grokbot_assign",
        toolset="grokbot",
        schema={
            "name": "grokbot_assign",
            "description": "Assign one job to a Grok Bot seat (watch, recon, homework, chief).",
            "parameters": {
                "type": "object",
                "properties": {
                    "seat": {"type": "string", "enum": ["chief", "watch", "recon", "homework"]},
                    "body": {"type": "string", "description": "One job. No secrets."},
                },
                "required": ["body"],
            },
        },
        handler=_tool_assign,
        description="Assign a job to a Grok Bot seat.",
    )
