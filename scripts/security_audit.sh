#!/usr/bin/env bash
# Fail if the tree looks like an operator dump.
# Keep this file free of real hostnames, IPs, and home users.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
fail=0

# Any /home/<user>/ except the public Grok Bot example user "box"
if git grep -n -I -E '/home/[A-Za-z0-9._-]+/' -- ':!scripts/security_audit.sh' \
  | grep -v '/home/box' >/dev/null 2>&1; then
  echo FAIL home-path
  fail=1
fi

# Concrete 100.x.y.z (docs may say "100.x")
if git grep -n -I -E '100\.[0-9]+\.[0-9]+\.[0-9]+' -- ':!scripts/security_audit.sh' >/dev/null 2>&1; then
  echo FAIL mesh-ip
  fail=1
fi

# MagicDNS hosts
if git grep -n -I -E '[A-Za-z0-9-]+\.ts\.net' -- ':!scripts/security_audit.sh' >/dev/null 2>&1; then
  echo FAIL magicdns
  fail=1
fi

# Credential shapes
if git grep -n -I -E 'BEGIN (OPENSSH|RSA) PRIVATE KEY' -- ':!scripts/security_audit.sh' >/dev/null 2>&1; then
  echo FAIL key-shape
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo OK
