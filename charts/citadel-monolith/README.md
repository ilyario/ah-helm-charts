# Citadel Monolith Helm Chart

A Helm chart for deploying monolithic applications in Kubernetes clusters.

## Description

This Helm chart is designed for deploying monolithic applications with support for:
- Multiple applications in a single release
- Infisical integration for secret management
- Automatic scaling (HPA)
- Ingress configuration
- Jobs for migrations and other tasks
- Monitoring through Grafana

## Requirements

- Kubernetes 1.19+
- Helm 3.0+
- Ingress controller (e.g., nginx-ingress)

## Installation

### Adding the repository

```bash
helm repo add ah-helm-charts https://your-repo-url
helm repo update
```

### Installing the chart

```bash
# Basic installation
helm install my-citadel ah-helm-charts/citadel-monolith

# Installation with custom values
helm install my-citadel ah-helm-charts/citadel-monolith -f values.yaml

# Installation in a specific namespace
helm install my-citadel ah-helm-charts/citadel-monolith --namespace my-namespace --create-namespace
```

## Configuration

### Main parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `nameOverride` | Override the release name | `""` |
| `fullnameOverride` | Override the full name | `""` |
| `common.environment` | Environment (dev, staging, prod) | `dev` |
| `common.grafana` | Grafana URL for monitoring | `""` |

### Application configuration

The chart supports deploying multiple applications. Each application can have:

```yaml
applications:
  - name: nginx
    replicaCount: 1
    image:
      repository: nginx
      tag: "latest"
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

### Jobs for migrations

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

## Usage

### Updating the release

```bash
helm upgrade my-citadel ah-helm-charts/citadel-monolith -f values.yaml
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
    livenessProbe:
      httpGet:
        path: /health
        port: http
    readinessProbe:
      httpGet:
        path: /ready
        port: http
```

## Troubleshooting

If you encounter issues:

1. Check pod status: `kubectl get pods -n <namespace>`
2. View logs: `kubectl logs <pod-name> -n <namespace>`
3. Check events: `kubectl get events -n <namespace>`
4. Verify values.yaml configuration is correct

## License

This project is licensed under MIT.
