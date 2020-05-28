# Kubernetes role example

```yaml
# Service Account
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: read-pods
  namespace: default
subjects:
  - kind: ServiceAccount
    name: dashboard-sa # Name is case sensitive
    namespace: default
roleRef:
  kind: Role #this must be Role or ClusterRole
  name: pod-reader # this must match the name of the Role or ClusterRole you wish to bind to
  apiGroup: rbac.authorization.k8s.io

---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: default
  name: pod-reader
rules:
  - apiGroups:
      - ''
    resources:
      - pods
    verbs:
      - get
      - watch
      - list
# user
---
 kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: developer-rolebinding
  namespace: development
subjects:
  - kind: User
    name: oktay
    namespace: development
roleRef:
  kind: Role 
  name: developer-role
  apiGroup: rbac.authorization.k8s.io

---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: development
  name: developer-role
rules:
  - apiGroups:
      - ''
    resources:
      - persistentvolumeclaims
      - pods
      - services
    verbs:
      - '*'
```
