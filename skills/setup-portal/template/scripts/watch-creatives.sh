#!/bin/sh
# Poll-Watcher: indexiert alle 30s neu, wenn sich die Quelle geaendert hat.
cd "$(dirname "$0")/.." || exit 1
while true; do
  python3 scripts/gen-creatives.py --quiet
  sleep 30
done
