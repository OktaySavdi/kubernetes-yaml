# Kubernetes network-policy example

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-policy
spec:
  podSelector:
    matchLabels:
      name: db
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              name: api-pod
      ports:
        - protocol: TCP
          port: 3306

---
#Only login label pod will be able to access the Mongodb port
kind: NetworkPolicy
apiVersion: extensions/v1beta1
metadata:
  name: allow-27107 
spec:
  podSelector: 
    matchLabels:
      app: mongodb #address to be visited
  ingress:
  - from:
    - podSelector: 
        matchLabels:
          app: login #outgoing address
    ports: 
    - protocol: TCP
      port: 27017 #port to go to
---
#db access is provided only through the mail pod
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-or-api-allow-app
  namespace: oktay
spec:
  podSelector:
    matchLabels:
      app: dotnet #outgoing address
  ingress:
    - from:
        - podSelector:
            matchLabels:
              web: nginx #outgoing address
---
#With login label, poda can be accessed via mynamespace namespace and test-pods pod
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: allow-pod-and-namespace-both
spec:
  podSelector:
    matchLabels:
      app: login
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            project: mynamespace
        podSelector:
          matchLabels:
            name: test-pods
---
#goes only on dotnet pod with monitoring pod over 80 and 443
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow-http-and-https
  namespace: oktay
spec:
  podSelector:
    matchLabels:
      app: dotnet #outgoing address
  ingress:
    - from:
        - podSelector:
            matchLabels:
              web: nginx #outgoing address
      ports:
        - protocol: TCP
          port: 80
        - protocol: TCP
          port: 443
---
#frontend label poda is only accessible on 80 and 443
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: allow-http-and-https
spec:
  podSelector:
    matchLabels:
      role: frontend
  ingress:
  - ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
---
#Same namespace pods see each other, pods in other projects cannot access
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: allow-same-namespace
spec:
  podSelector:
  ingress:
  - from:
    - podSelector: {}
---
#access from all environments for web application
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: web-allow-all
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
  - {}
---
#ALLOW traffic from external clients
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: web-allow-external
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
  - from: []
---
#Access from namespaces in all environments
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  namespace: secondary
  name: web-allow-all-namespaces
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
  - from:
    - namespaceSelector: {}
---
#Provides db access on a different Namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-db-allow-all-ns
  namespace: oktay
spec:
  podSelector:
    matchLabels:
      role: web-db
  ingress:
    - from:
        - namespaceSelector: {}
---
#db is only accessible from the production namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-allow-production
  namespace: oktay
spec:
  podSelector:
    matchLabels:
      app: db
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              env: production
---
#ALLOW traffic from apps that use multiple selectors
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: redis-allow-services
spec:
  podSelector:
    matchLabels:
      app: bookstore
      role: db
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: login
    - podSelector:
        matchLabels:
          app: dotnet
    - podSelector:
        matchLabels:
          web: nginx
#------------------------DENY------------------------------------
---
#Prevention of access via a specific port via namespace and pod
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: redis-deny
  namespace: oktay
spec:
  podSelector:
    matchLabels:
      app: redis #pod we do not want access
  ingress:
    - from:
        - namespaceSelector: #accessible through this namespace
            matchLabels:
              project: eclipse-che
        - podSelector:   #accessible via this pod
            matchLabels:
              app: codeready #pod label to go
      ports:
        - protocol: TCP
          port: 6379 #access denied port
---
#blocks all requests from outside
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: web-deny-all
  namespace: oktay
spec:
  podSelector:
    matchLabels:
      app: web
  ingress: []
---
#Access between pods is blocked in all environments
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: default-deny-all
  namespace: oktay
spec:
  podSelector: {}
  ingress: []
---
#egress traffic access is not allowed
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: foo-deny-egress
spec:
  podSelector:
    matchLabels:
      app: foo
  policyTypes:
  - Egress
  egress: []
---
#egress blocks all outgoing access
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: default-deny-all-egress
  namespace: default
spec:
  policyTypes:
  - Egress
  podSelector: {}
  egress: []
```
