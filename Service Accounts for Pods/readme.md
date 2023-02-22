
Create service account
```
kubectl create sa build-robot
```
### Manually create a long-lived API token for a ServiceAccount
```shell
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: build-robot-secret
  annotations:
    kubernetes.io/service-account.name: build-robot
type: kubernetes.io/service-account-token
EOF
```
Add secret into the serviceaccount
```
kubectl patch serviceaccount build-robot -p '{"secrets": [{"name": "build-robot-secret"}]}'
```
If you view the Secret using:
```
kubectl get secret/build-robot-secret -o yaml
```

### Get the secret name of the created ServiceAccount that stores the token:
```
export TOKENNAME=$(kubectl -n kube-system get serviceaccount/<service-account-name> -o jsonpath='{.secrets[0].name}')
``` 
Get the token from the secret in base64, decode it and add to the  `TOKEN`  environment variable:
```
export TOKEN=$(kubectl -n kube-system get secret $TOKENNAME -o jsonpath='{.data.token}' | base64 --decode) 
```
Check the token health level, make a request to the Kubernetes API with the token in the  `"Authorization: Bearer <TOKEN-HERE>"`  header:
```
curl -k -H "Authorization: Bearer $TOKEN" -X GET "https://<KUBE-API-IP>:6443/api/v1/nodes" | json_pp
```
Add the service account to kubeconfig:
```
kubectl config set-credentials <service-account-name> --token=$TOKEN
```
Change the current context:
```
kubectl config set-context --current --user=<service-account-name>
```
Perform a health check:
```
kubectl get no
```                                                                                                      
The updated kubeconfig will be located in the  `$HOME/.kube/config`  home directory.
