# CONNECT — make Hermes see the Grok Bot computer

This is the part most agents skip. **Run `hermes-grokbot doctor` after step 4.** The mailbox CLI does nothing until both machines share a network and SSH (or a synced folder).

Two machines:

| Role | What it is |
|------|------------|
| **Hermes host** | Where Hermes Agent / the gateway runs |
| **Grok Bot computer** | The persistent Linux VM from [x.ai/bot](https://x.ai/bot) (browser, terminal, files) |

They are **not** the same process. Grok-the-model inside Hermes is SuperGrok OAuth. Ignore that here.

## 0. Decide the wire

Pick one:

1. **Same folder** (syncthing, bind mount, shared disk) — skip to step 6.
2. **Tailscale + SSH** — steps 1–6. This is the path that actually works for a cloud Bot box.

Do not use `localhost` on the Hermes host to reach the Bot computer. Wrong machine.

## 1. Tailscale on the Bot computer

On the **Grok Bot computer** (its own terminal):

```bash
# official install — current script from tailscale.com/download
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Completion: `tailscale status` on that box shows itself **online**. Note the MagicDNS name and the `100.x` address. Do not publish those in git.

The human must approve the new machine in the Tailscale admin console if the tailnet requires it.

## 2. Same tailnet as Hermes

On the **Hermes host**:

```bash
tailscale status
# the Bot hostname must appear
tailscale ping -c 2 <bot-hostname>
```

Use `tailscale ping`, not system `ping`. ICMP is often dropped. First packets may go through a DERP relay. That is OK.

If `tailscale status` has **no peer**:

- Wrong tailnet / account
- Device not approved
- **ACL tags hide it** (next step)

Taildrop (`tailscale file cp`) often fails when the two nodes are owned by different Tailscale users (person vs tagged device). Do not depend on Taildrop. Use SSH.

## 3. Tags and ACL (the usual failure)

Hermes host and Bot computer need a grant **Hermes → Bot :22**.

Example policy shape (names are examples — match *your* tailnet):

```json
{
  "tagOwners": {
    "tag:hermes": ["autogroup:admin"],
    "tag:grokbot": ["autogroup:admin"]
  },
  "grants": [
    {
      "src": ["tag:hermes"],
      "dst": ["tag:grokbot"],
      "ip": ["22"]
    }
  ],
  "ssh": [
    {
      "action": "accept",
      "src": ["tag:hermes"],
      "dst": ["tag:grokbot"],
      "users": ["autogroup:nonroot", "root"]
    }
  ]
}
```

Apply in the Tailscale admin ACL editor. Tag the Hermes node `tag:hermes`. Tag the Bot node `tag:grokbot`.

**If you tag the Bot with a tag the Hermes node is not allowed to see, it disappears from `tailscale status`.** That is the ACL working. Fix the grant or use a tag Hermes already dests (many homes already have a `tag:worker` the orchestrator can reach).

Two tags on the Bot are fine (for example worker + something else) as long as **one** of them is in a grant from Hermes.

## 4. SSH from Hermes → Bot

On Hermes:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 USER@BOT_MAGICDNS 'echo OK && hostname && whoami'
```

`BatchMode=yes` is required. Agents must not hang on a password prompt.

If Tailscale SSH answers `tailnet policy does not permit you to SSH as user "X"`, try the users your `ssh` stanza lists (`root` is often the only one that works until you add more).

Completion: you get `OK` and a hostname. Put that in env (do not commit):

```bash
export GROKBOT_SSH=USER@BOT_MAGICDNS
export GROKBOT_REMOTE_HOME=/home/box
```

Grok Bot VMs often use a non-root user named `box` and a home at `/home/box`. Confirm with `ls /home` once you are in. Do not assume.

Install a pubkey if Tailscale SSH is off and plain `sshd` is on. Never paste private keys into chat.

## 5. Name the node (optional, do it on the Bot)

On the Bot, as a user that can run Tailscale:

```bash
sudo hostnamectl set-hostname grokbot   # or any short name
sudo tailscale set --hostname grokbot
```

Wait for MagicDNS. Hermes should then `tailscale ping grokbot`.

## 6. Mailbox

On the **Bot** (or in the shared folder):

```bash
pip install -e /path/to/hermes-grokbot   # or copy the CLI there
hermes-grokbot init --home "$GROKBOT_REMOTE_HOME"
hermes-grokbot status --home "$GROKBOT_REMOTE_HOME"
```

On **Hermes**:

```bash
export GROKBOT_SSH=USER@BOT_MAGICDNS
export GROKBOT_REMOTE_HOME=/home/box
hermes-grokbot drop --body "@watch one public page. File only."
hermes-grokbot pull --dest ./last.txt
# exit 0 new · 1 empty · 2 unchanged
```

Cron the pull on Hermes. Do nothing when exit is 2.

## 7. Speech and jobs

Chief of staff + seats in `seats/`. Group chats: `@name`, one job, stop. No tokens in the body. Approvals folder for spend / public / new logins.

## Agent checklist (do not skip)

0. [ ] `hermes-grokbot doctor` — fix every FAIL before drop
1. [ ] `tailscale ping` from Hermes to Bot succeeds
2. [ ] `ssh -o BatchMode=yes` prints OK
3. [ ] `hermes-grokbot init` + `status` all `ok`
4. [ ] `assign` a line, see `FROM-HERMES.txt` and `outbox/`
5. [ ] Bot runs `scripts/bot-watch.py`, writes ack, pull exit 0 once, then 2
6. [ ] `install-plugin` then restart the **Hermes gateway from a shell** (never from inside a gateway turn)

## Pitfalls

| Symptom | Cause |
|---------|--------|
| Peer missing after you “tagged it” | Tag not in Hermes→Bot grant |
| `ping` fails, `tailscale ping` works | Normal |
| Taildrop “different user” | Use SSH |
| Policy denies user `foo` | ACL `ssh.users` — try listed users only |
| `Connection timed out` to `:22` | Offline, DERP stall, or no grant on 22 |
| Empty world / wrong community | You used `localhost` on the wrong host |

## Security

The Bot computer is one blast radius. Do not copy Hermes secrets, mailbox passwords, or browser cookie DBs onto it. See SECURITY.md.
