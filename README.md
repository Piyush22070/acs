
# ACS (Agentic Control Sentinel)

ACS is an AI-driven Kubernetes monitoring and self-healing system. It uses LangGraph and the Groq API to continuously ingest pod logs, detect anomalies, and autonomously execute Kubernetes commands (like restarting pods or scaling deployments) to prevent downtime.

## Main Diagram

<img width="600" height="559" alt="image" src="https://github.com/user-attachments/assets/e88bd63b-7440-4512-9d3c-20fab7914541" />


## Docker Repositories

The project relies on the following container images hosted on Docker Hub:

* **ACS Agent**: [piyushdocs/acs-agent](https://hub.docker.com/repository/docker/piyushdocs/acs-agent/general)
* **ACS Server (Backend)**: [piyushdocs/acs-server](https://hub.docker.com/repository/docker/piyushdocs/acs-server)
* **ACS Client (Frontend)**: [piyushdocs/acs-client](https://hub.docker.com/repository/docker/piyushdocs/acs-client/general)
* **Test FastApp**: [piyushdocs/test-fastapp](https://hub.docker.com/repository/docker/piyushdocs/test-fastapp/general)

## Prerequisites

* Minikube installed and running
* kubectl installed
* Python 3.9+
* Groq API Key

## Steps to Start

### 1. Initialize the Cluster

Start Minikube and enable the metrics-server required for the Horizontal Pod Autoscaler (HPA) to function correctly.

```bash
minikube start
minikube addons enable metrics-server

```

### 2. Apply Kubernetes Manifests

Deploy the required infrastructure (Postgres, Redis), the application pods (Backend, Frontend), and the ACS Agent to your default namespace. Ensure your Groq API key is configured within your agent deployment manifest before applying.

```bash
kubectl apply -f k8s/

```

### 3. Verify Deployments

Check that all pods are running and the HPA is successfully tracking targets.

```bash
kubectl get pods
kubectl get hpa

```

### 4. Expose the Backend Service and Frontend

To allow the chaos script to send external traffic directly to your backend, expose the NodePort service using Minikube.

```bash
kubectl port-forward svc/acs-frontend-service 3000:3000
kubectl port-forward svc/acs-backend-service 8000:8000

```

Copy the generated URL (e.g., https://www.google.com/search?q=http://127.0.0.1:XXXXX).

### 5. Run the Chaos Test

Update the `BASE_URL` variable in your `Cahos2.py` file with the URL generated in the previous step. Run the script to inject faults and observe the agent's autonomous healing.

```bash
# Install required Python packages
pip install aiohttp kubernetes

# Execute the stress test
python3 Cahos2.py

```

### 6. Monitor Agent Logs

To view the AI agent's decision-making process and execution steps in real-time, tail the agent's logs in a separate terminal.

```bash
kubectl logs -f deployment/acs-agent
```
