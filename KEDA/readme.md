
1.  Add Helm repo
```sh
helm repo add kedacore https://kedacore.github.io/charts 
```
2.  Update Helm repo
```sh
helm repo update
```
3.  Install  `keda`  Helm chart
    
    **Helm 3**
```sh
helm install keda \
--create-namespace \
--namespace keda \
kedacore/keda 
```

```
kubectl get hpa
kubectl get ScaledObject
```

### Keda Confiration
```
examples - https://keda.sh/docs/2.9/scalers/
```
```yaml
cat <<EOF | kubectl create -f -
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: workload-scaledobject
  namespace: app
spec:
  scaleTargetRef:
    name: web
  minReplicaCount:  1
  maxReplicaCount:  10    
  triggers:
  - type: kubernetes-workload
    metadata:
      podSelector: 'app=web'
      value: '0.5'
      activationValue: '3.1'
EOF
```
### Deploy Application
```yaml
cat <<EOF | kubectl create -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: web
  name: web
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - image: quay.io/oktaysavdi/istioproject
        name: istioproject
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: web
  name: web
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 8080
  selector:
    app: web
  type: LoadBalancer
EOF 
```
### Load Generator
```yaml
cat <<EOF | kubectl create -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: infinite-calls
  labels:
    app: infinite-calls
spec:
  replicas: 2
  selector:
    matchLabels:
      app: infinite-calls
  template:
    metadata:
      name: infinite-calls
      labels:
        app: infinite-calls
    spec:
      containers:
      - name: infinite-calls
        image: busybox
        command:
        - /bin/sh
        - -c
        - "while true; do wget -q -O- http://myapp/istio; done"
EOF
```
