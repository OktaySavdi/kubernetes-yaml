# Kubernetes service example

```yaml
apiVersion: v1
kind: Service
metadata:
  name: back-end
spec:
  type: ClusterIp
  ports:
    - port: 80
      targetPort: 80
  selector:
    app: myapp
    type: back-end

---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30008
  selector:
    app: myapp
    type: front-end

---
apiVersion: v1
kind: Service
metadata:
  name: my-nginx
  labels:
    run: my-nginx
spec:
  type: NodePort
  ports:
  - port: 8080
    targetPort: 80
    protocol: TCP
    name: http
  - port: 443
    protocol: TCP
    name: https
  selector:
    run: my-nginx

---
kind: Service
apiVersion: v1
metadata:
  name: rabbitmq
  labels:
    run: rabbitmq
spec:
  selector:
    run: rabbitmq
  ports:
   - name: rabbitmq-mgmt-port
     protocol: TCP
     port: 15672
     targetPort: 15672
   - name: rabbitmq-amqp-port
     protocol: TCP
     port: 5672
     targetPort: 5672
```