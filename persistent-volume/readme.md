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
```
