#!/usr/bin/env python3
"""Generate citadel SRE Grafana dashboard JSON (Grafana 9+)."""
import json
import os
import sys

ds_var = "${datasource}"
ds_ref = {"type": "prometheus", "uid": ds_var}


def timeseries(
    id_,
    title,
    exprs,
    unit="",
    h=8,
    w=12,
    x=0,
    y=0,
):
    targets = []
    for i, (legend, expr) in enumerate(exprs):
        ref = chr(65 + i) if i < 26 else str(i)
        targets.append(
            {
                "datasource": ds_ref,
                "editorMode": "code",
                "expr": expr,
                "legendFormat": legend,
                "range": True,
                "refId": ref,
            }
        )
    return {
        "datasource": ds_ref,
        "fieldConfig": {
            "defaults": {
                "color": {"mode": "palette-classic"},
                "custom": {
                    "axisBorderShow": False,
                    "axisCenteredZero": False,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "drawStyle": "line",
                    "fillOpacity": 10,
                    "gradientMode": "none",
                    "hideFrom": {"legend": False, "tooltip": False, "viz": False},
                    "insertNulls": False,
                    "lineInterpolation": "smooth",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {"type": "linear"},
                    "showPoints": "never",
                    "spanNulls": False,
                    "stacking": {"group": "A", "mode": "none"},
                    "thresholdsStyle": {"mode": "off"},
                },
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [{"color": "green", "value": None}, {"color": "red", "value": 80}],
                },
                "unit": unit,
            },
            "overrides": [],
        },
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "id": id_,
        "options": {
            "legend": {
                "calcs": ["mean", "max", "lastNotNull"],
                "displayMode": "table",
                "placement": "bottom",
                "showLegend": True,
            },
            "tooltip": {"mode": "multi", "sort": "desc"},
        },
        "pluginVersion": "10.0.0",
        "targets": targets,
        "title": title,
        "type": "timeseries",
    }


def row(id_, title, y):
    return {
        "collapsed": False,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
        "id": id_,
        "panels": [],
        "title": title,
        "type": "row",
    }


def main():
    ing_ns = "$ingress_controller_namespace"
    panels = []
    y = 0
    pid = 1

    panels.append(row(100, "Ingress / API Gateway (nginx ingress controller)", y))
    y += 1

    panels.append(
        timeseries(
            pid,
            "RPS по host (ingress)",
            [
                (
                    "{{host}}",
                    f'sum by (host) (rate(nginx_ingress_controller_requests{{namespace=~"{ing_ns}"}}[5m]))',
                ),
            ],
            unit="reqps",
            y=y,
            x=0,
        )
    )
    pid += 1
    panels.append(
        timeseries(
            pid,
            "RPS по ingress и по service (upstream)",
            [
                (
                    "{{ingress}}",
                    f'sum by (ingress) (rate(nginx_ingress_controller_requests{{namespace=~"{ing_ns}"}}[5m]))',
                ),
                (
                    "{{service}}",
                    f'sum by (service) (rate(nginx_ingress_controller_requests{{namespace=~"{ing_ns}"}}[5m]))',
                ),
            ],
            unit="reqps",
            y=y,
            x=12,
        )
    )
    pid += 1
    y += 8

    panels.append(
        timeseries(
            pid,
            "Latency ingress — p50 / p95 / p99",
            [
                (
                    "p50",
                    f'histogram_quantile(0.50, sum(rate(nginx_ingress_controller_request_duration_seconds_bucket{{namespace=~"{ing_ns}"}}[5m])) by (le))',
                ),
                (
                    "p95",
                    f'histogram_quantile(0.95, sum(rate(nginx_ingress_controller_request_duration_seconds_bucket{{namespace=~"{ing_ns}"}}[5m])) by (le))',
                ),
                (
                    "p99",
                    f'histogram_quantile(0.99, sum(rate(nginx_ingress_controller_request_duration_seconds_bucket{{namespace=~"{ing_ns}"}}[5m])) by (le))',
                ),
            ],
            unit="s",
            y=y,
            x=0,
        )
    )
    pid += 1
    panels.append(
        timeseries(
            pid,
            "HTTP 4xx / 5xx (ingress)",
            [
                (
                    "4xx",
                    f'sum(rate(nginx_ingress_controller_requests{{namespace=~"{ing_ns}",status=~"4.."}}[5m]))',
                ),
                (
                    "5xx",
                    f'sum(rate(nginx_ingress_controller_requests{{namespace=~"{ing_ns}",status=~"5.."}}[5m]))',
                ),
            ],
            unit="reqps",
            y=y,
            x=12,
        )
    )
    pid += 1
    y += 8

    panels.append(row(101, "Приложение (namespace релиза)", y))
    y += 1

    panels.append(
        timeseries(
            pid,
            "RPS по job (http_requests_total / http_server)",
            [
                (
                    "http_requests_total",
                    'sum by (job) (rate(http_requests_total{namespace="$namespace"}[5m]))',
                ),
                (
                    "http_server_requests_total",
                    'sum by (job) (rate(http_server_requests_total{namespace="$namespace"}[5m]))',
                ),
            ],
            unit="reqps",
            y=y,
            x=0,
        )
    )
    pid += 1
    panels.append(
        timeseries(
            pid,
            "Latency приложения p95 (histogram)",
            [
                (
                    "http_request_duration_seconds",
                    'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{namespace="$namespace"}[5m])) by (le, job))',
                ),
                (
                    "http_server_duration_seconds",
                    'histogram_quantile(0.95, sum(rate(http_server_duration_seconds_bucket{namespace="$namespace"}[5m])) by (le, job))',
                ),
            ],
            unit="s",
            y=y,
            x=12,
        )
    )
    pid += 1
    y += 8

    panels.append(
        timeseries(
            pid,
            "4xx / 5xx приложение (http_requests_total)",
            [
                (
                    "5xx",
                    'sum(rate(http_requests_total{namespace="$namespace",status=~"5.."}[5m]))',
                ),
                (
                    "4xx",
                    'sum(rate(http_requests_total{namespace="$namespace",status=~"4.."}[5m]))',
                ),
            ],
            unit="reqps",
            w=24,
            y=y,
            x=0,
        )
    )
    pid += 1
    y += 8

    panels.append(row(102, "Kubernetes: поды, ресурсы, джобы", y))
    y += 1

    panels.append(
        timeseries(
            pid,
            "Рестарты контейнеров по pod",
            [
                (
                    "{{pod}}",
                    'sum by (pod) (kube_pod_container_status_restarts_total{namespace="$namespace"})',
                ),
            ],
            unit="short",
            y=y,
            x=0,
        )
    )
    pid += 1
    panels.append(
        timeseries(
            pid,
            "CPU throttling (container_cpu_cfs_throttled)",
            [
                (
                    "{{pod}}",
                    'sum by (pod) (rate(container_cpu_cfs_throttled_seconds_total{namespace="$namespace", container!=""}[5m]))',
                ),
            ],
            unit="s/s",
            y=y,
            x=12,
        )
    )
    pid += 1
    y += 8

    panels.append(
        timeseries(
            pid,
            "CPU: usage vs requests (cores)",
            [
                (
                    "usage",
                    'sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="$namespace", container!="POD", container!=""}[5m]))',
                ),
                (
                    "requests",
                    'sum by (pod) (kube_pod_container_resource_requests{namespace="$namespace", resource="cpu", container!="POD", container!=""})',
                ),
            ],
            unit="short",
            y=y,
            x=0,
        )
    )
    pid += 1
    panels.append(
        timeseries(
            pid,
            "Memory: working set vs limit",
            [
                (
                    "workingset",
                    'sum by (pod) (container_memory_working_set_bytes{namespace="$namespace", container!="POD", container!=""})',
                ),
                (
                    "limit",
                    'sum by (pod) (kube_pod_container_resource_limits{namespace="$namespace", resource="memory", container!="POD", container!=""})',
                ),
            ],
            unit="bytes",
            y=y,
            x=12,
        )
    )
    pid += 1
    y += 8

    panels.append(
        timeseries(
            pid,
            "Доля requests от limits (CPU и memory, сумма по namespace)",
            [
                (
                    "cpu",
                    'clamp_max(sum(kube_pod_container_resource_requests{namespace="$namespace",resource="cpu"}) / sum(kube_pod_container_resource_limits{namespace="$namespace",resource="cpu"}), 1)',
                ),
                (
                    "memory",
                    'clamp_max(sum(kube_pod_container_resource_requests{namespace="$namespace",resource="memory"}) / sum(kube_pod_container_resource_limits{namespace="$namespace",resource="memory"}), 1)',
                ),
            ],
            unit="percentunit",
            h=7,
            w=12,
            y=y,
            x=0,
        )
    )
    pid += 1
    panels.append(
        timeseries(
            pid,
            "Фазы подов (Pod phase)",
            [
                (
                    "Pending",
                    'sum(kube_pod_status_phase{namespace="$namespace",phase="Pending"})',
                ),
                (
                    "Running",
                    'sum(kube_pod_status_phase{namespace="$namespace",phase="Running"})',
                ),
                (
                    "Failed",
                    'sum(kube_pod_status_phase{namespace="$namespace",phase="Failed"})',
                ),
                (
                    "Succeeded",
                    'sum(kube_pod_status_phase{namespace="$namespace",phase="Succeeded"})',
                ),
            ],
            unit="short",
            h=7,
            w=12,
            y=y,
            x=12,
        )
    )
    pid += 1
    y += 7

    panels.append(
        timeseries(
            pid,
            "Ready condition (не готовы)",
            [
                (
                    "NotReady count",
                    'sum(kube_pod_status_condition{namespace="$namespace",condition="Ready",status="false"})',
                ),
            ],
            unit="short",
            h=7,
            w=12,
            y=y,
            x=0,
        )
    )
    pid += 1
    panels.append(
        timeseries(
            pid,
            "Jobs: failed / active / succeeded",
            [
                ("failed", 'sum(kube_job_status_failed{namespace="$namespace"})'),
                ("active", 'sum(kube_job_status_active{namespace="$namespace"})'),
                (
                    "succeeded",
                    'sum(kube_job_status_succeeded{namespace="$namespace"})',
                ),
            ],
            unit="short",
            h=7,
            w=12,
            y=y,
            x=12,
        )
    )
    pid += 1
    y += 7

    panels.append(
        {
            "datasource": ds_ref,
            "fieldConfig": {
                "defaults": {
                    "custom": {
                        "align": "auto",
                        "cellOptions": {"type": "auto"},
                        "inspect": False,
                    },
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [{"color": "green", "value": None}],
                    },
                },
                "overrides": [],
            },
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": y},
            "id": pid,
            "options": {
                "cellHeight": "sm",
                "footer": {
                    "countRows": False,
                    "fields": "",
                    "reducer": ["sum"],
                    "show": False,
                },
                "showHeader": True,
            },
            "pluginVersion": "10.0.0",
            "targets": [
                {
                    "datasource": ds_ref,
                    "editorMode": "code",
                    "exemplar": False,
                    "expr": 'kube_cronjob_info{namespace="$namespace"}',
                    "format": "table",
                    "instant": True,
                    "legendFormat": "__auto",
                    "refId": "A",
                }
            ],
            "title": "CronJobs (kube_cronjob_info)",
            "transformations": [
                {
                    "id": "organize",
                    "options": {
                        "excludeByName": {"Time": True, "Value": True},
                        "indexByName": {},
                        "renameByName": {"cronjob": "CronJob"},
                    },
                }
            ],
            "type": "table",
        }
    )
    pid += 1
    y += 8

    panels.append(
        {
            "datasource": ds_ref,
            "gridPos": {"h": 5, "w": 24, "x": 0, "y": y},
            "id": 999,
            "options": {
                "content": (
                    "**SRE-дашборд Citadel (Helm).** Ingress: метрики `nginx_ingress_controller_*` "
                    "(ingress-nginx). При другом ingress замените запросы. Приложение: типичные метрики "
                    "Prometheus/OpenTelemetry. Кластер: kube-state-metrics + cAdvisor. SLI по доступности: "
                    "правило `up` для ServiceMonitor (PrometheusRule в чарте)."
                ),
                "mode": "markdown",
            },
            "pluginVersion": "10.0.0",
            "title": "Примечания",
            "type": "text",
        }
    )

    dashboard = {
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": {"type": "grafana", "uid": "-- Grafana --"},
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard",
                }
            ]
        },
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 1,
        "links": [],
        "liveNow": False,
        "panels": panels,
        "refresh": "30s",
        "schemaVersion": 39,
        "tags": ["citadel", "kubernetes", "sre"],
        "templating": {
            "list": [
                {
                    "current": {"selected": False, "text": "Prometheus", "value": "Prometheus"},
                    "hide": 0,
                    "includeAll": False,
                    "label": "Datasource",
                    "name": "datasource",
                    "options": [],
                    "query": "prometheus",
                    "refresh": 1,
                    "regex": "",
                    "type": "datasource",
                },
                {
                    "allValue": ".*",
                    "current": {"selected": False, "text": "", "value": ""},
                    "datasource": ds_ref,
                    "definition": "label_values(kube_pod_info, namespace)",
                    "hide": 0,
                    "includeAll": False,
                    "label": "Namespace",
                    "name": "namespace",
                    "query": {
                        "query": "label_values(kube_pod_info, namespace)",
                        "refId": "PrometheusVariableQueryEditor-VariableQuery",
                    },
                    "refresh": 1,
                    "regex": "",
                    "sort": 1,
                    "type": "query",
                },
                {
                    "current": {
                        "selected": True,
                        "text": "ingress-nginx",
                        "value": "ingress-nginx",
                    },
                    "hide": 0,
                    "label": "Ingress controller NS",
                    "name": "ingress_controller_namespace",
                    "query": "ingress-nginx",
                    "skipUrlSync": False,
                    "type": "textbox",
                },
            ]
        },
        "time": {"from": "now-1h", "to": "now"},
        "timezone": "browser",
        "title": "Citadel — SRE dashboard",
        "uid": "citadel-sre-release",
        "version": 1,
    }

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(
        root,
        "charts/citadel-monolith/files/grafana-dashboards/citadel-sre.json",
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)
    print(out, file=sys.stderr)


if __name__ == "__main__":
    main()
