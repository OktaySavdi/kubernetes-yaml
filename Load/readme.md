```yaml
cat << EOF | oc create -f -
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
