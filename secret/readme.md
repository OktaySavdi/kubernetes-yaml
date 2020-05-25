# Kubernetes secret example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  username: <username>
  password: <password>

#Secret ENV
---
apiVersion: v1
kind: Pod
metadata:
  name: webapp-green
spec:
  containers:
    - name: webapp-green
      image: webapp-color:v1
      ports:
        - containerPort: 8080
      envFrom:
        - secretRef:
            name: mysecret

#Secret Mount
---
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
    - name: test
      image: busybox
      volumeMounts:
        - name: config-vol
          mountPath: /etc/config
  volumes:
    - name: config-vol
      secret:
        secretName: mysecret
```