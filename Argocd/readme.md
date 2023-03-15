# ARGOCD Multi Cluster Configuration
```
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install gitops --namespace=gitops argo/argo-cd --create-namespace
```
### Change svc type
```
kubectl patch svc gitops-argocd-server -p '{"spec": {"type": "LoadBalancer" }}'
```
### Get UI password
```
kubectl get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
```
### Login to the argocd server from CLI using the following command:
```
argocd login <address> --username admin --password <password>
``` 
### We will then extract the context name from cluster kubeconfig to
```
kubectl config get-contexts -o name
```
### Create a service account token Secret in the kube-system namespace, making sure that the annotation refers to the argocd-manager service account;
```
kubectl get sa -n kube-system | grep argo
```  
```
cat <<EOF | kubectl create -f-
apiVersion: v1
kind: Secret
metadata:
  annotations:
    kubernetes.io/service-account.name: argocd-manager
  name: argocd-manager-token
  namespace: kube-system
type: kubernetes.io/service-account-token
EOF
```
```
kubectl patch -n kube-system serviceaccount argocd-manager -p '{"secrets": [{"name": "argocd-manager-token"}]}'
```
### Add cluster the new cluster argocd-cluster by adding the context to Argocd using the following command in Argo CLI
```
argocd cluster add gitops-hce-admin --namespace argocd --name gitops-hce
```
