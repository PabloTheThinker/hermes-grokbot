---
name: hermes-grokbot
description: "Merge Hermes Agent with a Grok Bot computer."
version: 0.5.0
author: Pablo Navarro, Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [hermes, grok-bot, merge]
---

# Hermes × Grok Bot

Hermes has no Grok Bot platform in core. This repo **is** the merge: mailbox + gateway adapter + doctor. Grok-as-model (SuperGrok OAuth) is not this.

## When to Use

- User wants Hermes merged with a Grok Bot computer
- Long watch / browse that should not live in a chat turn

Do not use for Proton mail, Grok Build CLI, or inventing a second conductor.

## Prerequisites

- `hermes-grokbot` on PATH (`pip install -e .`)
- Env: `GROKBOT_HOME` and/or `GROKBOT_SSH` + `GROKBOT_REMOTE_HOME`
- CONNECT.md completed (Tailscale, tags, SSH)

## Procedure

1. `hermes-grokbot doctor` — every FAIL is blocking
2. Follow CONNECT.md then ARCHITECTURE.md
3. `hermes-grokbot install-plugin`
4. `hermes-grokbot assign --seat watch --body "..."` — no tokens
5. On the Bot: `python3 scripts/bot-watch.py --home "$GROKBOT_REMOTE_HOME"`
6. `hermes-grokbot pull --dest ./last.txt` — 1 nothing, 2 unchanged
7. Bot groups: first person, @mention, one job, stop
8. Restart the Hermes gateway **from a shell**, never from inside a turn, after enable-plugin

## Verification

`python3 -m unittest discover -s tests -q`. `bash scripts/security_audit.sh` prints OK. `doctor` has no FAIL on ssh/tailscale when remote.

## Pitfalls

- Marketing says each Bot has its own computer; docs say one VM per account
- SSH without BatchMode hangs
- `enable-plugin` must union `plugins.enabled` — never replace the list
- Do not restart the gateway from inside a gateway session
