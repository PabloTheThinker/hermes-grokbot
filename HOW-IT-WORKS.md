# How Grok Bot works (and what this repo remakes)

Sourced from @bot / @grok on X and xAI docs (Aug 2026). Not a leak of anyone’s inbox.

## The product

A **Bot** is a named teammate. You give it work. It uses a computer. You can close your laptop. It comes back finished — or asks for approval.

Early jobs @bot named: vendor talk, store support, CRM kept current.
Tiers: SuperGrok Heavy, Cursor Ultra, Cursor Teams Premium.

## The computer

Persistent Linux VM: browser, terminal, files. It *clicks* like a person when there is no clean API.

Marketing often says “each Bot has its own computer.”
**Docs and @grok:** one computer **per account**. Every Bot shares files and browser sessions. Treat the fleet as **one blast radius**, not a vault per seat.

Passwords and 2FA: prefer the human typing on the screen. Keep them off the model.

## How people actually run it

- **Chief of staff** as the only front door. Specialists behind it.
- **Group chat:** @mention, one job, hand the file, stop. Two to six Bots.
- **Routines / skills:** do it twice, save the run. Slack-like triggers.
- **90 → 100%:** land work in the real tool, not a chat draft.
- Still beta. Rough. High skill. Git sync is awkward (Nick Dobos).

## What hermes-grokbot remakes

Hermes Agent has no Grok Bot platform. Grok *inside* Hermes is only a model.

This CLI is the mailbox on that shared computer:

| Path | Job |
|------|-----|
| `FROM-HERMES.txt` | Order from Hermes |
| `TO-HERMES.txt` | Finished work back |
| `seats/watch.md` | Watch public sites — no send |
| `seats/recon.md` | Recon — log, do not mail |
| `seats/homework.md` | One steal from the open web / X, remade |
| `routines/` | Twice → file |
| `approvals/` | Human GO for spend, public, new logins |

`init` creates that. `pull` no-ops when the hash is unchanged.

## What we refuse

Logging the operator into the Bot Chrome.
Sending as the operator.
Pretending separate Bots are a security boundary.
“Runs the company while you sleep.”
