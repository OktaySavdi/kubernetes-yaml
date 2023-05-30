```yaml
kubectl create -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: trooubleshhoting
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
    command:
      - sleep
      - "infinity"
    imagePullPolicy: IfNotPresent
  restartPolicy: Always
EOF
```
