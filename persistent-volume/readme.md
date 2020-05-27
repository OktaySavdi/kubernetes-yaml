# Kubernetes persistence volume example

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysqlvol
spec:
  storageClassName: manual
  capacity:
    storage: 10Gi #Size of the volume
  accessModes:
    - ReadWriteOnce #type of access
  hostPath:
    path: "/mnt/data" #host location
  persistentVolumeReclaimPolicy: Retain

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysqlvol
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
    app: myapp
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: nginx-pv
      mountPath: /var/www/html/modules
      subPath: modules
    - name: nginx-pv
      mountPath: /var/www/html/profiles
      subPath: profiles    
  volumes:
    - name: nginx-pv
      persistentVolumeClaim:
        claimName: mysqlvol
```
