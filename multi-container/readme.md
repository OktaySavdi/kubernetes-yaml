# Kubernetes multi-container example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: yellow
spec:
  containers:
    - name: lemon
      image: busybox
    - name: gold
      image: redis
```