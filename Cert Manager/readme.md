

## Cert Manager

  

### Let's prep for the installation of cert manager:
```
kubectl create namespace cert-manager

helm repo add jetstack https://charts.jetstack.io

helm repo update
```
### Now do the actual installation:
```
helm install cert-manager jetstack/cert-manager --namespace cert-manager --version v1.2.0 --create-namespace --set installCRDs=true
```
### Verify things installed correctly:
```
kubectl get po -n cert-manager
```
### Since we're going to use our own CA as the backend, let's install the correct root certs/keys:
```
kubectl create -n cert-manager secret tls cert-manager-cacerts --cert labs/04/certs/ca/root-ca.crt --key labs/04/certs/ca/root-ca.key
```
### Let's configure a ClusterIssuer to use our CA:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: ca-issuer
  namespace: sandbox
spec:
  ca:
    secretName: cert-manager-cacerts
```
### Lets add it:
```
kubectl apply -f labs/04/cert-manager/ca-cluster-issuer.yaml
```
### We will ask ask cert-manager to issue us a secret with this config:
```
cat labs/04/cert-manager/istioinaction-io-cert.yaml
```
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: istioinaction-cert
  namespace: istio-ingress
spec:
  secretName: istioinaction-cert
  duration: 2160h # 90d
  renewBefore: 360h # 15d
  subject:
    organizations:
    - solo.io
  isCA: false
  privateKey:
    algorithm: RSA
    encoding: PKCS1
    size: 2048
  usages:
    - server auth
    - client auth
  dnsNames:
  - istioinaction.io
  issuerRef:
    name: ca-issuer
    kind: ClusterIssuer
    group: cert-manager.io
```
### After reviewing the config, go ahead and apply it:
```
kubectl apply -f labs/04/cert-manager/istioinaction-io-cert.yaml
```
### Let's make sure the certificate was recognized and issued:
```
kubectl get Certificate -n istio-ingress
```
### Let's check the certificate SAN was specified correctly as istioinaction.io:
```
kubectl get secret -n istio-ingress istioinaction-cert -o jsonpath="{.data['tls\.crt']}" | base64 -d | step certificate inspect -
```
### Let's try call our gateway again to make sure the call still succeeds:
```
curl --cacert ./labs/04/certs/ca/root-ca.crt -H "Host: istioinaction.io" https://istioinaction.io --resolve istioinaction.io:443:$GATEWAY_IP
```
