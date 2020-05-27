# Kubernetes environment example


```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: alpha
      image: nginx
      env:
      - name: name
        value: alpha
      - name: user
        value: "oktay"

---
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
    - name: test
      image: mysql
      env:
        - name: MYSQL_DATABASE
          valueFrom:
            secretKeyRef:
              name: mysql-mysql-secret
              key: MYSQL_DATABASE
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-mysql-secret
              key: MYSQL_ROOT_PASSWORD
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: mysql-mysql-secret
              key: MYSQL_USER 
```
