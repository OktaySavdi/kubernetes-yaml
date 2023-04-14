```yaml
apiVersion: v1
data:
  resolve-gt-domains.server: |
    mydomain1.com:53 {
        errors
        cache 30
        forward . 10.10.10.10 10.10.10.11 10.10.10.12
    }
    mydomain2.com:53 {
        errors
        cache 30
        forward . 10.10.10.10 10.10.10.11 10.10.10.12
    }
    mydomain3.com:53 {
        errors
        cache 30
        forward . 10.10.10.10 10.10.10.11 10.10.10.12
    }
    mydomain4.com:53 {
        errors
        cache 30
        forward . 10.10.10.10 10.10.10.11 10.10.10.12
    }
kind: ConfigMap
metadata:
  name: coredns-custom
  namespace: kube-system
```
