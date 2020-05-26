# Kubernetes non-root example


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
```