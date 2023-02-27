

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
Create Custom Cluster Role
```
kubectl create -f deployment-role.yaml
```
Create Custom Cluster Rolebinding
```
kubectl create clusterrolebinding custom-role --clusterrole=custom-edit --serviceaccount=default:build-robot
```
Check permission
```
kubectl auth can-i --list --as=system:serviceaccount:<namespace>:<serviceaccount> -n <namespace>
kubectl auth can-i get pods --as=system:serviceaccount:<namespace>:<serviceaccount> -n <namespace>
kubectl auth can-i delete deployments --as=system:serviceaccount:<namespace>:<serviceaccount> -n <namespace>  
kubectl auth can-i create sa --as=system:serviceaccount:<namespace>:<serviceaccount> -n <namespace>  

kubectl auth can-i --list --as=system:serviceaccount:default:build-robot -n app
kubectl auth can-i get pods --as=system:serviceaccount:default:build-robot -n app
kubectl auth can-i delete deployments --as=system:serviceaccount:default:build-robot -n app
```

### Get the secret name of the created ServiceAccount that stores the token:
```
export TOKENNAME=$(kubectl -n default get serviceaccount/build-robot -o jsonpath='{.secrets[0].name}')
``` 
Get the token from the secret in base64, decode it and add to the  `TOKEN`  environment variable:
```
export TOKEN=$(kubectl -n default get secret $TOKENNAME -o jsonpath='{.data.token}' | base64 --decode) 
```
Check the token health level, make a request to the Kubernetes API with the token in the  `"Authorization: Bearer <TOKEN-HERE>"`  header:
```
export APISERVER=$(kubectl config view -o jsonpath="{.clusters[?(@.name==\"<Cluster_Name>\")].cluster.server}")
curl -ks -H "Authorization: Bearer $TOKEN" -X GET $APISERVER/api/v1/namespaces | jq -r '.items[].metadata.name'
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
Check Service Account Token
```
kubectl exec -it <pod_name> -- ls /var/run/secrets/kubernetes.io/serviceaccount/token
```
