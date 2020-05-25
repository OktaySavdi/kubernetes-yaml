# Kubernetes service account example

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
 name: demo-sa

---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: Role
metadata:
 name: list-pods
rules:
 — apiGroups:
   — ''
 resources:
   — pods
 verbs:
   — list

---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: RoleBinding
metadata:
 name: list-pods_demo-sa
roleRef:
 kind: Role
 name: list-pods
 apiGroup: rbac.authorization.k8s.io
subjects:
 — kind: ServiceAccount
   name: demo-sa
   namespace: default

---
apiVersion: v1
kind: Pod
metadata:
 name: pod-demo-sa
spec:
 serviceAccountName: demo-sa
 containers:
 — name: alpine
   image: alpine:3.9
   command:
   — "sleep"
   — "10000"
```
