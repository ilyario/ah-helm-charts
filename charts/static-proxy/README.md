![Version: 0.1.2](https://img.shields.io/badge/Version-0.1.2-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

NGINX-based static-file proxy: routes URL paths to S3-compatible object storage
or other upstreams via plain values.yaml. Renders a Deployment, Service and
optionally Ingress and HPA.

## Features

- Locations declared from values: `config.targets` maps `target` (URL path) to `source` (upstream URL) with raw nginx `annotations` directives per location
- Chart-managed nginx ConfigMap (`default.conf`) built from `config.targets`
- Ingress with optional TLS (single `spec.tls` block, `hosts` from `ingress.tls`)
- HorizontalPodAutoscaler via `autoscaling.enabled`

## Requirements

- Kubernetes 1.23+ (enforced via `kubeVersion: ">=1.23.0-0"`)
- Helm 3.0+ (Helm 4 works as well)
- Optional: an ingress controller; Prometheus metrics-server for HPA

## Installation

```bash
helm repo add ah-helm https://ilyario.github.io/ah-helm-charts
helm repo update

# From the published repo
helm install my-static-proxy ah-helm/static-proxy -f my-values.yaml

# Or straight from a git checkout
helm install my-static-proxy ./charts/static-proxy -f my-values.yaml
```

## Example config

```yaml
config:
  targets:
    - target: /storage/file
      pathType: ImplementationSpecific
      source: https://storage.yandexcloud.net/bucket/file.pdf
      annotations: |
        proxy_redirect     off;
        proxy_hide_header Content-Type;
        add_header Content-Type application/pdf;
        add_header Content-Disposition "inline";

ingress:
  enabled: true
  hosts:
    - host: static.example.com
      paths:
        - path: /storage(/|$)(.*)
          pathType: ImplementationSpecific
  tls:
    - secretName: static-tls
      hosts:
        - static.example.com
```

## Values

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` | Node affinity for proxy pods |
| autoscaling | object | `{"enabled":false,"maxReplicas":100,"minReplicas":1,"targetCPUUtilizationPercentage":80}` | HorizontalPodAutoscaler for the proxy |
| autoscaling.enabled | bool | `false` | Render the HPA (overrides replicaCount) |
| config | object | `{"targets":[{"annotations":"proxy_redirect     off;\nproxy_hide_header Content-Type;\nadd_header Content-Type application/pdf;\nadd_header Content-Disposition \"inline\";\n","pathType":"ImplementationSpecific","source":"https://storage.yandexcloud.net/test/file.pdf","target":"/storage/file"},{"annotations":"proxy_redirect     off;\nproxy_hide_header Content-Type;\nadd_header Content-Type application/pdf;\nadd_header Content-Disposition \"inline\";\n","pathType":"ImplementationSpecific","source":"https://storage.yandexcloud.net/test/public/","target":"/storage/files"},{"annotations":"proxy_set_header Host storage.yandexcloud.net;\nadd_header Access-Control-Allow-Origin *;\nproxy_send_timeout         30;\nproxy_read_timeout         30;\n","pathType":"ImplementationSpecific","source":"https://storage.yandexcloud.net/test/public/","target":"/storage/public/"}]}` | NGINX proxy locations: `target` — URL path to serve, `source` — upstream, `annotations` — raw nginx location directives applied inside `location` block |
| config.targets | list | `[{"annotations":"proxy_redirect     off;\nproxy_hide_header Content-Type;\nadd_header Content-Type application/pdf;\nadd_header Content-Disposition \"inline\";\n","pathType":"ImplementationSpecific","source":"https://storage.yandexcloud.net/test/file.pdf","target":"/storage/file"},{"annotations":"proxy_redirect     off;\nproxy_hide_header Content-Type;\nadd_header Content-Type application/pdf;\nadd_header Content-Disposition \"inline\";\n","pathType":"ImplementationSpecific","source":"https://storage.yandexcloud.net/test/public/","target":"/storage/files"},{"annotations":"proxy_set_header Host storage.yandexcloud.net;\nadd_header Access-Control-Allow-Origin *;\nproxy_send_timeout         30;\nproxy_read_timeout         30;\n","pathType":"ImplementationSpecific","source":"https://storage.yandexcloud.net/test/public/","target":"/storage/public/"}]` | List of proxy locations; `pathType` maps to the nginx location modifier |
| fullnameOverride | string | `""` | Full resource name override (defaults to release+chart name) |
| gatewayApi | object | `{"annotations":{},"enabled":false,"labels":{},"parentRefs":[]}` | Gateway API: HTTPRoute to an existing Gateway (Gateway/GatewayClass deployed separately). |
| gatewayApi.annotations | object | `{}` | Extra HTTPRoute annotations |
| gatewayApi.enabled | bool | `false` | Render the HTTPRoute resource |
| gatewayApi.labels | object | `{}` | Extra HTTPRoute labels |
| gatewayApi.parentRefs | list | `[]` | Gateway API parentRefs |
| image | object | `{"pullPolicy":"IfNotPresent","repository":"nginx","tag":"1.29"}` | Proxy container image |
| image.pullPolicy | string | `"IfNotPresent"` | Kubernetes pull policy |
| image.repository | string | `"nginx"` | Registry/repo of the proxy image |
| image.tag | string | `"1.29"` | Image tag (falls back to Chart.appVersion when empty) |
| imagePullSecrets | list | `[]` | Registry pull secrets for the proxy image |
| ingress | object | `{"annotations":{},"className":"nginx","enabled":true,"host":"static-proxy.example.com","tls":[]}` | Ingress for the proxy (host covers all config.targets) |
| ingress.annotations | object | `{}` | Extra Ingress annotations |
| ingress.className | string | `"nginx"` | Ingress class |
| ingress.enabled | bool | `true` | Render the Ingress resource |
| ingress.host | string | `"static-proxy.example.com"` | Ingress host |
| ingress.tls | list | `[]` | TLS entries (single spec.tls block in the rendered Ingress) |
| nameOverride | string | `""` | Short chart name override (defaults to chart name) |
| nodeSelector | object | `{}` | Node selector for proxy pods |
| podAnnotations | object | `{}` | Extra annotations on the proxy pod template |
| podLabels | object | `{}` | Extra labels on the proxy pod template |
| podSecurityContext | object | `{}` | Pod-level security context |
| replicaCount | int | `3` | Number of proxy replicas |
| resources | object | `{}` | Container resources for the proxy |
| securityContext | object | `{}` | Container security context |
| service | object | `{"port":80,"type":"ClusterIP"}` | Proxy Service |
| service.port | int | `80` | Service port |
| tolerations | list | `[]` | Tolerations for proxy pods |
