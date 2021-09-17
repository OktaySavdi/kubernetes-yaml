```yaml
apiVersion: v1
kind: Pod
metadata:
  name: fio-baseline
spec:
  nodeName: node01
  containers:
  - name: fio-write
    image: quay.io/oktaysavdi/alpine-fio
    args:
    - "sleep"
    - "100000"
````
