# Security

## Threat model

A Grok Bot computer is a shared VM. Every Bot on the account can see the same files and browser sessions. Treat that box as one blast radius.

This package does **not** collect personal data. It does not phone home. It does not read mail, browser cookies, SSH private keys, or Hermes memory files.

Hermes Agent must not put mailbox passwords, OAuth tokens, or personal identity files on that VM.

## Rules this package enforces

- File names allowlisted (`FROM-HERMES.txt`, `TO-HERMES.txt`)
- No `..` path escape
- Body size cap
- SSH is BatchMode only; target must look like `user@host`
- `doctor` reports ok/fail only — it does not print IPs or ping payloads
- `enable-plugin` only unions plugin lists on the machine that runs it

## Rules you must keep

- Do not copy Hermes `$HOME` secrets onto the Grok Bot computer
- Do not put names, addresses, mailboxes, or money in the mailbox body
- Bind any webhook you add later to loopback until you have a real ACL
- Do not log message bodies that might contain secrets

`scripts/security_audit.sh` fails if the tree looks like an operator dump.
