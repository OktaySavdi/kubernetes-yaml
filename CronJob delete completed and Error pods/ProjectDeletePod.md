```yaml
kind: ServiceAccount
apiVersion: v1
metadata:
  name: clear-job
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: clear-failed-pods-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: clearpods-rb
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: clear-failed-pods-role
subjects:
- kind: ServiceAccount
  name: clear-job
  namespace: default
---
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: jobs-cleanup
  namespace: default
spec:
  schedule: '0 0 * * *'
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: clear-job
          containers:
          - name: kubectl-container
            image: bitnami/kubectl:latest
            # I'm using bitnami kubectl, because the suggested kubectl image didn't had the `field-selector` option
            command: ["sh", "-c", "kubectl get po | grep -E \"Completed|Error\" | awk '{print $1}' | xargs kubectl delete pod  --grace-period=0 --force"]
          restartPolicy: OnFailure
```
