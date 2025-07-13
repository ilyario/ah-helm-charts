# Helm Charts Repository

This repository contains Helm charts for deploying various services in Kubernetes.

## Adding this repository

```bash
helm repo add helms https://ilyario.github.io/helms
helm repo update
```

## Available Charts

### reverse-proxy

A Helm chart for deploying an NGINX-based reverse proxy.

The chart allows you to proxy requests to external and internal resources, configure redirects and headers via values.yaml.

Main features:
- Flexible configuration of paths and target addresses for proxying
- Support for NGINX annotations for fine-tuning behavior
- Integration with Ingress and Service
- Convenient display of all configured redirects in a table format

#### Installation

```bash
helm install my-reverse-proxy helms/reverse-proxy
```

#### Upgrading

```bash
helm upgrade my-reverse-proxy helms/reverse-proxy
```

## Development

To add a new chart:

1. Create a new directory in `charts/` with your chart
2. Update the version in `Chart.yaml`
3. Push to main branch - the GitHub Action will automatically package and update the repository index

## Repository Structure

```
helms/
├── charts/
│   └── reverse-proxy/     # Chart source
├── index.yaml            # Repository index (auto-generated)
├── *.tgz                 # Packaged charts (auto-generated)
└── .github/workflows/    # CI/CD workflows
```
