# Kubernetes CRD example

```yaml
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: appconfigs.stable.example.com
spec:
  group: stable.example.com
  version: v1
  scope: Namespaced
  names:
    plural: appconfigs
    singular: appconfig
    kind: AppConfig
    shortNames:
    - ac
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1 
metadata:
  name: apconfig-admin-düzenlenme 
  labels:
    rbac.authorization.k8s.io/aggregate-to-admin: "true" 
    rbac.authorization.k8s.io/aggregate-to-edit: "true" 
rules:
- apiGroups: ["stable.example.com"] 
  resources: ["appconfigs"] 
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete", "deletecollection"] 
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: apconfig-admin-görüntülenme
  labels:
    rbac.authorization.k8s.io/aggregate-to-view: "true" 
    rbac.authorization.k8s.io/aggregate-to-cluster-reader: "true" 
rules:
- apiGroups: ["stable.example.com"] 
  resources: ["appconfigs"] 
  verbs: ["get", "list", "watch"]

---
apiVersion: stable.example.com/v1
kind: AppConfig
metadata:
  labels:
    name: nginx
  name: nginx
spec:
  template:
    metadata:
      labels:
        name: nginx
    spec:
      containers:
        image: nginx
        name: nginx
```