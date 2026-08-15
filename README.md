<p align="center">
  <strong>hermes-grokbot</strong><br>
  Merge <a href="https://hermes-agent.nousresearch.com/">Hermes Agent</a> with a <a href="https://x.ai/bot">Grok Bot</a> computer
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <a href="skills/hermes-grokbot/SKILL.md"><img src="https://img.shields.io/badge/Agent_skill-SKILL.md-111111?style=for-the-badge" alt="Agent skill"></a>
</p>

Two runtimes. One mission. Hermes is the conductor (gateway, memory, skills). Grok Bot is the always-on computer (named teammates, browser). This repo is the merge — not a toy file drop.

**If you are an agent:** do this in order. Do not skip `doctor`.

```bash
git clone https://github.com/PabloTheThinker/hermes-grokbot.git
cd hermes-grokbot
pip install -e .

# 1) wire the two machines (Tailscale + SSH). Read CONNECT.md.
export GROKBOT_SSH=user@bot-magicdns
export GROKBOT_REMOTE_HOME=/home/box   # confirm with ls /home

# 2) prove the wire
hermes-grokbot doctor

# 3) mailbox + Hermes plugin (does not restart the gateway)
hermes-grokbot init --home ./inbox
hermes-grokbot install-plugin
# hermes-grokbot enable-plugin   # merges config.yaml; restart gateway FROM A SHELL

# 4) one job
hermes-grokbot assign --seat watch --body "Three public shop sites. File only."
```

On the **Bot computer**, after the same `pip install -e .`:

```bash
hermes-grokbot init --home "$HOME"
python3 scripts/bot-watch.py --home "$HOME"
# when work is finished:
python3 scripts/bot-watch.py --home "$HOME" --ack "watch done. notes in seats/watch.md"
```

Then read [CONNECT.md](CONNECT.md), [ARCHITECTURE.md](ARCHITECTURE.md), [HOW-IT-WORKS.md](HOW-IT-WORKS.md).

<table>
<tr><td><b>Merge</b></td><td>Gateway platform <code>grokbot</code> + tools <code>grokbot_doctor</code> / <code>grokbot_assign</code></td></tr>
<tr><td><b>Envelope</b></td><td><code>---hgb-1</code> from/to/kind so seats do not clobber each other</td></tr>
<tr><td><b>Doctor</b></td><td>Tailscale ping, SSH BatchMode, mailbox, plugin</td></tr>
<tr><td><b>Enable</b></td><td>Unions <code>plugins.enabled</code> — never replaces the list</td></tr>
</table>

## What this is not

- Grok Build CLI, or SuperGrok-as-model inside a Hermes turn
- A vault per Bot (one computer per account)
- A place for passwords, OAuth, or browser cookies

## Named agents

Kits in [`agents/`](agents/). Chief + Watch + Recon + Homework. `./agents/install.sh` then `hermes-grokbot assign`.

## License

MIT. Pablo Navarro.
