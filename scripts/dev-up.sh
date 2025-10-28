#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pushd "$ROOT_DIR/infra" >/dev/null

docker compose up --build --detach

echo "API available at http://localhost:8000"

popd >/dev/null
