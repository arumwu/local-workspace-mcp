#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ "$#" -eq 0 ]; then
  echo 'Run: ./Install.command --workspace /absolute/workspace --state /absolute/private-state --mode full'
  echo 'Full mode grants user-account access. Use --mode documents for Docker-isolated document jobs.'
  exit 0
fi
exec python3 scripts/install.py "$@"
