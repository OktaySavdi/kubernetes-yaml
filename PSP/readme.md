Exclude namespace on pod security policy
```
kubectl create clusterrolebinding psprb --clusterrole=non-priv-role --user=jaya_vkl@yahoo.co.in
kubectl create clusterrolebinding psprbgrp --clusterrole=non-priv-role --group=system:authenticated
kubectl create clusterrolebinding psprbsa --clusterrole=non-priv-role --serviceaccount=default:<sa_name>
```
```yaml
cat <<EOF | kubectl create -f -
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: allow-argocd-psp
rules:
- apiGroups:
    - policy
  resourceNames:
    - vmware-system-privileged
    - vmware-system-tmc-agent-restricted
  resources:
    - podsecuritypolicies
  verbs:
    - use
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: allow-argocd-psp
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: allow-argocd-psp
subjects:
- kind: ServiceAccount
  name: argocd-server
  namespace: argocd
- kind: ServiceAccount
  name: argocd-redis
  namespace: argocd
- kind: ServiceAccount
  name: argocd-notifications-controller
  namespace: argocd
- kind: ServiceAccount
  name: argocd-dex-server
  namespace: argocd
- kind: ServiceAccount
  name: argocd-applicationset-controller
  namespace: argocd
---
EOF
```
```
kubectl get deploy --no-headers | awk '{print $1}' | xargs kubectl rollout restart deploy
```
