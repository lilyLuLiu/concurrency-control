FROM registry.access.redhat.com/ubi9/ubi-minimal

LABEL org.opencontainers.image.authors="CodeReady Containers <devtools-cdk@redhat.com>"

ENV TKN_URL="https://github.com/tektoncd/cli/releases/download/v0.42.0/tkn_0.42.0_Linux_x86_64.tar.gz"
ENV OC_URL="https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz"

RUN microdnf install -y openssh-clients sshpass zip bash jq python3 pip tar \
    && curl -kLO ${OC_URL} \
    && tar xzf oc.tar.gz -C /usr/local/bin \
    && curl -kL ${TKN_URL} -o tkn.tar.gz \
    && tar xvzf tkn.tar.gz -C /usr/local/bin \
    && pip install --no-cache-dir paramiko \
    && microdnf clean all \
    && chmod 777 -R /opt/

COPY src /opt/