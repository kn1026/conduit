#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.venv/bin:$PATH"
pytest -q
conduit version
conduit doctor --repo . || true
conduit topo --repo . >/tmp/conduit-topo.json
echo "smoke ok"
