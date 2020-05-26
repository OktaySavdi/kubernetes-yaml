# Kubernetes securityContext example

```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: redis
  name: non-root-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  containers:
  - image: redis:alpine
    name: redis

---
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    mylabels: web-pod
spec:
  securityContext:
    runAsUser: 1001
  containers:
    - name: ubuntu
      image: ubuntu
      command: ["/bin/sh"]
      args: ["-c", "while true; do echo hello; sleep 10;done"]
      securityContext:
        runAsUser: 1002
        capabilities:
          add:
            - MAC_ADMIN
```