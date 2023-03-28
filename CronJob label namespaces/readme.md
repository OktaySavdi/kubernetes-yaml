```yaml
kind: ServiceAccount
apiVersion: v1
metadata:
  name: label-job
  namespace: default
---
# 2. Create a role

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: label-ns-role
rules:
- apiGroups: [""]
  resources: ["namespaces"]
  verbs: ["get", "patch", "list", "update", "create"]
---
# 3. Attach the role to the service account

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: labelns-rb
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: label-ns-role
subjects:
- kind: ServiceAccount
  name: label-job
  namespace: default
---
# 4. Create a cronjob (with a crontab schedule) using the service account to check for completed jobs
apiVersion: batch/v1
kind: CronJob
metadata:
  name: jobs-labeling
  namespace: default
spec:
  schedule: '0 0 * * *'
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: label-job
          containers:
          - name: kubectl-container
            image: bitnami/kubectl:latest
            # I'm using bitnami kubectl, because the suggested kubectl image didn't had the `field-selector` option
            command: ["sh", "-c", "for i in $(kubectl get ns --show-labels --no-headers | awk '{print $1\",\"$4}' | grep -vE \"default|vmware-system-*|kube-system|kube-public|kube-node-lease|backup=true\");do kubectl label namespaces $(echo $i | cut -d, -f1) backup=true;done"]
          restartPolicy: OnFailure
```
