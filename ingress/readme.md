# Kubernetes ingress example

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: kiali-ingress
spec:
  rules:
  - host: kiali-10-10-10-11.nip.io
    http:
      paths:
      - path: /
        backend:
          serviceName: kiali
          servicePort: 20001

---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: host-switch
spec:
  rules:
    - host: red.com
      http:
        paths:
          - backend:
              serviceName: red
              servicePort: 80
    - host: green.com
      http:
        paths:
          - backend:
              serviceName: green
              servicePort: 80

---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: url-switch
spec:
  rules:
    - http:
        paths:
          - path: /blue
            backend:
              serviceName: blue
              servicePort: 80
          - path: /red
            backend:
              serviceName: red
              servicePort: 80

---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: test-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - http:
        paths:
          - path: /pay
            backend:
              serviceName: pay-service
              servicePort: 8282

---
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: kibana
  annotations:
    nginx.org/ssl-services: "kibana-kb-http"
spec:
  tls:
  - hosts:
    - kibana.NODE.nip.io
    secretName: tls-k8s-kibana-ingress
  rules:
  - host: "kibana.nip.io"
    http:
      paths:
      - path: /
        backend:
          serviceName: kibana-kb-http
          servicePort: 5601

```
