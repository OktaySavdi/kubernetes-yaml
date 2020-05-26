# Kubernetes environment example


```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: alpha
      image: nginx
      env:
      - name: name
        value: alpha
      - name: user
        value: "oktay"
```