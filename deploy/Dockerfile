FROM registry.access.redhat.com/ubi9/ubi-minimal
ARG TARGETARCH
LABEL org.opencontainers.image.authors="CodeReady Containers <devtools-cdk@redhat.com>"

ENV TKN_URL="https://github.com/tektoncd/cli/releases/download/v0.42.0/tkn_0.42.0_Linux_x86_64.tar.gz"
ENV OC_URL="https://downloads-openshift-console.apps.gpc.ocp-hub.prod.psi.redhat.com/${TARGETARCH}/linux/oc.tar"

RUN microdnf install -y openssh-clients sshpass zip bash jq python3 pip tar \
    && if [ "$TARGETARCH" = "arm64" ]; then export TKN_URL="https://github.com/tektoncd/cli/releases/download/v0.42.0/tkn_0.42.0_Linux_aarch64.tar.gz"; fi \
    && curl -kLO ${OC_URL} \
    && tar xvf oc.tar -C /usr/local/bin \
    && curl -kL ${TKN_URL} -o tkn.tar.gz \
    && tar xvzf tkn.tar.gz -C /usr/local/bin \
    && pip install --no-cache-dir paramiko \
    && microdnf clean all \
    && chmod 777 -R /opt/

COPY src /opt/