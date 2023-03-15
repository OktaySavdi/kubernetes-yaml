## Set a secret in Vault

The web application that you deploy in the  [Deploy web application](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-azure-aks#deploy-web-application)  step, expects Vault to store a username and password at the path  `secret/webapp/config`. To create this secret requires you to enable the  [key-value secret engine](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2), and store a secret username and password at that defined path.

1.  Select the  **Secrets**  tab in the Vault UI.
    
2.  Under  **Secrets Engines**, select  **Enable new engine**.

![image](https://user-images.githubusercontent.com/3519706/218127355-3b23354e-e06d-4a02-93a3-c37ce300ab5b.png)

3. Under **Enable a Secrets Engine**, select **KV** and **Next**.

![image](https://user-images.githubusercontent.com/3519706/218127422-551253e0-85ea-4f9b-a930-dcc07235825b.png)

4.  Enter  `secret`  in the  **Path**  text field.
    
5.  Select  **Enable Engine**.

![image](https://user-images.githubusercontent.com/3519706/218127522-ef76e0cc-c2ef-4984-9ac5-efee96a26d05.png)

The view changes to display all the secrets for this secrets engine.
    
6.  Select the  **Create secret**  action.

![image](https://user-images.githubusercontent.com/3519706/218127828-9939384b-3117-4278-b2cc-20c3c190b949.png)

7.  Enter  `devwebapp/config`  in the  **Path for this secret**.
    
8.  Under  **Version data**, enter  `username`  in the  **key**  field and  `giraffe`  in the  **value**  field.
    
9.  Select  **Add**  to create another key and value field in  **Version data**.
    
10.  Enter  `password`  in the  **key**  field and  `salsa`  in the  **value**  field.

![image](https://user-images.githubusercontent.com/3519706/218127944-79751e7f-42ab-401f-a88f-317d4b5923c3.png)

11.  Select  **Save**  to create the secret.
    
    The view displays the contents of the newly created secret.
    
You successfully created the secret for the web application.


## Configure Kubernetes authentication

The initial  [root token](https://developer.hashicorp.com/vault/docs/concepts/tokens#root-tokens)  is a privileged user that can perform any operation at any path. The web application only requires the ability to read secrets defined at a single path. This application should authenticate and be granted a token with limited access.

**Best practice:**  We recommend that  [root tokens](https://developer.hashicorp.com/vault/docs/concepts/tokens#root-tokens)  are used only for initial setup of an authentication method and policies. Afterwards they should be revoked. This tutorial does not show you how to revoke the root token.

Vault provides a  [Kubernetes authentication](https://developer.hashicorp.com/vault/docs/auth/kubernetes)  method that enables clients to authenticate with a Kubernetes Service Account Token.

1.  Select the  **Access**  tab in the Vault UI.

![image](https://user-images.githubusercontent.com/3519706/218128097-c5e0b29f-e002-423f-aad7-08899a30baa2.png)

The view displays all the authentication methods that are enabled.
    
2.  Under  **Authentication Methods**, select  **Enable new method**.

![image](https://user-images.githubusercontent.com/3519706/218128182-0d3fb522-1252-4f1a-a05a-aed98a4f1f1c.png)

3.  Under  **Enable an Authentication Method**, select  **Kubernetes**  and  **Next**.
    
    The view displays the method options configuration for the authentication method.
    
4.  Select  **Enable Method**  to create this authentication method with the default method options configuration.

![image](https://user-images.githubusercontent.com/3519706/218128264-e83cc4c5-72c9-4c4d-b5f9-ec34c5a250b5.png)

The view displays the configuration settings that enable the auth method to communicate with the Kubernetes cluster. The **Kubernetes host**, **CA Certificate**, and **Token Reviewer JWT** require configuration. These values are defined on the `vault-0` pod.

![image](https://user-images.githubusercontent.com/3519706/218128314-d6278c76-7cfe-413e-8d3c-1b02336fbb3f.png)

5. Enter the address returned from the following command in  **Kubernetes host**  field.

```shell-session
$ echo "https://$( kubectl exec vault-0 -- env | grep KUBERNETES_PORT_443_TCP_ADDR| cut -f2 -d'='):443"
https://10.0.0.1:443

```
The command displays the environment variables defined on the node, filters to only the  `KUBERNETES_PORT_443_TCP_ADDR`  address and then prefixes the  `https://`  protocol and appends the  `443`  port.

![image](https://user-images.githubusercontent.com/3519706/218128408-9a1d5e1e-7562-4979-a481-cc898e697554.png)

6.  For the  **Kubernetes CA Certificate**  field, toggle the  **Enter as text**.
    
7.  Enter the certificate returned from the following command in  **Kubernetes CA Certificate**  entered as text.

```shell-session
$ kubectl exec vault-0 -- cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
-----BEGIN CERTIFICATE-----
MIIEyjCCArKgAwIBAgIRAI20oNPOAqRDhNnOzHjtkAYwDQYJKoZIhvcNAQELBQAw
DTELMAkGA1UEAxMCY2EwIBcNMjAxMjE0MjAwNTM0WhgPMjA1MDEyMTQyMDE1MzRa
MA0xCzAJBgNVBAMTAmNhMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA
sScrgikc12Tif7Py+8cbyuQ82D+D14734JkJuf1Z5pMHJEJzXydjRDKpf1ut+yO0
IdZMrn4fjyRe8qrzjpH6pOD2WdSqZlzb23XIRV1byVqsWwir77I6p6KO6DNPyAcN
YQ92W9SDlwKHUoyByJxwOTIwcobpZcentUVd9ld4ExA5uFXu7VzKfxVOmHW0m1aO
xgOKZEZJrPnWpZBMHK14Cqq1yxV5LxZEF3xfb6ONYnXsY+IgddEkSDgiUxTkkDZv
5wYLiWIY/DhfJvlFDH1c7nYfIbukpmzOKqempKI/aWvJxgtHKYnW7ydvdPkv2dMv
nAH5puNrsdKXN2HNfdytZGX9tpQIssRpgOCgjKV0+9liyE2MJ1/vmndlKomamC1L
GD7LrRPUlf0hlXXTIgMAXaUtNjaS4KT37mZI9Z5yUZUH5Unfu19WDsRvYp4ZuYqC
zEvTy06aJ5maUYmdobK0fIbpHr5Vbiu3J54Co7w1EJvZlwM91D6VhlzkodsKI4Jn
+WEmZSewvUgTCJDPWgHhgahsl9ZuOW47M9ZQkR/HXKtqm4iygNcPX2eN1LlZpFrG
D213WFmW6g5P6j0wILaZxfk9ufEsPmh5dptx1WGSgtJ0yfwNlvwhRBrJFuksKMpX
ZziT/ALbDe7hPnkxGZcyEJCjXCqkfQphbIT1FJpNjlsCAwEAAaMjMCEwDgYDVR0P
AQH/BAQDAgKkMA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggIBABWJ
wCW4i/S4DJ+othnoDyy30rSxkKl4RIczJ+/TFL6iqDcK4bElasxxWCgXV15fDpH4
z6dI5Ic5jyu+pK/7cwY3C1Y3uZq8e/8/+4Q1UJs5xRb7BPAQLlHlHF74Z4Ho3THn
uHjfN2k/V+atQEZiZ5CCvtR3tvVCGV3iO9i21pVvA+ypt61qGlXGt1ENoxZJX8ts
j8kBo+Ud1lwiWblV1Ba6yses7lYCX/GAiK75uvuKGW51m6oU6ItvXie3og6YDW7Y
05YhqJYhQnbYV4tTAjBmuR1S4BeQUJBkArbwHnMxsSwUSHPFSIj+VrjexS+K0H9g
vx2bXrQILivGxmysjJlA0YwcTLLDhjX6hlW1AR1fVWOt8odTGZ5Vk24bqWBw3fY1
W68Gm230L5T4fdb0CwLKeowbIBraYD6z/E9L3pJCA8ZUYPWeWdZm55ZKqp5M8A8f
0QLn15Vbb57EKLhPndBJlgomLuaIHD1K9je3lhlWYeoJjDvKGq6Jjw8OAThRNsBp
RRx/X5HD2pLACpgLlcqjTcsSa+wdI5lFGrR7uubt+z8igsmJT5pP1jL5AFrzHqOQ
WAm4ifPDF1bAgUhJMhvPL5B2JJPYjwlKZ4qbrLLDifg3KNBJ9D0B9tldWTw1oD3p
UTZbPZUwkIFK9UygG8na5fZFqQG+8sCjOF2hXfou
-----END CERTIFICATE-----
```
![image](https://user-images.githubusercontent.com/3519706/218128703-05f19503-7e5c-4fa7-af54-bf2b4901b441.png)

8.  Expand the  **Kubernetes Options**  section.
    
9.  Enter the token returned from the following command in  **Token Reviewer JWT**  field.
    
```shell-session
    $ echo $(kubectl exec vault-0 -- cat /var/run/secrets/kubernetes.io/serviceaccount/token)
    eyJhbGciOiJSUzI1NiIsImtpZCI6ImdFUjRkcWlValh5SXJ2Q3NvO ... snipped ...
    
```
The command displays the JSON Web Token (JWT) mounted by Kubernetes on the  `vault-0`  pod.

![image](https://user-images.githubusercontent.com/3519706/218128854-b9e0ceb9-e203-4a69-ba28-0a1fc42ffc75.png)

10.  Select  **Save**.
    
The Kubernetes authentication method is configured to work within the cluster. The web application requires a Vault policy to read the secret and a Kubernetes role to grant it that policy.

## Configure web application authentication

For a client of the Vault server to read the secret data defined in the  [Set a secret in Vault](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-azure-aks#set-a-secret-in-vault)  step requires that the read capability be granted for the path  `secret/data/devwebapp/config`.

1.  Select the  **Policies**  tab in the Vault UI.
    
2.  Under  **ACL Policies**, select the  **Create ACL policy**  action.

![image](https://user-images.githubusercontent.com/3519706/218129045-d8bf8de3-0149-48a6-8ab8-5a5df13435b4.png)

3.  Enter  `devwebapp`  in the  **Name**  field.
    
4.  Enter this policy in the  **Policy**  field.

```hcl
# Read the configuration secret
path "secret/data/devwebapp/config" {
  capabilities = ["read"]
}
```
![image](https://user-images.githubusercontent.com/3519706/218129500-6af95b3f-4b67-47e5-b343-2a49d1ae1742.png)

5. Select  **Create policy**.

The policy is created and the view displays its name and contents.

![image](https://user-images.githubusercontent.com/3519706/218129603-a1a2f999-90f4-4698-9020-30e811743646.png)

The policy is assigned to the web application through a Kubernetes role. This role also defines the Kubernetes service account and Kubernetes namespace that is allowed to authenticate.
    
6.  Select the  **Access**  tab in the Vault UI.
    
7.  Under  **Authentication Methods**, click the  **...**  for the  **kubernetes/**  auth method. Select  **View configuration**.

![image](https://user-images.githubusercontent.com/3519706/218129722-2eb975f5-5eea-45dc-9a9a-dd7951f2f460.png)


8.  Under the  **kubernetes**  method, choose the  **Roles**  tab.
    
    This view displays all the roles defined for this authentication method.
    
9.  Select  **Create role**.

![image](https://user-images.githubusercontent.com/3519706/218129806-dbd21020-7a69-4940-9be0-7a3eb0f68cb4.png)

10.  Enter  `devweb-app`  in the  **Name**  field.
    
11.  Enter  `internal-app`  in the  **Bound service account names**  field.
    
    This field contains one or more Kubernetes service accounts that this role supports. This Kubernetes service account is created in the  [Deploy web application](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-azure-aks#deploy-web-application)  step.
    
12.  Enter  `default`  in the  **Bound service account namespaces**  field and select  **Add**.
    
    This field contains one or Kubernetes namespaces that this role supports.

![image](https://user-images.githubusercontent.com/3519706/218129916-5bde2e6b-283f-446b-abd5-2be07ff90198.png)

13.  Expand the  **Tokens**  section.
    
14.  Enter  `devwebapp`  in the  **Generated Token's Policies**.

![image](https://user-images.githubusercontent.com/3519706/218130018-a3dced10-c359-4a40-b94f-b7a191b52359.png)

15. Select Save.

The role is created and the view displays its name in the roles view for this authentication method.

## Deploy web application

The web application pod requires the creation of the  `internal-app`  Kubernetes service account specified in the Vault Kubernetes authentication role created in the  [Configure Kubernetes authentication](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-azure-aks#configure-kubernetes-authentication)  step.

Define a Kubernetes service account named  `internal-app`.

```shell-session
cat > internal-app.yaml <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: internal-app
EOF
```
Create the  `internal-app`  service account.
```shell-session
kubectl apply --filename internal-app.yaml
```
Define a pod named  `devwebapp`  with the web application.
```shell-session
cat > devwebapp.yaml <<EOF
---
apiVersion: v1
kind: Pod
metadata:
  name: devwebapp
  labels:
    app: devwebapp
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "devweb-app"
    vault.hashicorp.com/agent-inject-secret-credentials.txt: "secret/data/devwebapp/config"
spec:
  serviceAccountName: internal-app
  containers:
    - name: devwebapp
      image: jweissig/app:0.0.1
EOF
```
This definition creates a pod with the specified container running with the  `internal-app`  Kubernetes service account. The container within the pod is unaware of the Vault cluster. The Vault Injector service reads the  [annotations](https://developer.hashicorp.com/vault/docs/platform/k8s/injector#annotations)  to find the secret path, stored within Vault at  `secret/data/devwebapp/config`  and the file location,  `/vault/secrets/secret-credentials.txt`, to mount that secret with the pod.

**Learn more:**  For more information about annotations refer to the  [Injecting Secrets into Kubernetes Pods via Vault Agent Injector](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-sidecar)  tutorial.

Create the  `devwebapp`  pod.

```shell-session
kubectl apply --filename devwebapp.yaml
```
Get all the pods within the default namespace.
```shell-session
kubectl get pods
devwebapp                               2/2     Running   0          6s
vault-0                                 1/1     Running   0          8m48s
vault-agent-injector-56bf46695f-gdpsz   1/1     Running   0          8m48s
```
Wait until the  `devwebapp`  pod reports that is running and ready (`2/2`).

Display the secrets written to the file  `/vault/secrets/secret-credentials.txt`  on the  `devwebapp`  pod.
```shell-session
kubectl exec --stdin=true --tty=true devwebapp --container=devwebapp \
    -- cat /vault/secrets/credentials.txt
```
**Example output:**
```undefined
data: map[password:salsa username:giraffe]
metadata: map[created_time:2020-12-11T19:14:05.170436863Z deletion_time: destroyed:false version:1]
```

The result displays the unformatted secret data present on the container.

