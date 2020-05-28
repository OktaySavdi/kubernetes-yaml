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
#ConfigMap Env
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
        - configMapRef:
            name: app-config
            
---
#ConfigMap Mount
---
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
    - name: test
      image: busybox
      volumeMounts:
        - name: config-vol
          mountPath: /etc/config
  volumes:
    - name: config-vol
      configMap:
        name: mysql-config-map

#ConfigMap Data
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-cluster-configmap
data:
  redis.conf: |-
    cluster-enabled yes
    cluster-require-full-coverage no
    cluster-node-timeout 15000
    cluster-config-file /data/nodes.conf
    cluster-migration-barrier 1
    appendonly yes
    protected-mode no
```
