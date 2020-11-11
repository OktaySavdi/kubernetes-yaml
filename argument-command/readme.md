# Kubernetes argument-command example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: command
spec:
  containers:
    - name: beta
      image: busybox
      command:
      - sleep
      - "4800"

---
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    mylabels: web-pod
spec:
  containers:
    - name: ubuntu
      image: ubuntu
      command: ["/bin/sh"]
      args: ["-c", "while true; do echo hello; sleep 10;done"]

---
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    mylabels: web-pod
spec:
  containers:
    - name: nginx
      image: nginx
      command: ["/bin/sh"]
      args: ["-c", "while [ ! -f /opt/myfile ]; do sleep 10; done; ls -l /opt/myfile && /usr/local/s2i/run"]
      
 ---
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    mylabels: web-pod
spec:
  containers:
    - name: istio
      image: istio     
      command: ["/bin/bash", "-c"]
      args: ["until curl --head localhost:15000 ; do echo Waiting for Sidecar; sleep 3 ; done ; echo Sidecar available; ./startup.sh"]
```
