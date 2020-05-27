# Kubernetes persistence volume claim example

```yaml
---
# Dynamic provision

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-example
  labels:
    app: nginx
spec:
  storageClassName: rook-ceph-block
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi

---
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
    - name: myfrontend
      image: nginx
      volumeMounts:
        - mountPath: "/var/www/html"
          name: mypd
  volumes:
    - name: mypd
      persistentVolumeClaim:
        claimName: pvc-example

---
# Manuel PV-PVC

---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nginx-persistentvolume
  labels:
    type: local
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/opt"
    
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nginx-persistentvolumeclaim
spec:
  accessModes:
      - ReadWriteOnce
  resources:
      requests:
        storage: 1Gi

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
    - name: nginx-persistentvolume
      mountPath: "/usr/share/nginx/html/modules"
      subPath: modules
    - name: nginx-persistentvolume
      mountPath: "/usr/share/nginx/html"
  volumes:
    - name: nginx-persistentvolume
      persistentVolumeClaim:
        claimName: nginx-persistentvolumeclaim
```
