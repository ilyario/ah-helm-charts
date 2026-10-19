![Version: 0.2.9](https://img.shields.io/badge/Version-0.2.9-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.0.0](https://img.shields.io/badge/AppVersion-1.0.0-informational?style=flat-square)

A Helm chart for deploying monolithic applications in Kubernetes clusters.

## Description

This Helm chart is designed for deploying monolithic applications with support for:
- Multiple applications in a single release, each with its own Service, probes and autoscaling
- Infisical integration for secret management
- Automatic scaling (HPA) with autoscaling/v2 metrics and behavior
- Ingress configuration and/or Gateway API HTTPRoute
- Jobs for migrations and other tasks
- CronJobs with timeZone, concurrency policy and history limits
- Shared PVCs and Secrets mounted into all application pods
- Pod topology spread constraints
- Startup, liveness and readiness probes
- Prometheus ServiceMonitor and PrometheusRule for metrics collection and alerts
- Explicit Deployment update strategies per application (`recreate` / `rollingUpdate`)

> Note: the chart name is `citadel` (the directory is `citadel-monolith`), so the
> published package is `citadel-<version>.tgz`.

## Requirements

- Kubernetes 1.23+ (enforced via `kubeVersion: ">=1.23.0-0"`)
- Helm 3.0+ (Helm 4 works as well)
- Optional: an ingress controller (e.g. ingress-nginx), Gateway API CRDs and a Gateway, the Prometheus Operator (for `ServiceMonitor`/`PrometheusRule`), Infisical Operator (for secret sync)

## Installation

### Adding the repository

```bash
helm repo add ah-helm https://ilyario.github.io/ah-helm-charts
helm repo update
```

### Installing the chart

```bash
# Basic installation
helm install my-citadel ah-helm/citadel

# Installation with custom values
helm install my-citadel ah-helm/citadel -f values.yaml

# Installation in a specific namespace
helm install my-citadel ah-helm/citadel --namespace my-namespace --create-namespace

# Or straight from a git checkout of this repository
helm install my-citadel ./charts/citadel-monolith -f my-values.yaml
```

> The container image repository and tag are mandatory for every application, job
> and cronjob: the chart fails rendering early when the effective image tag is
> empty, instead of accidentally deploying `repository:`.

## Configuration

### Application configuration

The chart supports deploying multiple applications. Each application can have:

```yaml
applications:
  - name: nginx
    replicaCount: 1
    # recreate | rollingUpdate (omit for Kubernetes default RollingUpdate)
    updateStrategy: rollingUpdate
    # rollingUpdate:
    #   maxUnavailable: 0
    #   maxSurge: 1
    image:
      repository: nginx
      tag: "1.29"
    service:
      type: ClusterIP
      port: 80
    ingress:
      enabled: true
      hosts:
        - host: example.com
          paths:
            - path: /
              pathType: ImplementationSpecific
    resources:
      limits:
        cpu: 100m
        memory: 128Mi
      requests:
        cpu: 100m
        memory: 128Mi
```

### Infisical integration

For secret management through Infisical:

```yaml
common:
  infisical:
    enabled: true
    url: http://infisical-standalone-infisical.infisical.svc.cluster.local:8080/api
    resyncInterval: 10
    commonSecret:
      enabled: true
      projectSlug: "your-project"
      secretsPath: /
      credentialsRef:
        secretName: client-infisical-secrets
```

### Jobs and CronJobs

One-off Jobs (e.g. migrations) are defined at the top level:

```yaml
jobs:
  - name: migration
    enabled: true
    command: ["python"]
    args: ["manage.py", "migrate"]
    image:
      repository: your-app
      tag: "latest"
    resources:
      limits:
        cpu: 100m
        memory: 128Mi
      requests:
        cpu: 100m
        memory: 128Mi
```

CronJobs support schedules with time zones, concurrency policy, history limits and pod-level security configuration:

```yaml
cronjobs:
  - name: backup
    enabled: true
    schedule: "0 2 * * *"
    timeZone: "UTC"
    concurrencyPolicy: Forbid
    successfulJobsHistoryLimit: 3
    failedJobsHistoryLimit: 1
    command: ["python"]
    args: ["manage.py", "backup"]
    image:
      repository: your-app
      tag: "1.0"
```

### Gateway API (HTTPRoute)

Applications can be exposed through Gateway API in addition to (or instead of) Ingress. `parentRefs` defaults to `common.gatewayApi.parentRefs` and can be overridden per application:

```yaml
common:
  gatewayApi:
    parentRefs:
      - name: my-gateway
        namespace: istio-system

applications:
  - name: web
    service: { type: ClusterIP, port: 8000 }
    gatewayApi:
      enabled: true
      hosts:
        - host: myapp.example.com
          paths:
            - path: /
              pathType: PathPrefix
```

### Shared PVCs, secrets and env

Volumes and secrets declared under `common` are mounted into every application pod:

```yaml
common:
  sharedPVCs:
    - name: static
      mountPath: /static
      storageClass: csi-s3
      size: 10Gi
      accessModes:
        - ReadWriteMany
      # Optional. Merged onto the PVC. `helm.sh/resource-policy: keep` is set
      # unless the same key is overridden here.
      annotations: {}
  sharedSecrets:
    - my-secret-name
  env:
    - name: TZ
      value: Asia/Irkutsk
```

A claim created by a chart version that rendered `helm.sh/hook: pre-install` is not part of the release manifest. After that hook was removed, `helm upgrade` tries to create the same PVC as a regular resource and fails because it already exists. Put the previous hook annotations on that item so Helm keeps treating it as a hook:

```yaml
common:
  sharedPVCs:
    - name: static
      annotations:
        helm.sh/hook: pre-install
        helm.sh/hook-weight: "-5"
```

Leave `helm.sh/hook` unset on new claims. A `pre-install` hook is not created on `helm upgrade`.

### Topology spread constraints

`common.topologySpreadConstraints` applies cluster-wide spreading to all application pods. The `labelSelector.matchLabels.component` value is templated per application, so applications only spread their own pods:

```yaml
common:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: ScheduleAnyway
      labelSelector:
        matchLabels:
          component: ""  # substituted with the application dns-safe name
```

### Service account and private registries

```yaml
serviceAccount:
  create: true
  name: my-app-sa

imagePullSecrets:
  - name: regcred
```

## Usage

### Updating the release

```bash
helm upgrade my-citadel ah-helm/citadel -f values.yaml
```

### Uninstalling the release

```bash
helm uninstall my-citadel
```

### Checking status

```bash
helm status my-citadel
```

### Getting values

```bash
helm get values my-citadel
```

## Monitoring

### Prometheus ServiceMonitor

The chart supports Prometheus monitoring through `ServiceMonitor` resources. Configure `serviceMonitor` under each application:

```yaml
applications:
  - name: web
    service:
      type: ClusterIP
      port: 8000
    serviceMonitor:
      enabled: true
      interval: 30s
      scrapeTimeout: 10s
      path: /metrics
      # Must match the port name on the Service (default: http-<app name>, e.g. http-web)
      portName: http-web
      labels:
        release: prometheus
      annotations: {}

  - name: api
    service:
      type: ClusterIP
      port: 9000
    serviceMonitor:
      enabled: true
      interval: 15s
      scrapeTimeout: 5s
      path: /api/metrics
      portName: http-api
      labels:
        release: prometheus
        app: api
```

### Alertmanager: PrometheusRule

The chart can render a `PrometheusRule` (consumed by Prometheus Operator and evaluated by Alertmanager) per application. When `prometheusRule.enabled` is `true`, a default alert **KubeHttpTargetDown** is included unless you disable it under `defaultRules.targetDown.enabled`. It fires when the `up` series for the application Service is 0. You can add more rule groups with `additionalGroups` (full YAML for `spec.groups` entries).

```yaml
applications:
  - name: web
    service: { type: ClusterIP, port: 8000 }
    serviceMonitor:
      enabled: true
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
      portName: http-web
      labels: { release: prometheus }
    prometheusRule:
      enabled: true
      labels: { release: prometheus }
      defaultRules:
        targetDown:
          for: 5m
          severity: critical
      additionalGroups: []
```

### Health Checks

The chart supports three types of health checks:

1. **Startup Probe**: Used to determine if the application has successfully started
2. **Liveness Probe**: Used to determine if the application is alive
3. **Readiness Probe**: Used to determine if the application is ready to serve traffic

Example configuration:

```yaml
applications:
  - name: web
    startupProbe:
      httpGet:
        path: /health
        port: http
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 30
    livenessProbe:
      httpGet:
        path: /health
        port: http
    readinessProbe:
      httpGet:
        path: /ready
        port: http
```

### Grafana Integration

After installing the chart, you will have access to:

1. **Application logs** (if Grafana is configured):
   ```
   https://grafana.{domain}/explore?schemaVersion=1&panes=%7B%22a5k%22:%7B%22datasource%22:%22P8E80F9AEF21F6940%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22%7Bnamespace%3D%5C%22{namespace}%5C%22%7D%20%7C%3D%20%60%60%22,%22queryType%22:%22range%22,%22datasource%22:%7B%22type%22:%22loki%22,%22uid%22:%22P8E80F9AEF21F6940%22%7D,%22editorMode%22:%22builder%22,%22direction%22:%22backward%22%7D%5D,%22range%22:%7B%22from%22:%22now-1h%22,%22to%22:%22now%22%7D,%22panelsState%22:%7B%22logs%22:%7B%22visualisationType%22:%22logs%22%7D%7D%7D%7D&orgId=1
   ```

2. **Resource consumption metrics**:
   ```
   https://grafana.{domain}/d/k8s_views_ns/kubernetes-views-namespaces?orgId=1&from=now-1h&to=now&timezone=browser&var-datasource=prometheus&var-cluster=&var-namespace={namespace}&var-resolution=30s&var-created_by=$__all&refresh=30s
   ```

## Example values.yaml

```yaml
# Main settings
nameOverride: ""
fullnameOverride: ""

# Common settings
common:
  environment: production
  grafana: "grafana.example.com"
  env:
    - name: TZ
      value: Asia/Irkutsk

# Infisical integration
common:
  infisical:
    enabled: true
    url: http://infisical-standalone-infisical.infisical.svc.cluster.local:8080/api
    resyncInterval: 10
    commonSecret:
      enabled: true
      projectSlug: "my-project"
      secretsPath: /
      credentialsRef:
        secretName: client-infisical-secrets

# Jobs for migrations
jobs:
  - name: migration
    enabled: true
    command: ["python"]
    args: ["manage.py", "migrate"]
    image:
      repository: my-app
      tag: "latest"

# Applications
applications:
  - name: web
    replicaCount: 3
    image:
      repository: my-web-app
      tag: "latest"
    service:
      type: ClusterIP
      port: 8000
    ingress:
      enabled: true
      hosts:
        - host: myapp.example.com
          paths:
            - path: /
              pathType: ImplementationSpecific
    resources:
      limits:
        cpu: 500m
        memory: 512Mi
      requests:
        cpu: 250m
        memory: 256Mi
    startupProbe:
      httpGet:
        path: /health
        port: http-web
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 30
    livenessProbe:
      httpGet:
        path: /health
        port: http-web
    readinessProbe:
      httpGet:
        path: /ready
        port: http-web
    serviceMonitor:
      enabled: true
      interval: 30s
      scrapeTimeout: 10s
      path: /metrics
      portName: http-web
      labels:
        release: prometheus
```

## Troubleshooting

If you encounter issues:

1. Check pod status: `kubectl get pods -n <namespace>`
2. View logs: `kubectl logs <pod-name> -n <namespace>`
3. Check events: `kubectl get events -n <namespace>`
4. Verify values.yaml configuration is correct

## License

This project is licensed under MIT.

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| applications | list | `[]` | Long-running applications: each gets Deployment, Service and optional Ingress/HTTPRoute, HPA and monitoring |
| common | object | `{"affinity":{},"env":[],"environment":"dev","gatewayApi":{"parentRefs":[]},"grafana":{"dashboard":{"annotations":{},"enabled":false,"labels":{"grafana_dashboard":"1"},"name":""}},"image":{"pullPolicy":"IfNotPresent","repository":"nginx","tag":""},"imagePullSecrets":[],"infisical":{"commonSecret":{"credentialsRef":{"secretName":"client-infisical-secrets"},"enabled":false,"projectSlug":"","secretsPath":"/"},"enabled":false,"resyncInterval":10,"url":"http://infisical-standalone-infisical.infisical.svc.cluster.local:8080/api"},"ingress":{"className":"nginx"},"nodeSelector":{},"sharedPVCs":[],"sharedSecrets":[],"tolerations":[],"topologySpreadConstraints":[{"labelSelector":{"matchLabels":{"component":""}},"maxSkew":1,"topologyKey":"topology.kubernetes.io/zone","whenUnsatisfiable":"ScheduleAnyway"}]}` | Shared settings for all applications (scheduling, env, storage, secrets, image, gateway) |
| common.affinity | object | `{}` | Node affinity applied to all application pods |
| common.env | list | `[]` | Extra environment variables for every application container |
| common.environment | string | `"dev"` | Logical environment (dev/staging/prod), used in labels/annotations |
| common.gatewayApi | object | `{"parentRefs":[]}` | Cluster-scoped Gateway/GatewayClass live elsewhere; the chart only renders HTTPRoutes |
| common.grafana.dashboard.enabled | bool | `false` | Render the SRE Grafana dashboard ConfigMap (kube-prometheus-stack sidecar picks it up) |
| common.image | object | `{"pullPolicy":"IfNotPresent","repository":"nginx","tag":""}` | Default container image for applications/jobs/cronjobs without their own image |
| common.image.pullPolicy | string | `"IfNotPresent"` | Kubernetes pull policy for the default image |
| common.image.repository | string | `"nginx"` | Registry/repo of the default image |
| common.image.tag | string | `""` | Required: rendering fails when the effective tag is empty |
| common.imagePullSecrets | list | `[]` | Registry pull secrets for the default image |
| common.infisical | object | `{"commonSecret":{"credentialsRef":{"secretName":"client-infisical-secrets"},"enabled":false,"projectSlug":"","secretsPath":"/"},"enabled":false,"resyncInterval":10,"url":"http://infisical-standalone-infisical.infisical.svc.cluster.local:8080/api"}` | Infisical ExternalSecret sync (requires the Infisical operator CRDs) |
| common.infisical.commonSecret | object | `{"credentialsRef":{"secretName":"client-infisical-secrets"},"enabled":false,"projectSlug":"","secretsPath":"/"}` | Shared secret store for all applications in the release |
| common.infisical.commonSecret.projectSlug | string | `""` | Infisical project slug to sync secrets from |
| common.infisical.resyncInterval | int | `10` | External Secrets resync interval in seconds |
| common.infisical.url | string | `"http://infisical-standalone-infisical.infisical.svc.cluster.local:8080/api"` | Infisical API URL |
| common.ingress | object | `{"className":"nginx"}` | Ingress class for per-application Ingress resources |
| common.nodeSelector | object | `{}` | Node selector applied to all application pods |
| common.sharedPVCs | list | `[]` | PVCs provisioned in the release namespace and mounted into every application pod. Per-item `annotations` are merged onto the claim; `helm.sh/resource-policy=keep` is the default so uninstall does not delete the volume. Set `helm.sh/hook` on a claim that was created as a Helm hook so upgrade does not try to adopt it. |
| common.sharedSecrets | list | `[]` | Pre-existing Secrets mounted into every application pod |
| common.tolerations | list | `[]` | Tolerations applied to all application pods |
| cronjobs | list | `[]` | CronJobs with schedule/timeZone/concurrency policy and history limits; empty image tag fails rendering |
| fullnameOverride | string | `""` | Full resource name override (defaults to release+chart name) |
| imagePullSecrets | list | `[]` | Secret refs for private registries, e.g. `[{name: regcred}]` |
| jobs | list | `[]` | One-off Jobs (migrations etc.); empty image tag fails rendering |
| nameOverride | string | `""` | Short chart name override (defaults to chart name) |
| serviceAccount | object | `{"annotations":{},"automount":true,"create":false,"name":""}` | Service account for the rendered resources |
| serviceAccount.automount | bool | `true` | Automatically mount the ServiceAccount token inside pods |
| serviceAccount.create | bool | `false` | Create a ServiceAccount and attach it to rendered workloads |
| serviceAccount.name | string | `""` | ServiceAccount name (defaults to <fullname>) |
