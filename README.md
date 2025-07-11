This repository contains Helm charts for deploying various services in Kubernetes.

**reverse-proxy** — A Helm chart for deploying an NGINX-based reverse proxy.

The chart allows you to proxy requests to external and internal resources, configure redirects and headers via values.yaml.

Main features:
- Flexible configuration of paths and target addresses for proxying
- Support for NGINX annotations for fine-tuning behavior
- Integration with Ingress and Service
- Convenient display of all configured redirects in a table format
