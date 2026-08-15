# Architecture — merge, not a drop box

```
Human
  │
  ├─ Telegram / Buzz / CLI     →  Hermes Agent (conductor, memory, skills, seals)
  │
  └─ Grok Bot app              →  Grok Bot computer (always-on VM, named Bots, browser)

         Hermes gateway platform `grokbot`
                    │
         mailbox (FROM-HERMES.txt / TO-HERMES.txt)
         local folder  or  Tailscale SSH
                    │
              Grok Bot computer
```

## Two runtimes, one mission

| | Hermes | Grok Bot |
|--|--------|----------|
| Job | Conductor. Memory. Skills. Mail. Seals. | Always-on computer. Browse. Parallel Bots. |
| Lives | Your host / gateway | xAI/Cursor cloud VM |
| Identity | One agent, many surfaces | Named Bots on **one shared VM** |

Grok **as a model** inside Hermes (SuperGrok OAuth) is the brain in a Hermes turn. That is not this merge.

## How they merge

1. **CONNECT.md** — Tailscale, tags, SSH. Without this, nothing talks.
2. **Mailbox** — orders out, finished work back. `init` / `drop` / `pull`.
3. **Gateway plugin** — `plugins/grokbot/` copies into `$HERMES_HOME/plugins/grokbot`. Hermes treats Grok Bot like Telegram: inbound poll becomes a turn; `send()` writes the mailbox.
4. **Seats** — chief of staff + watch / recon / homework. Group speech: `@name`, one job, stop.
5. **Doctor + enable** — `hermes-grokbot doctor`. `enable-plugin` unions Hermes plugin lists (never replace).
6. **Bot watch** — `scripts/bot-watch.py` on the Grok Bot computer so orders are seen.

## Install the merge

On the Hermes host:

```bash
pip install -e .
hermes-grokbot install-plugin          # copies plugins/grokbot → $HERMES_HOME/plugins/grokbot
# config.yaml:
#   gateway:
#     platforms:
#       grokbot:
#         enabled: true
# env: GROKBOT_SSH=user@bot-host  GROKBOT_REMOTE_HOME=/home/box
# then restart the gateway from a shell (not from inside a gateway turn)
```

On the Bot computer: CONNECT.md + `hermes-grokbot init --home $HOME`.

## Security

One VM = one blast radius. No Hermes secrets, no mailbox passwords, no cookie DBs on the Bot computer.
