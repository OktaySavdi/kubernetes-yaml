# kubernetes CertificateSigningRequest example

```yaml
apiVersion: certificates.k8s.io/v1beta1
kind: CertificateSigningRequest
metadata:
  name: oktay-access
spec:
  request: $(cat mycert.csr | base64 | tr -d '\n')
  usages:
  - client auth
```