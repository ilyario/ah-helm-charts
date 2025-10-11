# Helm Charts Repository

This repository contains Helm charts for deploying various services in Kubernetes.

## Available Charts

### static-proxy

A Helm chart for deploying an NGINX-based reverse proxy.

The chart allows you to proxy requests to external and internal resources, configure redirects and headers via values.yaml.

Main features:
- Flexible configuration of paths and target addresses for proxying
- Support for NGINX annotations for fine-tuning behavior
- Integration with Ingress and Service
- Convenient display of all configured redirects in a table format

#### Installation

```bash
helm install my-static-proxy ah-helm/static-proxy
```

#### Upgrading

```bash
helm upgrade my-static-proxy ah-helm/static-proxy
```

## Development

To add a new chart:

1. Create a new directory in `charts/` with your chart
2. Update the version in `Chart.yaml`
3. Push to main branch - the GitHub Action will automatically package and update the repository index
