# Concurrency Control for Tekton Pipelines

## Overview

This project provides a concurrency control system for Tekton pipelines, ensuring that pipelines are executed in an orderly manner based on the availability of test machines. It uses a config map to track the status of each machine and includes a web interface for real-time monitoring of machine statuses, running pipelines, and execution logs.

## Features

- **Pipeline Queuing:** Automatically queues pending pipelines and starts them when the required machines are free.
- **Machine Status Tracking:** Monitors the status of each machine (`free` or `busy`) using a Kubernetes config map.
- **Web Interface:** A web-based UI that displays:
  - The current status of all machines.
  - A list of currently running pipelines and the machines they are using.
  - A live-scrolling window with the latest execution logs.
- **Containerized Deployment:** The application is designed to be deployed in a container on an OpenShift or Kubernetes cluster.

## Prerequisites

- An OpenShift or Kubernetes cluster.
- `oc` or `kubectl` command-line tool configured to access your cluster.
- A service account with permissions to manage Tekton pipelines and config maps.

## Deployment

1. **Configure the Service Account:**
   The deployment uses a service account named `ci-use`. Ensure this service account exists in your namespace and has the necessary roles and permissions to manage Tekton resources and config maps.

2. **Deploy the Application:**
   Apply the `deployment.yaml` file to deploy the application:
   ```shell
   oc apply -f deploy/deployment.yaml
   ```

3. **Access the Web Interface:**
   The application is exposed via a `NodePort` service. To find the URL to access the web interface, run the following command:
   ```shell
   oc get service concurrency-control-service
   ```
   The output will show the port mapping. You can access the UI at `http://<node-ip>:<node-port>`.

## Configuration

The application is configured using environment variables set in the `deploy/deployment.yaml` file:

- `NAMESPACE`: The namespace where the Tekton pipelines are running.
- `MACHINE_CM`: The name of the config map used to store machine statuses.
- `LABEL_MACHINE_PR`: The label on the `PipelineRun` that specifies the primary machine.
- `LAEBL_MACHINE_TASK`: The label on the `PipelineRun` that specifies the machine for a specific task.
- `LABEL_TASK`: The name of the task to monitor for machine release.

## File Structure

- `src/control.py`: The main script that runs the control loop for monitoring and starting pipelines.
- `src/web.py`: The Flask application that serves the web interface.
- `src/configmap.py`: A utility module for interacting with the machine status and pipeline config maps.
- `src/log.py`: Configures the application's logging.
- `src/templates/status.html`: The HTML template for the web interface.
- `deploy/deployment.yaml`: The Kubernetes deployment file for the application.
