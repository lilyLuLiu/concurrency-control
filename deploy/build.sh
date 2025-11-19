podman build --platform linux/amd64 -t quay.io/crc-org/concurrency:v0.1 -f Dockerfile ../
podman push quay.io/crc-org/concurrency:v0.1