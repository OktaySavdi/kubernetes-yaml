```yaml
cat << EOF | kubectl create -f -
---
apiVersion: batch/v1
kind: Job
metadata:
  generateName: maxscale
spec:
  template:
    spec:
      containers:
      - name: work
        image: busybox
        command: ["sleep",  "300"]
        resources:
          requests:
            memory: 500Mi
            cpu: 500m
      restartPolicy: Never
  backoffLimit: 4
  completions: 50
  parallelism: 50
EOF
```

### Disk Load

```yaml
cat << EOF | kubectl create -f -
---
# Create a test PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-storage-pvc
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
# Create a pod using the PVC
apiVersion: v1
kind: Pod
metadata:
  name: test-storage-pod
  namespace: default
spec:
  containers:
  - name: test
    image: busybox
    command: 
    - sh
    - -c
    - |
      # Fill the volume to ~92% to trigger WARNING alert
      dd if=/dev/zero of=/data/testfile bs=1M count=920 2>/dev/null || true
      echo "Created 920MB file to simulate 92% usage"
      df -h /data
      # Keep container running
      tail -f /dev/null
    volumeMounts:
    - name: storage
      mountPath: /data
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: test-storage-pvc
EOF
```

### Performans Load

```yaml
cat << EOF | kubectl create -f -
---
apiVersion: v1
kind: Pod
metadata:
  name: cpu-stress-test
  namespace: default
  labels:
    app: stress-test
spec:
  containers:
  - name: stress
    image: polinux/stress
    resources:
      requests:
        cpu: 1500m
        memory: 256Mi
      limits:
        cpu: 2000m
        memory: 512Mi
    command: ["stress"]
    args:
    - "--cpu"
    - "2"
    - "--timeout"
    - "300s"
    - "--verbose"
  restartPolicy: Never
EOF
```

### Quota Load

```yaml
cat << EOF | kubectl create -f -
---
# Create a test namespace with ResourceQuota
apiVersion: v1
kind: Namespace
metadata:
  name: quota-test-ns
  labels:
    purpose: testing

---
# Create ResourceQuota with low limits to trigger alerts
apiVersion: v1
kind: ResourceQuota
metadata:
  name: test-quota
  namespace: quota-test-ns
spec:
  hard:
    requests.cpu: "1"           # 1 core total
    requests.memory: 2Gi        # 2GB total
    limits.cpu: "2"             # 2 cores total
    limits.memory: 4Gi          # 4GB total
    count/pods: "10"            # Max 10 pods
    count/services: "5"         # Max 5 services

---
# Create a deployment that uses most of the quota (to trigger WARNING)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quota-consumer
  namespace: quota-test-ns
spec:
  replicas: 3
  selector:
    matchLabels:
      app: quota-test
  template:
    metadata:
      labels:
        app: quota-test
    spec:
      containers:
      - name: app
        image: nginx:alpine
        resources:
          requests:
            cpu: 250m          # 3 replicas * 250m = 750m (75% of 1000m quota)
            memory: 512Mi      # 3 replicas * 512Mi = 1536Mi (75% of 2048Mi quota)
          limits:
            cpu: 500m
            memory: 1Gi
EOF
```
