# kubernetes readinessProbe example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: readiness-pod
spec:
  containers:
    - name: nginx
      image: nginx
      ports:
        - containerPort: 8080
      readinessProbe:
        httpGet:
          port: 8080
          path: /app/ready
        tcpSocket:
          port: 3306
        exec:
          command:
            - cat
            - /app/is_ready
        initialDelaySeconds: 10
        periodSeconds: 5
        failureThreshold: 8

---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: chat
  name: chat
spec:  
  replicas: 1
  selector:
    matchLabels:
      app: chat
  template:
    metadata:
      labels:
        app: chat
    spec:
      containers:
      - image: quay.io/oktaysavdi/chat #Code Repo https://github.com/OktaySavdi/chat_example
        imagePullPolicy: IfNotPresent
        name: chat
        livenessProbe:
          httpGet:
            path: /chat/health
            port: 80
            scheme: HTTP
          initialDelaySeconds: 5
          timeoutSeconds: 30
          periodSeconds: 10
          successThreshold: 1
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /chat/health
            port: 80
            scheme: HTTP
          initialDelaySeconds: 5
          timeoutSeconds: 30
          periodSeconds: 10
          successThreshold: 1
          failureThreshold: 3
        terminationMessagePath: /dev/termination-log        
```