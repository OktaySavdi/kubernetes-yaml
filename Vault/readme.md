
## Install the Vault Helm chart

The recommended way to run Vault on Kubernetes is via the  [Helm chart](https://developer.hashicorp.com/vault/docs/platform/k8s/helm).

Add the HashiCorp Helm repository.
```
helm repo add hashicorp https://helm.releases.hashicorp.com
```
Update all the repositories to ensure `helm` is aware of the latest versions.
```
helm repo update
```
Search for all the Vault Helm chart versions.
```
helm search repo vault --versions
```
```
NAME CHART VERSION APP VERSION DESCRIPTION 
hashicorp/vault 0.8.0 1.5.4 Official HashiCorp Vault Chart 
hashicorp/vault 0.7.0 1.5.2 Official HashiCorp Vault Chart 
hashicorp/vault 0.6.0 1.4.2 Official HashiCorp Vault Chart 
```
Install the latest version of the Vault Helm chart with the Web UI enabled.
```
helm install vault hashicorp/vault \
  --set='ui.enabled=true' \
  --set='ui.serviceType=LoadBalancer' \
  --create-namespace \
  --namespace=vault
```
The Vault pod, Vault Agent Injector pod, and Vault UI Kubernetes service are deployed in the default namespace.

Get all the pods within the default namespace.
```
kubectl get pods 
```
```
NAME READY STATUS RESTARTS AGE 
vault-0 0/1 Running 0 30s 
vault-agent-injector-56bf46695f-crqqn 1/1 Running 0 30s
```
The  `vault-0`  pod deployed runs a Vault server and reports that it is  `Running`  but that it is not ready (`0/1`). This is because the status check defined in a  [readinessProbe](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-probes)  returns a non-zero exit code.

The  `vault-agent-injector`  pod deployed is a Kubernetes Mutation Webhook Controller. The controller intercepts pod events and applies mutations to the pod if specific annotations exist within the request.

Retrieve the status of Vault on the  `vault-0`  pod.
```
kubectl exec vault-0 -- vault status
```
```
Key Value 
--- ----- 
Seal Type shamir 
Initialized false 
Sealed true 
Total Shares 0 
Threshold 0 
Unseal Progress 0/0 
Unseal Nonce n/a 
Version n/a 
HA Enabled false 
command terminated with exit code 2
```
## Initialize and unseal Vault
Vault starts  [uninitialized](https://developer.hashicorp.com/vault/docs/commands/operator/init)  and in the  [sealed](https://developer.hashicorp.com/vault/docs/concepts/seal#why)  state. The process of initializing and unsealing Vault can be performed via the exposed Web UI.

**Command-line interface:**  The Vault CLI on the  `vault-0`  is able to initialize and unseal the Vault server. For more information refer to the  [Injecting Secrets into Kubernetes Pods via Vault Helm Sidecar](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-sidecar)  tutorial.

The Vault web UI is available through a Kubernetes service.

Display the  `vault-ui`  service in the default namespace.
```
kubectl get service vault-ui
```
```
NAME TYPE CLUSTER-IP EXTERNAL-IP PORT(S) AGE 
vault-ui LoadBalancer 10.0.1.209 20.62.223.255 8200:32656/TCP 9m15s
```
The  `EXTERNAL-IP`  displays the IP address of the Vault UI. In this example output this address is  `20.62.223.255`.

1.  Launch a web browser, and enter the  _EXTERNAL-IP_  with the port  `8200`  in the address. For example:  `http://20.62.223.255:8200`.
    
2.  Enter  `5`  in the  **Key shares**  and  `3`  in the  **Key threshold**  text fields.

![image](https://user-images.githubusercontent.com/3519706/218095411-9415af05-79af-430f-8e92-eaf88014d514.png)


3.  Click  **Initialize**.
    
4.  When the root token and unseal key is presented, scroll down to the bottom and select  **Download keys**. Save the generated unseal keys file to your computer.

![image](https://user-images.githubusercontent.com/3519706/218095627-32d1851a-9d50-4105-a5e0-f6ef63ab4229.png)

5.  Click  **Continue to Unseal**  to proceed.
    
6.  Open the downloaded file.
    
    **Example key file:**
    
    ```json
    {
      "keys": [
        "ecfb4ef59f9a2570f856c471cd3b0580e2b7d99962d5c9af7a25b80138affe935a",
        "807e9bbfb984c631becc526c621c9852f82d88b2347f7398ef7af3c1fbfbbe9fd0",
        "561a7ff6b44b88f96a2d9faca1ae514d1557008ce19283dcfe2fb746ed4f0f7d94",
        "3671e9e817177d79d3c004e0745e5f1d1a5cbfcd9fd6ad22505d4bc538176fa3f9",
        "313fffc1c848276fffe1e3fcfce4d3472d104cda466227ca155e4f693cfbaa36b9"
      ],
      "keys_base64": [
        "7PtO9Z+aJXD4VsRxzTsFgOK32Zli1cmveiW4ATiv/pNa",
        "gH6bv7mExjG+zFJsYhyYUvgtiLI0f3OY73rzwfv7vp/Q",
        "Vhp/9rRLiPlqLZ+soa5RTRVXAIzhkoPc/i+3Ru1PD32U",
        "NnHp6BcXfXnTwATgdF5fHRpcv82f1q0iUF1LxTgXb6P5",
        "MT//wchIJ2//4eP8/OTTRy0QTNpGYifKFV5PaTz7qja5"
      ],
      "root_token": "s.p3L38qZwmnHUgIHR1MBmACfd"
    }
    
    ``` 
7.  Copy one of the  `keys`  (not  `keys_base64`) and enter it in the  **Master Key Portion**  field. Click  **Unseal**  to proceed.

![image](https://user-images.githubusercontent.com/3519706/218096077-ed2c419d-ca0c-4153-a867-ac08c5e150c7.png)

The Unseal status shows  `1/3 keys provided`.
    
8.  Enter another key and click  **Unseal**.
    
    The Unseal status shows  `2/3 keys provided`.
    
9.  Enter another key and click  **Unseal**.
    
    After 3 out of 5 unseal keys are entered, Vault is unsealed and is ready to operate.
    
10.  Copy the  `root_token`  and enter its value in the  **Token**  field. Click  **Sign In**.

![image](https://user-images.githubusercontent.com/3519706/218096290-8804426f-e518-4d3d-aba9-43d8e788d2fe.png)

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
Next, connect to Vault and configure a policy named “internal-app” for the demo. This is a very non-restrictive policy, and in a production setting, you would typically want to lock this down more, but it serves as an example while you play around with this feature.

```
vault policy write internal-app - <<EOF
path "internal/data/database/config"{
capabilities = ["read"]
}
EOF
```
Next, we want to configure the  [Vault Kubernetes Auth](https://www.vaultproject.io/docs/auth/kubernetes.html)  method and attach our newly recreated policy to our applications service account (we’ll create the application in just a minute).

```
vault auth enable kubernetes

vault write auth/kubernetes/config \
   token-reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
   kubernetes_host=https://${KUBERNETES_PORT_443_TCP_ADDR}:443 \
   kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

vault write auth/kubernetes/role/internal-app \
   bound_service_account_names=internal-app \
   bound_service_account_namespaces=demo\
   policies=internal-app \
   ttl=1h
```
Finally, let's create an example username and password in Vault using the KV Secrets Engine. The end goal here, is for this username and password to be injecting into our target pod's filesystem, which knows nothing about Vault.
```
vault kv put internal/database/config username="oktay" password="savdi"
```

Here is an example `app.yaml` configuration file for running a demo application. This spawns a simple web service container useful for our testing purposes. We are also defining a Service Account which we can then tie back to the Vault Policy we created earlier. This allows you to specify each secret an application is allowed to access.
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
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "internal-app"
        vault.hashicorp.com/agent-inject-secret-helloworld: "internal/database/config"
        #vault.hashicorp.com/agent-inject-secret-credentials.txt: "internal/data/database/config" 
        vault.hashicorp.com/agent-inject-template-helloworld: |
          {{- with secret "internal/data/database/config" -}}
          postgresql://{{ .Data.data.username }}:{{ .Data.data.password }}@postgres:5432/wizard
          {{- end }}
      labels:
        app: vault-agent-demo
    spec:
      serviceAccountName: internal-app
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
resource1 - https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-azure-aks#install-the-vault-helm-chart

resource2 - https://www.hashicorp.com/blog/injecting-vault-secrets-into-kubernetes-pods-via-a-sidecar

