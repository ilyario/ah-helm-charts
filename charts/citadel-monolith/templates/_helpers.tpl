{{/*
Expand the name of the chart.
*/}}
{{- define "citadel-common.name" -}}
{{- $raw := default .Chart.Name .Values.nameOverride }}
{{- include "citadel-common.dnsLabel" $raw }}
{{- end }}

{{/*
Convert a string to a single DNS-1035 label (valid for metadata.name segments).
Lowercase, replace dots/underscores, collapse hyphens, ensure leading letter, max 63 chars.
*/}}
{{- define "citadel-common.dnsLabel" -}}
{{- $s := . | toString | lower }}
{{- $s = replace "_" "-" $s }}
{{- $s = replace "." "-" $s }}
{{- $s = regexReplaceAll "[^a-z0-9-]+" $s "-" }}
{{- $s = regexReplaceAll "-+" $s "-" }}
{{- $s = trimAll "-" $s }}
{{- if not $s }}
x
{{- else }}
{{- $out := $s }}
{{- if not (regexMatch "^[a-z]" $s) }}
{{- $out = printf "x%s" $s }}
{{- end }}
{{- $out | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "citadel-common.fullname" -}}
{{- $raw := "" }}
{{- if .Values.fullnameOverride }}
{{- $raw = .Values.fullnameOverride }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- $raw = .Release.Name }}
{{- else }}
{{- $raw = printf "%s-%s" .Release.Name $name }}
{{- end }}
{{- end }}
{{- include "citadel-common.dnsLabel" $raw }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "citadel-common.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "citadel-common.labels" -}}
helm.sh/chart: {{ include "citadel-common.chart" . }}
{{ include "citadel-common.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "citadel-common.selectorLabels" -}}
app.kubernetes.io/name: {{ include "citadel-common.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Compose a full container image reference "repository:tag".
The input is a dict:
  commonRepository, commonTag - fallbacks from common.image
  repository, tag             - optional per-object overrides
  path                        - values path label used in the failure message
Rendering fails with a clear error when the effective repository or tag is empty,
so broken references like "repository:" never reach the cluster.
*/}}
{{- define "citadel-common.image" -}}
{{- $repository := .repository | default .commonRepository | default "" }}
{{- $tag := .tag | default .commonTag | default "" }}
{{- if not $repository }}
{{- fail (printf "citadel: %s: image repository is empty - set common.image.repository or the per-object override" .path) }}
{{- end }}
{{- if not $tag }}
{{- fail (printf "citadel: %s: image tag is empty - set common.image.tag or the per-object override" .path) }}
{{- end }}
{{- printf "%s:%s" $repository $tag }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "citadel-common.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- include "citadel-common.dnsLabel" (default (include "citadel-common.fullname" .) .Values.serviceAccount.name) }}
{{- else }}
{{- include "citadel-common.dnsLabel" (default "default" .Values.serviceAccount.name) }}
{{- end }}
{{- end }}

{{/* Kubernetes Gateway API: name for an HTTPRoute (one per application host) */}}
{{- define "citadel-common.httprouteName" -}}
{{- $root := .root }}{{- $app := .app }}{{- $i := .index -}}
{{ include "citadel-common.fullname" $root }}-{{ $app.name }}-httproute-{{ $i }}
{{- end }}

{{/* Map Ingress pathType to gateway.networking.k8s.io path match type */}}
{{- define "citadel-common.httproutePathMatchType" -}}
{{- $t := . | default "ImplementationSpecific" -}}
{{- if or (eq $t "Prefix") (eq $t "ImplementationSpecific") -}}
PathPrefix
{{- else if eq $t "Exact" -}}
Exact
{{- else if eq $t "RegularExpression" -}}
RegularExpression
{{- else -}}
PathPrefix
{{- end -}}
{{- end }}
