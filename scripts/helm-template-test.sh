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

echo "== static-proxy: gateway API values =="
helm template test-static charts/static-proxy \
  -f charts/static-proxy/ci/gateway-api-values.yaml \
  --show-only templates/httproute.yaml

echo "== citadel-monolith: HPA (metrics + behavior) =="
helm template test-citadel-hpa charts/citadel-monolith \
  -f charts/citadel-monolith/ci/hpa-values.yaml \
  --namespace app-test \
  --show-only templates/hpa.yaml \
  --show-only templates/deployment.yaml

echo "== static-proxy: HPA (behavior) =="
helm template test-static-hpa charts/static-proxy \
  -f charts/static-proxy/ci/hpa-values.yaml \
  --show-only templates/hpa.yaml \
  --show-only templates/deployment.yaml

echo "OK: Gateway API and HPA templates render successfully."
