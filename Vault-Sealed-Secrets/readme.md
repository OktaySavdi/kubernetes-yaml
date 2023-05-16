##### Download selaed-secrets binary file
```bash
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.21.0/kubeseal-0.21.0-linux-amd64.tar.gz[URL ](https://github.com/bitnami-labs/sealed-secrets)
tar -xvf kubeseal-0.21.0-linux-amd64.tar.gz
mv kubeseal /usr/local/bin/
```
##### The Sealed Secrets helm chart is now officially supported and hosted in this GitHub repo. ([URL](https://github.com/bitnami-labs/sealed-secrets))
```
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets -n kube-system --set-string fullnameOverride=sealed-secrets-controller sealed-secrets/sealed-secrets
```
You can ensure that the relevant Pod is running as expected by executing the following command:
```
kubectl get pods -n kube-system | grep sealed-secrets-controller
```

##### If you would rather not need access to the cluster to generate the sealed secret you can run:
```
kubeseal \
  --controller-name=sealed-secrets-controller \
  --controller-namespace=kube-system \
  --fetch-cert > mycert.pem
```
##### Create Secret 
```
kubectl create secret generic my-secret --from-literal=username=oktay --from-literal=password=123 --dry-run=client -o yaml > secret.yaml
```
```
kubeseal --cert=mycert.pem --format=yaml < secret.yaml > sealed-secret.yaml
```
The generated output will look something like this:

![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/ff97bf39-22e5-41c9-8058-7bcda8f3bfbd)

You can then proceed to review the secret and fetch its values.
```
kubectl get secret my-secret -o jsonpath="{.data.username}" | base64 --decode
kubectl get secret my-secret -o jsonpath="{.data.password}" | base64 --decode
```
![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/845b7115-1469-4952-8283-0963592d2056)
```
kubectl logs -n kube-system -f sealed-secrets-controller-56769c5b9f-58w2w
```
![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/21bd609c-e12a-4ea3-a1cb-fffe7d52a169)



