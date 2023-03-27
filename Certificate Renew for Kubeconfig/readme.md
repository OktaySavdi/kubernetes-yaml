### Backup old .kube folder
```
mv .kube/ .kube_backup
```
### Create new .kube folder
```
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config
```
### Create new certificate 
```
openssl genrsa -out kubernetes-admin.key 2048
openssl req -new -key kubernetes-admin.key -out kubernetes-admin.csr -subj "/CN=kubernetes-admin/O=system:masters"
openssl x509 -req -in kubernetes-admin.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out kubernetes-admin.crt -days 1080
```
### Add new certificate into the kubeconfig
```
kubectl config set-credentials kubernetes-admin --client-certificate=/root/kubernetes-admin.crt  --client-key=/root/kubernetes-admin.key
```
