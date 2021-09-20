
### Install gVisor and Create a containerd Sandbox Configuration

> **Note:**  Perform the following steps on both the control plane and worker node.

1.  Install gVisor:
    
    ```bash
    curl -fsSL https://gvisor.dev/archive.key | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64,arm64] https://storage.googleapis.com/gvisor/releases release main"
    
    sudo apt-get update && sudo apt-get install -y runsc
    ```
    
2.  Edit the containerd configuration file to add configuration for  `runsc`:
    
    ```bash
    sudo vi /etc/containerd/config.toml
    ```
    
3.  In the  `disabled_plugins`  section, add the  `restart`  plugin:
    
    ```bash
    disabled_plugins = ["io.containerd.internal.v1.restart"]
    ```
    
4.  Under  `[plugins]`, scroll down to  `[plugins."io.containerd.grpc.v1.cri".containerd.runtimes]`  and add the  `runsc`  runtime configuration:
    
    ```bash
    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
        runtime_type = "io.containerd.runc.v1"
        runtime_engine = ""
        runtime_root = ""
        privileged_without_host_devices = false
      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc]
        runtime_type = "io.containerd.runsc.v1"
    ```
    
5.  Scroll down to the  `[plugins."io.containerd.runtime.v1.linux"]`  block and set  `shim_debug`  to  `true`:
    
    ```bash
    [plugins."io.containerd.runtime.v1.linux"]
    
      ...
    
      shim_debug = true
    ```
    
6.  To save and exit, type  `:wq`  and press  **Enter**.
    
7.  Restart containerd:
    
    ```bash
    sudo systemctl restart containerd
    ```
    
8.  Verify that containerd is still running:
    
    ```bash
    sudo systemctl status containerd
    ```
    
9.  Close out of the worker node. The remainder of the lab will be completed using only the control plane node.
    

### Create a RuntimeClass for the Sandbox

1.  On the control plane node, create a RuntimeClass:
    
    ```bash
    vi runsc-sandbox.yml
    ```
    
2.  Paste in the following YAML:
    
    ```yaml
    apiVersion: node.k8s.io/v1
    kind: RuntimeClass
    metadata:
      name: runsc-sandbox
    handler: runsc
    ```
    
3.  Type  `:wq`  and press  **Enter**.
    
4.  Create the sandbox in the cluster:
    
    ```
    kubectl create -f runsc-sandbox.yml
    ```
    

### Move All Pods in the questionablesoft Namespace to the New Runtime Sandbox

1.  Retrieve the Pods in the  `questionablesoft`  namespace:
    
    ```
    kubectl get pods -n questionablesoft
    ```
    
2.  Delete the Pods:
    
    ```bash
    kubectl delete pod questionablesoft-api -n questionablesoft --force
    
    kubectl delete pod questionablesoft-data -n questionablesoft --force
    ```
    
3.  Edit the  `questionablesoft-api.yml`  manifest file:
    
    ```bash
    vi questionablesoft-api.yml
    ```
    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: questionablesoft-api
      namespace: questionablesoft
    spec:
      containers:
      - name: busybox
        image: busybox
        command: ['sh', '-c', 'while true; do echo "Running..."; sleep 5; done']
    ```
    
4.  Under  `spec`, add the  `runtimeClassName`  of  `runsc-sandbox`:
    
    ```yaml
    spec:
      runtimeClassName: runsc-sandbox
    ```
    
5.  Type  `:wq`  and press  **Enter**.
    
6.  Edit the  `questionablesoft-data.yml`  manifest file:
    
    ```bash
    vi questionablesoft-data.yml
    ```
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: questionablesoft-data
  namespace: questionablesoft
spec:
  containers:
  - name: busybox
    image: busybox
    command: ['sh', '-c', 'while true; do echo "Running..."; sleep 5; done']
```

7.  Add the  `runtimeClassName`  of  `runsc-sandbox`:
    
    ```yaml
    spec:
      runtimeClassName: runsc-sandbox
    ```
    
8.  Type  `:wq`  and press  **Enter**.
    
9.  Re-create the Pods:
    
 ```
kubectl create -f questionablesoft-api.yml
    
kubectl create -f questionablesoft-data.yml
```
    
10.  To verify the Pods are running, retrieve them from the  `questionablesoft`  namespace:
```     
kubectl get pods -n questionablesoft
```     
11.  To verify the Pods are running in a gVisor sandbox, check the Pods'  `dmesg`  output: 
```   
kubectl exec questionablesoft-api -n questionablesoft -- dmesg
    
kubectl exec questionablesoft-data -n questionablesoft -- dmesg
```
    
   The output begins with  `Starting gVisor...`, indicating the container process is running in a gVisor sandbox.
    
12.  Compare this output to the non-sandboxed Pod  `securicorp-api`  in the  `default`  namespace:
```    
kubectl exec securicorp-api -- dmesg
```    
   
   The output is running using the Linux host kernel directly and is much lengthier than the output received from the gVisor sandboxed Pods.
