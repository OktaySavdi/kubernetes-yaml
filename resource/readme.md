# Kubernetes resource example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-requirement-pod
spec:
  containers:
    - name: nginx
      image: nginx
      ports:
        - containerPort: 80
      resources:
        requests:
          memory: "1Gi"
          cpu: 1
        limits:
          memory: "2Gi"
          cpu: 2
```