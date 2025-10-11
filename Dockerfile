# Первый стейдж: сборка и установка инструментов
FROM alpine:3.19 AS builder

# Определяем build arguments для версий в builder стейдже
ARG KUBECTL_VERSION=v1.33.0
ARG HELM_VERSION=v3.15.0
ARG HELM_DIFF_VERSION=v3.8.1
ARG HELMFILE_VERSION=v1.1.5

# Устанавливаем необходимые пакеты для сборки
RUN apk add --no-cache \
    curl \
    bash \
    git \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Устанавливаем kubectl
RUN curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

# Устанавливаем Helm
RUN curl -fsSL "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" | tar xz \
    && mv linux-amd64/helm /usr/local/bin/ \
    && rm -rf linux-amd64

RUN helm plugin install https://github.com/databus23/helm-diff --version ${HELM_DIFF_VERSION}

# Устанавливаем helmfile
RUN curl -fsSL -o /tmp/helmfile.tar.gz \
    "https://github.com/helmfile/helmfile/releases/download/${HELMFILE_VERSION}/helmfile_${HELMFILE_VERSION#v}_linux_amd64.tar.gz" && \
    tar -xzf /tmp/helmfile.tar.gz -C /tmp && \
    mv /tmp/helmfile /usr/local/bin/helmfile && \
    chmod +x /usr/local/bin/helmfile && \
    rm -rf /tmp/helmfile.tar.gz /tmp/helmfile

# Проверяем установку всех инструментов
RUN kubectl version --client && \
    helm version && \
    helm plugin list | grep diff && \
    helmfile version

# Второй стейдж: финальный минимальный образ
FROM alpine:3.19 AS runtime

# Устанавливаем только необходимые runtime пакеты
RUN apk add --no-cache \
    bash \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Копируем установленные инструменты из builder стейджа
COPY --from=builder /usr/local/bin/kubectl /usr/local/bin/
COPY --from=builder /usr/local/bin/helm /usr/local/bin/
COPY --from=builder /usr/local/bin/helmfile /usr/local/bin/
COPY --from=builder /root/.local/share/helm/plugins/ /root/.local/share/helm/plugins/

# Создаем рабочую директорию
WORKDIR /workspace

# Создаем директорию для charts
RUN mkdir -p /workspace/charts

# Копируем charts
COPY charts/ /workspace/charts/

# Устанавливаем bash как оболочку по умолчанию
SHELL ["/bin/bash", "-c"]

# Команда по умолчанию
CMD ["/bin/bash"]