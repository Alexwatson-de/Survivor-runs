#!/bin/bash
# Runs the included optimized game locally, without npm install or Internet access.
set -e
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js 22+ is required. Install Node.js, then run this launcher again."
  read -r -p "Press Return to close."; exit 1
fi
node serve-built-game.mjs --open
