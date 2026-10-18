#!/usr/bin/env bash
# Validates that citadel-monolith renders metadata.name without dots (DNS-1035).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v helm >/dev/null 2>&1; then
  echo "helm not found in PATH" >&2
  exit 1
fi

run_case() {
  local rel="$1"
  local values="$2"
  local expected="$3"
  local out
  out="$(helm template "$rel" "$ROOT" -f "$values" 2>&1)" || {
    echo "$out" >&2
    return 1
  }
  echo "$out" | grep -q 'kind: Service' || {
    echo "No Service in output for $values" >&2
    echo "$out" >&2
    return 1
  }
  echo "$out" | grep -F "name: ${expected}" >/dev/null || {
    echo "Expected Service name '${expected}' not found (release=${rel}, values=${values})" >&2
    echo "$out" >&2
    return 1
  }
  # Lines that look like top-level metadata name under two-space indent must not contain a dot.
  if echo "$out" | awk '/^  name: / { print }' | grep -E '\.'; then
    echo "Found a top-level '  name:' line containing a dot" >&2
    return 1
  fi
}

run_case "testrel" "$ROOT/ci/dns-label-values.yaml" "my-site-ru-app-v1"
run_case "rel.example.ru" "$ROOT/ci/dns-label-release-values.yaml" "rel-example-ru-citadel-core"

echo "OK: dns-label helm template checks passed"
