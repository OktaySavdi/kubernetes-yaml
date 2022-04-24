
### Configure the Admission Controller

1.  Edit the  `admission-control.conf`  file:
    
    ```bash
    vi /etc/kubernetes/policywebhook/admission_config.conf
    ```
    
2.  Paste in the ImagePolicyWebhook:
    
    ```yaml
    apiVersion: apiserver.config.k8s.io/v1
    kind: AdmissionConfiguration
    plugins:
    - name: ImagePolicyWebhook
      configuration:
        imagePolicy:
          kubeConfigFile: /etc/kubernetes/policywebhook/kubeconf
          allowTTL: 50
          denyTTL: 50
          retryBackoff: 500
          defaultAllow: false
    ```
    
3.  To save and exit the file, press  **Escape**, type  `:wq`, and hit  **Enter**.
    

### Edit the Admission Controller's kubeconfig to Point to the Backend Webhook

> **Note:**  Certificates are already set up in the kubeconfig, and the API server is already set up to be able to locate these certificate files.

1.  Edit the kubeconfig file:
    
```bash
vi /etc/kubernetes/policywebhook/kubeconf
```
```yaml
apiVersion: v1
kind: Config
clusters:
- name: trivy-k8s-webhook
  cluster:
    certificate-authority: /etc/kubernetes/policywebhook/imagepolicywebhook-ca.crt # CA for verifying the remote service.
    server: "https://acg.trivy.k8s.webhook:8090/scan"                              # URL of remote service to query. Must use 'https'.
contexts:
- name: trivy-k8s-webhook
  context:
    cluster: trivy-k8s-webhook
    user: api-server
current-context: trivy-k8s-webhook
preferences: {}
users:
- name: api-server
  user:
    client-certificate: /etc/kubernetes/policywebhook/api-server-client.crt      # cert for the webhook admission controller to use
    client-key: /etc/kubernetes/policywebhook/api-server-client.key              # key matching the cert
```
    
2.  Set the location of the backend image scanning service:
    
    ```bash
    server: https://acg.trivy.k8s.webhook:8090/scan
    ```
    
3.  To save and exit the file, press  **Escape**, type  `:wq`, and hit  **Enter**.
    

### Enable Any Necessary Admission Control Plugins

1.  Edit the kube-apiserver manifest:
    
    ```bash
    vi /etc/kubernetes/manifests/kube-apiserver.yaml
    ```
    
2.  In the  `command`  container, scroll down to  `--enable-admission-plugins`  and add  `ImagePolicyWebhook` neccesary configure:
    
    ```
    spec:
      containers:
      - command:
        - kube-apiserver
        - --enable-admission-plugins=NodeRestriction,ImagePolicyWebhook
        - --admission-control-config-file=/etc/kubernetes/policywebhook/admission_config.conf
    ---
    volumeMounts:
    - mountPath: /etc/kubernetes/policywebhook
      name: policywebhook
      readyOnly: true
    ---
    volumes:
    - hostPath:
        path: /etc/kubernetes/policywebhook
        type: DirectoryOrCreate
      name: policywebhook
    ```
    
3.  To save and exit the file, press  **Escape**, type  `:wq`, and hit  **Enter**.
    
4.  Once the kube-apiserver has been re-created, create the  `good-pod`  Pod:
    
    ```
    kubectl create -f good-pod.yml
    ```
```yaml
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: Pod
metadata:
  name: good-pod
spec:
  restartPolicy: Never
  containers:
  - name: busybox
    image: busybox:1.33.1
EOF
```
    The Pod should be successfully created.
    
5.  Attempt to create the  `bad-pod`  Pod:
    
    ```
    kubectl create -f bad-pod.yml
    ```

```yaml
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: Pod
metadata:
  name: bad-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.14.2
EOF
```
    
    Pod creation should fail and return an error due to image vulnerabilities.
