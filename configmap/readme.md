# Kubernetes Configmap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config-map
data:
  APP_COLOR: blue
  APP_MOD: prod
  port: 3306
  max_allowed_packet: 128M

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_COLOR: blue
  APP_MOD: prod
  port: 3306
  max_allowed_packet: 128M
  portRedis: 6379
  rdb-compression: yes

---
apiVersion: v1
kind: Pod
metadata:
  name: webapp-green
spec:
  containers:
    - name: webapp-green
      image: webapp-color:v1
      args:
        - "--color"
        - "green"
      ports:
        - containerPort: 8080
      envFrom:
        - configMapRef:
            name: app-config
```
