# Kubernetes pod example

```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: nginx
  name: nginx
spec:
  containers:
  - command:
    - sleep
    - "1000"
    image: nginx
    name: nginx
    ports:
    - containerPort: 8080
    resources:
      limits:
        memory: 20Mi
      requests:
        memory: 15Mi
```