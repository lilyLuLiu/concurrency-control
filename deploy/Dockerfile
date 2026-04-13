FROM registry.access.redhat.com/ubi9/ubi-minimal

LABEL org.opencontainers.image.authors="CodeReady Containers <devtools-cdk@redhat.com>"

ARG TARGETARCH

RUN microdnf install -y openssh-clients sshpass zip bash jq python3 pip tar  \
    && if [ "${TARGETARCH}" = "amd64" ]; then \
        OC_ARCH="amd64"; \
        TKN_ARCH="x86_64"; \
    elif [ "${TARGETARCH}" = "arm64" ]; then \
        OC_ARCH="arm64"; \
        TKN_ARCH="aarch64"; \
    else \
        echo "Unsupported architecture: ${TARGETARCH}"; \
        exit 1; \
    fi \
    && OC_URL="https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux-${OC_ARCH}.tar.gz" \
    && TKN_URL="https://github.com/tektoncd/cli/releases/download/v0.42.0/tkn_0.42.0_Linux_${TKN_ARCH}.tar.gz" \
    && curl -kLO ${OC_URL} \
    && tar xzvf "openshift-client-linux-${OC_ARCH}.tar.gz" -C /usr/local/bin \
    && rm "openshift-client-linux-${OC_ARCH}.tar.gz" \
    && curl -kL ${TKN_URL} -o tkn.tar.gz \
    && tar xvzf tkn.tar.gz -C /usr/local/bin \
    && rm tkn.tar.gz \
    && pip install --no-cache-dir paramiko flask \
    && microdnf clean all \
    && chmod 777 -R /opt/

COPY src /opt/
