# Kubernetes CronJob Example

```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: reporting-cron-job
spec:
  jobTemplate:
    spec:
      completions: 3
      parallelism: 3
      template:
        spec:
          containers:
            - name: reporting-tool
              image: reporting-tool
          restartPolicy: Never
  schedule: "*/1 * * * *"

---
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: hello-world
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - command: ["echo", "Hello-World","Runned"]
            image: alpine
            name: hello-world-deneme
          restartPolicy: OnFailure

---
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: hello-world
spec:
  suspend: false
  concurrencyPolicy: Allow
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - command: ['sh', '-c', 'echo POD Running ; sleep 90']
            image: alpine
            name: hello-world-deneme
          restartPolicy: OnFailure
```
