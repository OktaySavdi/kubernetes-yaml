### Install Kind
```
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.17.0/kind-linux-amd64
chmod +x ./kind
mv ./kind /usr/local/bin/kind
```
### Install Kubectl
```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
mkdir -p ~/.local/bin
mv ./kubectl /usr/local/bin/kubectl
source <(kubectl completion bash)
echo "source <(kubectl completion bash)" >> ~/.bashrc
```
### Config
```
cat <<EOF> config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: app-1-cluster
networking:
  apiServerPort: 6443
  apiServerAddress: 127.0.0.1
  podSubnet: "10.244.0.0/16"
  serviceSubnet: "10.96.0.0/12"
  kubeProxyMode: "ipvs"
  #disableDefaultCNI: true
kubeadmConfigPatches:
- |
  apiVersion: kubelet.config.k8s.io/v1beta1
  kind: KubeletConfiguration
  evictionHard:
    nodefs.available: "0%"
nodes:
- role: control-plane
  labels:
    company: greentube    
- role: worker
  labels:
    company: novamatic
- role: worker
  labels:
    ingress-ready: true
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
- role: worker
  image: kindest/node:v1.25.3@sha256:f52781bc0d7a19fb6c405c2af83abfeb311f130707a0e219175677e366cc45d1
EOF
```
### Login Cluster
```
kind create cluster --config config.yaml
kubectl config get-contexts
kubectl config use-context kind-app-1-cluster
```
### Deploy Ingress
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl config set-context --current --namespace ingress-nginx
```
### Deploy App
```
kubectl create deployment web --image=quay.io/oktaysavdi/istioproject
kubectl expose deploy web --target-port=8080 --port=80

cat <<EOF | kubectl create -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /istio
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
EOF
```
