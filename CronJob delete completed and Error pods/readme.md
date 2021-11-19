```yaml
# 1. Create a service account

kind: ServiceAccount
apiVersion: v1
metadata:
  name: clear-job
  namespace: default

---

# 2. Create a role

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: clear-failed-pods-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list", "delete"]

---

# 3. Attach the role to the service account

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

# 4. Create a cronjob (with a crontab schedule) using the service account to check for completed jobs

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
            command: ["sh", "-c", "kubectl get pod -A --no-headers | grep -v kube-system | awk '{if ($4==\"Error\" || $4==\"Completed\") print \"kubectl delete pod \" $2 \" -n \" $1;}' | sh"]
          restartPolicy: OnFailure
```
