#!/usr/bin/env bash
# Copy named-agent kits into seats/ on the Bot computer.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
dest="${GROKBOT_HOME:-./inbox}/seats"
mkdir -p "$dest"

for seat in chief watch recon homework; do
  cp "$here/${seat}.md" "$dest/${seat}.md"
  echo "minted $dest/${seat}.md"
done

echo
echo "next:"
echo "  hermes-grokbot assign --seat watch --body \"Three public shop sites. File only.\""
echo "  hermes-grokbot assign --seat recon --body \"Three businesses. Log. Do not mail.\""
echo "  hermes-grokbot assign --seat homework --body \"One steal from the open web. Remade.\""
echo "  hermes-grokbot assign --seat chief --body \"Hand one job. File only.\""
