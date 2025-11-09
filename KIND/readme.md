# KIND (Kubernetes IN Docker) Cluster Setup

This guide provides step-by-step instructions for creating a production-ready Kubernetes cluster using KIND with high availability control plane and ingress support.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Cluster Configuration](#cluster-configuration)
- [Cluster Operations](#cluster-operations)
- [Ingress Setup](#ingress-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Cleanup](#cleanup)

## Prerequisites

### System Requirements
- Linux OS (Ubuntu 20.04+ recommended)
- Minimum 8GB RAM (16GB+ recommended for full cluster)
- 4 CPU cores minimum
- 20GB free disk space
- Docker installed and running

### Required Tools
- Docker
- kubectl
- kind

## Installation

### 1. Install Docker

```bash
# Update package list
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group
sudo usermod -aG docker $USER

# Verify Docker installation
docker --version
```

**Important:** Log out and log back in for group membership to take effect.

### 2. Install kubectl

```bash
# Download kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Make it executable
chmod +x kubectl

# Move to PATH
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

### 3. Install KIND

```bash
# Download KIND
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64

# Make it executable
chmod +x ./kind

# Move to PATH
sudo mv ./kind /usr/local/bin/kind

# Verify installation
kind version
```

## Cluster Configuration

### Basic Cluster (1 Control Plane + 1 Worker)

Use `config-basic.yaml`:

```bash
kind create cluster --config config-basic.yaml
```

### HA Cluster (3 Control Planes + 3 Workers)

Use `config-ha.yaml`:

```bash
kind create cluster --config config-ha.yaml
```

### Production Cluster (3 Control Planes + 3 Workers + Ingress)

Use `config-production.yaml`:

```bash
kind create cluster --config config-production.yaml --wait 5m
```

## Cluster Operations

### Create Cluster

```bash
# Basic cluster
kind create cluster --name my-cluster

# With custom config
kind create cluster --config config-production.yaml --name production-cluster

# With specific Kubernetes version
kind create cluster --image kindest/node:v1.29.2 --name my-cluster
```

### List Clusters

```bash
kind get clusters
```

### Get Cluster Info

```bash
kubectl cluster-info --context kind-app-1-cluster
```

### View Nodes

```bash
kubectl get nodes -o wide
```

### Delete Cluster

```bash
kind delete cluster --name app-1-cluster
```

### Export Kubeconfig

```bash
kind export kubeconfig --name app-1-cluster
```

## Ingress Setup

### 1. Install Ingress-NGINX Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

### 2. Wait for Ingress Controller to be Ready

```bash
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### 3. Verify Ingress Installation

```bash
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx
```

### 4. Test Ingress

Deploy the sample application:

```bash
kubectl apply -f examples/sample-app.yaml
kubectl apply -f examples/sample-ingress.yaml
```

Test the ingress:

```bash
curl http://localhost/
```

## Verification

### Check Cluster Health

```bash
# Check nodes
kubectl get nodes

# Check system pods
kubectl get pods -n kube-system

# Check all resources
kubectl get all --all-namespaces
```

### Verify HA Setup

```bash
# Check control plane nodes
kubectl get nodes -l node-role.kubernetes.io/control-plane

# Check etcd pods
kubectl get pods -n kube-system -l component=etcd
```

### Check Resource Usage

```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods -A
```

## Troubleshooting

### Common Issues

#### 1. "too many open files" Error

```bash
# Check current limit
ulimit -n

# Increase file descriptor limit (temporary)
ulimit -n 65536

# Permanent fix - edit /etc/security/limits.conf
sudo bash -c 'cat >> /etc/security/limits.conf <<EOF
* soft nofile 65536
* hard nofile 65536
EOF'
```

#### 2. Worker Nodes Not Ready

```bash
# Check node status
kubectl describe node <node-name>

# Check kubelet logs
docker exec <node-container> journalctl -u kubelet -n 50

# Restart the node
docker restart <node-container>
```

#### 3. CNI Plugin Issues

```bash
# Check CNI pods
kubectl get pods -n kube-system -l k8s-app=kindnet

# Check CNI logs
kubectl logs -n kube-system -l k8s-app=kindnet
```

#### 4. Docker Not Running

```bash
# Check Docker status
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# Enable Docker on boot
sudo systemctl enable docker
```

### Debug Commands

```bash
# Get cluster logs
kind export logs --name app-1-cluster

# Check Docker containers
docker ps -a | grep kind

# Inspect node container
docker exec -it app-1-cluster-control-plane bash

# Check cluster events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'
```

## Cleanup

### Delete Specific Cluster

```bash
kind delete cluster --name app-1-cluster
```

### Delete All KIND Clusters

```bash
kind delete clusters --all
```

### Remove KIND Images

```bash
docker images | grep kindest | awk '{print $3}' | xargs docker rmi -f
```

### Complete Cleanup

```bash
# Delete all clusters
kind delete clusters --all

# Remove Docker containers
docker container prune -f

# Remove Docker images
docker image prune -a -f

# Remove Docker volumes
docker volume prune -f
```

## Additional Resources

- [Official KIND Documentation](https://kind.sigs.k8s.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Ingress-NGINX Documentation](https://kubernetes.github.io/ingress-nginx/)
- [Docker Documentation](https://docs.docker.com/)

## Quick Reference

### Useful kubectl Commands

```bash
# Get cluster info
kubectl cluster-info

# Get all resources in all namespaces
kubectl get all -A

# Describe a resource
kubectl describe <resource-type> <resource-name> -n <namespace>

# View logs
kubectl logs <pod-name> -n <namespace>

# Execute command in pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Port forward
kubectl port-forward <pod-name> <local-port>:<pod-port> -n <namespace>

# Apply manifests
kubectl apply -f <file.yaml>

# Delete resources
kubectl delete -f <file.yaml>
```

### Useful Docker Commands

```bash
# List KIND containers
docker ps | grep kind

# Execute command in container
docker exec -it <container-name> bash

# View container logs
docker logs <container-name>

# Inspect container
docker inspect <container-name>

# Stop container
docker stop <container-name>

# Restart container
docker restart <container-name>
```

## Configuration Files Overview

- `config-basic.yaml` - Single node development cluster
- `config-ha.yaml` - 3 control-plane nodes for HA (no workers)
- `config-production.yaml` - Full HA cluster with 3 control-planes + 3 workers + ingress
- `config-custom.yaml` - Template for custom configurations
