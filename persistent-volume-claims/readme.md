# Kubernetes persistence volume claim example

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nginx-persistentvolume
  labels:
    type: local
spec:
  capacity:
    storage: 10Gi
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
        storage: 500Mi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        volumeMounts:
        - name: nginx-persistentvolume
          mountPath: "/usr/share/nginx/html"
      volumes:
        - name: nginx-persistentvolume
          persistentVolumeClaim:
            claimName: nginx-persistentvolumeclaim
---
# Dynamic provision
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-deneme
  labels:
    app: nginx
spec:
  storageClassName: rook-ceph-block
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
      
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.15.4
        ports:
        - containerPort: 80
        volumeMounts:
          - name:  storage-pvc
            mountPath:  /opt/deneme
      volumes:
        - name:  storage-pvc
          persistentVolumeClaim:
            claimName: pvc-deneme

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
        claimName: myclaim
```
