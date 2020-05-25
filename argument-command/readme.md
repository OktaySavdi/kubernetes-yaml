# Kubernetes argument-command example

```yaml
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