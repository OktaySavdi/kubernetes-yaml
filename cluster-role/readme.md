# Kubernetes clusterrole example

```ruby
kubectl create sa demo-sa
kubectl create clusterrole myrole --resource=persistencevolumes --verb=list
kubectl create clusterrolebinding myrole-binding --clusterrole=myrole --serviceaccount=default:demo-sa
```

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
 name: demo-sa

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: mypv-list-role
rules:
- apiGroups: [""]
  resources:
  - persistentvolumes
  - nodes
  - namespaces
  verbs: ["list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: mypv-list-role-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: mypv-list-role
subjects:
  - kind: ServiceAccount
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
 - name: alpine
   image: alpine:3.9
```
