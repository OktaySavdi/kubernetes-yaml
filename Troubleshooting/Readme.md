```yaml
kubectl create -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: troubleshooting
  namespace: default
spec:
  containers:
  - name: dnsutils
    image: quay.io/oktaysavdi/rhel-tools
    command:
      - sleep
      - "infinity"
    imagePullPolicy: IfNotPresent
  restartPolicy: Always
EOF
```
-------
```yaml
kubectl create -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: dnsutils
  namespace: default
spec:
  containers:
  - name: dnsutils
    image: quay.io/oktaysavdi/dnsutils
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
      runAsGroup: 10000
      runAsNonRoot: true
      runAsUser: 10000
      seccompProfile:
        type: RuntimeDefault
    command:
      - sleep
      - "infinity"
    imagePullPolicy: IfNotPresent
  restartPolicy: Always
EOF
```
