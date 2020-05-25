# Kubernetes job example

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: math-add-job
spec:
  parallelism: 3
  completions: 3
  template:
    spec:
      containers:
        - name: ubuntu
          image: ubuntu
          command:  ["expr", "3", "+", "2"]
      restartPolicy: never

---
apiVersion: batch/v1
kind: Job
metadata:
  labels:
    job-name: hello-world
  name: hello-world
spec:
  template:
    metadata:
      labels:
        job-name: hello-world
    spec:
      containers:
      - command: ["echo", "Hello-World","Runned"]
        image: alpine
        name: hello-world
      restartPolicy: OnFailure

---
apiVersion: batch/v1
kind: Job
metadata:
  labels:
    job-name: hello-world
  name: hello-world
spec:
  ttlSecondsAfterFinished: 60
  completions: 4
  parallelism: 2
  template:
    metadata:
      labels:
        job-name: hello-world
    spec:
      containers:
      - command: ["echo", "Hello-World","Runned"]
        image: alpine
        name: hello-world
      restartPolicy: OnFailure
```
