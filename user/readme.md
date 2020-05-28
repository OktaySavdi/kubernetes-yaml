
# Kubernetes user example

**Create config file**
```bash
vi myconfig
```
```yaml
apiVersion: v1
kind: Config

clusters:
- name: kubernetes
  cluster:
    certificate-authority: /etc/kubernetes/pki/ca.crt
    server: https://172.17.0.78:6443

contexts:
- name: oktay@kubernetes
  context:
    cluster: kubernetes
    user: oktay

users:
- name: oktay
  user:
    client-certificate: /root/oktay.crt
    client-key: /root/oktay.key

current-context: oktay@kubernetes
```
**Create Role and RoleBinding**
```yaml
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
**Test config**
```ruby
kubectl get po -n development --kubeconfig=myconfig
```
```ruby
kubectl get pvc -n development --kubeconfig=myconfig
```
```ruby
kubectl get svc -n development --kubeconfig=myconfig
```