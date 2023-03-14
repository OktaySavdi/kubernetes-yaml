
### Create self-sign certificate

1- Generate a private key:
```
openssl genrsa -out server.key 2048
```
2- Create a CSR (Certificate Signing Request) file:
```
openssl req -new -key server.key -out server.csr
```
3- Generate a CA (Certificate Authority) certificate and key:
```
openssl genrsa -out ca.key 2048
openssl req -new -x509 -key ca.key -out ca.crt
```

4- Sign the CSR with the CA certificate:
```
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365
```
### Create Namespace
```
kubectl create namespace harbor
```
### Create Secret for TLS encryption with encoded certification
```
kubectl create secret generic <NAME> --from-file=tls.crt=<PATH  TO  CRT> --from-file=tls.key=<PATH  TO  KEY> --namespace=<NAME>

kubectl create secret generic my-harbor-crt --from-file=tls.crt=server.crt --from-file=tls.key=server.key --from-file=ca.crt=ca.crt
```
### Add repo and install Harbor via heml chart
```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```
```
helm fetch bitnami/harbor --untar
```
```
helm install myharbor bitnami/harbor -f values.yaml
``` 
###  Get admin Passwort
```
kubectl get secret -n <NAMESPACE> <SECRET NAME - harbor-core-envvars> -o jsonpath='{.data.HARBOR_ADMIN_PASSWORD}'| base64 --decode
```
### Login via CLI
```
podman login myharbor.com -u <user> -p '<password>' --tls-verify=false
podman pull quay.io/oktaysavdi/istioproject
podman push quay.io/oktaysavdi/istioproject myharbor.com/library/istio:latest --tls-verify=false
```
URL - https://artifacthub.io/packages/helm/bitnami/harbor

URL - https://goharbor.io/docs/

![image](https://user-images.githubusercontent.com/3519706/224947295-1c6f533c-ee2a-4086-90be-bd1c95f3d08d.png)
