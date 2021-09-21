
### Enable the Use of PodSecurityPolicies in the Cluster

1.  Become the root user:
    
    ```
    sudo -i
    ```
    
2.  Edit the manifest file for the Kube API server:
    
    ```
    sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
    ```
    
3.  Under the  `command`  section in the YAML file, modify the  `--enable-admission-plugins`  flag to read:
    
    ```
    - --enable-admission-plugins=NodeRestriction,PodSecurityPolicy
    ```
    
4.  Save and exit the file by pressing the Escape key and entering:
    
    ```
    :wq
    ```
    
5.  Ensure the files are working correctly. This may take a few tries before results appear:
    
    ```
    kubectl get nodes
    ```
    

### Create a PodSecurityPolicy to Allow Only Non-Privileged Pods

1.  Create the  `psp-no-privileged.yml`  file:
    
    ```
    vi psp-no-privileged.yml
    ```
    
2.  Add in the YAML for the file:
    
    ```yaml
    apiVersion: policy/v1beta1
    kind: PodSecurityPolicy
    metadata:
      name: psp-no-privileged
    spec:
      privileged: false
      runAsUser:
        rule: MustRunAsNonRoot
      fsGroup:
        rule: RunAsAny
      seLinux:
        rule: RunAsAny
      supplementalGroups:
        rule: RunAsAny
      volumes:
      - configMap
      - downwardAPI
      - emptyDir
      - persistentVolumeClaim
      - secret
      - projected
    ```
    
3.  Save and exit the file by pressing the Escape key and entering:
    
    ```
    :wq
    ```
    
4.  Create a PodSecurityPolicy:
    
    ```
    kubectl create -f psp-no-privileged.yml
    ```
    

### Create an RBAC Setup to Apply the PodSecurityPolicy in the auth Namespace

1.  Create a new cluster role file:
    
    ```
    vi cr-use-psp-no-privileged.yml
    ```
    
2.  Add in the YAML for the cluster role:
    
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRole
    metadata:
      name: cr-use-psp-no-privileged
    rules:
    - apiGroups: ['policy']
      resources: ['podsecuritypolicies']
      verbs:     ['use']
      resourceNames:
      - psp-no-privileged
    ```
    
3.  Save and exit the file by pressing the Escape key and entering:
    
    ```
    :wq
    ```
    
4.  Create the cluster role:
    
    ```
    kubectl create -f cr-use-psp-no-privileged.yml
    ```
    
5.  Create a role binding to bind that cluster role to the service account:
    
    ```
    vi rb-auth-sa-psp.yml
    ```
    
6.  Add in the YAML for the role binding:
    
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: RoleBinding
    metadata:
      name: rb-auth-sa-psp
      namespace: auth
    roleRef:
      kind: ClusterRole
      name: cr-use-psp-no-privileged
      apiGroup: rbac.authorization.k8s.io
    subjects:
    - kind: ServiceAccount
      name: auth-sa
      namespace: auth
    ```
    
7.  Save and exit the file by pressing the Escape key and entering:
    
    ```
    :wq
    ```
    
8.  Create the role binding:
    
    ```
    kubectl create -f rb-auth-sa-psp.yml
    ```
    
9.  View the  `non-privileged-pod.yml`:
    
    ```
    cat non-privileged-pod.yml
    ```
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: non-privileged-pod
  namespace: auth
spec:
  containers:
  - name: background-monitor
    image: radial/busyboxplus:curl
    command: ['sh', '-c', 'while true; do echo "Running..."; sleep 5; done']
```    
10.  Create the  `non-privileged-pod.yml`  pod:
    
    kubectl create -f non-privileged-yml
    
    
11.  Look at the pod's contents:
    
    cat privileged-pod.yml
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
  namespace: auth
spec:
  containers:
  - name: background-monitor
    image: radial/busyboxplus:curl
    command: ['sh', '-c', 'while true; do echo "Running..."; sleep 5; done']
    securityContext:
      privileged: true
```
    
12.  Create the  `privileged-pod.yml`:
    
    kubectl create -f privileged-pod.yml
