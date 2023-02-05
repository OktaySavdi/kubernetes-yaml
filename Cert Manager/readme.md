

## Cert Manager

### Let's install cert manager:
```
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm upgrade cert-manager jetstack/cert-manager \
    --install \
    --create-namespace \
    --wait \
    --namespace cert-manager \
    --set installCRDs=true
```
### Verify things installed correctly:
```
kubectl get po -n cert-manager
```
### Since we're going to use our own CA as the backend, let's install the correct root certs/keys:
```
kubectl create -n cert-manager secret tls root-secret --cert labs/04/certs/ca/root-ca.crt --key labs/04/certs/ca/root-ca.key
```
### Let's configure a ClusterIssuer to use our CA:
```yaml
cat << EOF | kubectl create -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: ca-issuer
spec:
  ca:
    secretName: root-secret
EOF
```
### We will ask ask cert-manager to issue us a secret with this config:
```yaml
cat << EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: myapp-cert
  namespace: example
spec:
  secretName: oktay-secret
  duration: 2160h # 90d
  renewBefore: 360h # 15d
  privateKey:
    algorithm: RSA
    encoding: PKCS1
    size: 2048
    rotationPolicy: Always
  issuerRef:
    name: ca-issuer
    kind: ClusterIssuer
  dnsNames:
  - "oktaysavdi.com"
EOF
```
### Let's deploy application:
```yaml
cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: web
  name: web
  namespace: example
spec:
  replicas: 2
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: web
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: web
    spec:
      containers:
      - image: quay.io/oktaysavdi/istioproject
        imagePullPolicy: Always
        name: istioproject
--- 
apiVersion: v1
kind: Service 
metadata:     
  labels:
    app: web
  name: web
  namespace: example
spec:
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 8080
  selector:
    app: web
  type: ClusterIP
EOF
```
### Let's deploy ingress
```yaml
cat << EOF | kubectl apply -f-
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-manager.io/issuer: "ca-issuer"
  name: myapp-ingress
spec:
  tls:
  - hosts:
    - oktaysavdi.com
    secretName: oktay-secret
  ingressClassName: nginx
  rules:
  - host: oktaysavdi.com
    http:
      paths:
      - backend:
          service:
            name: web
            port:
              number: 8080
        path: /
        pathType: Prefix
EOF
```
### test cert
```
curl --cacert ./labs/04/certs/ca/root-ca.crt -H "Host: oktaysavdi.com" https://oktaysavdi.com --resolve oktaysavdi.com:443:$GATEWAY_IP
```
