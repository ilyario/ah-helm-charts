#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== citadel-monolith: gateway API values =="
helm template test-citadel charts/citadel-monolith \
  -f charts/citadel-monolith/ci/gateway-api-values.yaml \
  --show-only templates/httproute.yaml

echo "== static-proxy: gateway API values =="
helm template test-static charts/static-proxy \
  -f charts/static-proxy/ci/gateway-api-values.yaml \
  --show-only templates/httproute.yaml

echo "OK: Gateway API templates render successfully."
