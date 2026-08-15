# Named agents

One Grok Bot computer per account. A seat is a file in `seats/`. Not a vault.

Hermes conducts. The Bot computer stays on. Finish is a file. No send. No spend. No new logins.

## Mint a seat

Copy the four kits onto the computer:

```bash
bash agents/install.sh
```

That writes `chief.md`, `watch.md`, `recon.md`, and `homework.md` into `$GROKBOT_HOME/seats/` (or `./inbox/seats/` if `GROKBOT_HOME` is unset).

Then give one job:

```bash
hermes-grokbot assign --seat watch --body "Three public shop sites. File only."
```

The seat reads its file. Does the job. Writes a file. Stops.

Speech: first person, @mention, one job, stop.

## Seats

| File | Job |
|------|-----|
| `chief.md` | Front door. Hands one job to one seat. |
| `watch.md` | Watch public sites. Draft only. |
| `recon.md` | Three businesses. Log. Do not mail. |
| `homework.md` | One steal from the open web. Remade. |
