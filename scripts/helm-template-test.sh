#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== citadel-monolith: gateway API values =="
helm template test-citadel charts/citadel-monolith \
  -f charts/citadel-monolith/ci/gateway-api-values.yaml \
  --show-only templates/httproute.yaml

echo "== citadel-monolith: ServiceMonitor + PrometheusRule =="
helm template test-citadel-mon charts/citadel-monolith \
  -f charts/citadel-monolith/ci/monitoring-values.yaml \
  --namespace app-test \
  --show-only templates/servicemonitor.yaml \
  --show-only templates/prometheusrule.yaml \
  --show-only templates/service.yaml

echo "== citadel-monolith: common + per-app merge =="
helm template test-merge charts/citadel-monolith \
  -f charts/citadel-monolith/ci/monitoring-merge-values.yaml \
  --namespace app-test \
  --show-only templates/servicemonitor.yaml

echo "== static-proxy: gateway API values =="
helm template test-static charts/static-proxy \
  -f charts/static-proxy/ci/gateway-api-values.yaml \
  --show-only templates/httproute.yaml

echo "OK: Gateway API templates render successfully."
