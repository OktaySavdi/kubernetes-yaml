# Kubernetes node selector example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test
  labels:
    mylabels: mysamplelable
spec:
  containers:
    - name: myPodName
      image: nginx
  nodeSelector:
    size: Large
```