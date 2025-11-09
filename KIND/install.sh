#!/bin/bash

set -e

echo "================================"
echo "KIND Cluster Installation Script"
echo "================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Please do not run this script as root"
   exit 1
fi

echo "[1/4] Installing Docker..."
echo "----------------------------"

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

# Add user to docker group
sudo usermod -aG docker $USER

echo "Docker installed successfully!"
docker --version
echo ""

echo "[2/4] Installing kubectl..."
echo "----------------------------"

# Download kubectl
KUBECTL_VERSION=$(curl -L -s https://dl.k8s.io/release/stable.txt)
curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"

# Make it executable
chmod +x kubectl

# Move to PATH
sudo mv kubectl /usr/local/bin/

echo "kubectl installed successfully!"
kubectl version --client
echo ""

echo "[3/4] Installing KIND..."
echo "-------------------------"

# Download KIND
KIND_VERSION="v0.20.0"
curl -Lo ./kind "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-amd64"

# Make it executable
chmod +x ./kind

# Move to PATH
sudo mv ./kind /usr/local/bin/kind

echo "KIND installed successfully!"
kind version
echo ""

echo "[4/4] Post-installation steps..."
echo "---------------------------------"

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

echo ""
echo "================================"
echo "Installation Complete!"
echo "================================"
echo ""
echo "IMPORTANT: You need to log out and log back in for Docker group membership to take effect."
echo ""
echo "After logging back in, you can create a cluster with:"
echo "  kind create cluster --config config-production.yaml"
echo ""
echo "Or use the quick start script:"
echo "  ./create-cluster.sh"
echo ""
