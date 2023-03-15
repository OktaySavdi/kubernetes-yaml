### Deploy first password in the cluster

login vault pod
```
kubectl exec -it vault-0 -n vault -- sh
```
login with root token
```
vault login 
```
Enable secret engine
```
vault secrets enable -path=internal kv-v2 
```
### Policies 
```
vault policy write app - <<EOF
path "secret*"{
 capabilities = ["read"]
}
EOF
```
### Access
```
vault auth enable kubernetes 

vault write auth/kubernetes/config \
   token-reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
   kubernetes_host=https://${KUBERNETES_PORT_443_TCP_ADDR}:443 \
   kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

vault write auth/kubernetes/role/myapp \
   bound_service_account_names=app \
   bound_service_account_namespaces=demo \
   policies=app \
   ttl=24h
   
vault read auth/kubernetes/config
```
create secret
```
vault kv put secret/helloworld username=oktay password=savdi
```
Deploy application
```yaml
cat <<EOF|kubectl apply -f-
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app
  namespace: demo
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: vault-agent-demo
  name: app
  namespace: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vault-agent-demo
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true" # must be change
        vault.hashicorp.com/role: "myapp" # must be change
        vault.hashicorp.com/agent-inject-secret-helloworld: "secret/helloworld" # must be change
        vault.hashicorp.com/agent-inject-template-helloworld: | # must be change
          {{- with secret "secret/helloworld" -}}
          {
            "username" : "{{ .Data.data.username }}",
            "password" : "{{ .Data.data.password }}"
          }
          {{- end }}
      labels:
        app: vault-agent-demo
    spec:
      serviceAccountName: app # must be change
      containers:
      - image: jweissig/app:0.0.1
        name: app
EOF
```
Next, lets launch our example application and create the service account. We can also verify there are no secrets mounted at `/vault/secrets`.
```
kubectl exec -it app-789d677db4-9fd5m -c app -- ls -l /vault/secrets
kubectl exec -it app-789d677db4-9fd5m -c app -- cat /vault/secrets/helloworld
```
