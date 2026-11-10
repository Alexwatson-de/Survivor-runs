#!/bin/bash
# Survivor Runs: launch the included optimized game locally. No npm install needed.
set -e
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js 22+ is required. Install Node.js and run this launcher again."
  read -r -p "Press Return to close."; exit 1
fi
# Keep the owner's existing browser origin/local saves; reuse our live host.
if curl --fail --silent --max-time 2 http://127.0.0.1:5190/assets/manifest.json | grep -q '"title": "Survivor Runs"'; then
  open http://127.0.0.1:5190
  exit 0
fi
PORT=5190 node serve-built-game.mjs --open
