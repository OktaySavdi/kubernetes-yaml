# Kubernetes strategies example

```yaml
#Recreate
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rolling-update
  labels:
    app: nginx
spec:
  replicas: 4
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: frontent
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: nginx
          image: nginx

#Rolling Deployment
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rolling-update
  labels:
    app: nginx
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
  selector:
    matchLabels:
      app: frontent
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: nginx
          image: nginx
```
