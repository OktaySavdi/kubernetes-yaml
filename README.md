

# Kubernetes CLI Commands

# CLI Example
```ruby
kubectl run nginx --image nginx --replicas=1 \
                  --port='8080' --requests 'memory=15Mi' \
                  --limits 'memory=20Mi' --restart Never \
                  --labels='app=nginx' --dry-run -o yaml \
                  --command -- sleep 1000
```
**ConfigMap**
```ruby
kubectl create configmap webapp-config-map
```
**Secret**
```ruby
kubectl create secret generic db-secret \
        --from-literal=DB_HOST=sql01 \
        --from-literal=DB_User=root \
        --from-literal=DB_Password=password123 
```
```ruby
kubectl create secret docker-registry private-reg-cred \
               --docker-username=dock_user \
               --docker-password=dock_password \
               --docker-server=myprivateregistry.com:5000 \
               --docker-email=dock_user@myprivateregistry.com
```

# json path

```ruby
kubectl get nodes node01 -o jsonpath='{.metadata.name}'

kubectl get nodes -o jsonpath='{.items[*].metadata.name}'

kubectl config view -o=jsonpath='{.users[*].name}'

kuconfig view --kubeconfig=my-kube-config -o jsonpath="{.users[*].name}"

kubectl get pv --sort-by=.spec.capacity.storage

kubectl get pv --sort-by=.spec.capacity.storage -o=custom-columns=NAME:.metadata.name,CAPACITY:.spec.capacity.storage 

kubectl config view --kubeconfig=my-kube-config -o jsonpath="{.contexts[?(@.context.user=='aws-user')].name}"
```

# Taint - Toleration
```ruby
kubectl taint nodes node-name key=value:taint-effect
kubectl taint nodes node-name app=blue:NoSchedule
```
```yaml
tolerations:
- key: "app"
  operator: "Equal"
  value: "blue"
  effect: "NoSchedule"
```
```ruby
kubectl taint nodes node1 key1=value1:NoSchedule
kubectl taint nodes node1 key1=value1:NoExecute
kubectl taint nodes node1 key2=value2:NoSchedule
```
**Example**
```
kubectl taint nodes node01 spray=mortein:NoSchedule
```
```yaml
tolerations:
- key: "spray"
  operator: "Equal"
  value: "mortein"
  effect: "NoSchedule"
```
**delete taint**
```ruby
kubectl taint node master node-role.kubernetes.io/master:NoSchedule-
```
# Node Selector
```ruby
kubectl label nodes node-1 size=Large
```
```yaml
nodeSelector:
 size: Large
```

# Affinity
**Available**
```
requiredDuringSchedulingIgnoredDuringExecution # does not assign if there is no matching node
```
```
preferredDuringSchedulingIgnoredDuringExecution # if there is no matching node, it makes an assignment
```
**Planning**
```
requiredDuringSchedulingRequiredDuringExecution
```
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: color
          operator: In
          values:
          - blue
```
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: node-role.kubernetes.io/master
          operator: Exists
```



# Static Pod

```ruby
kubectl run --restart=Never --image=busybox:1.28.4 \
            static-busybox --dry-run -o yaml \ 
            --command -- sleep 1000 > /etc/kubernetes/manifests/static-busybox.yaml
```
# Upgrade

```ruby
kubectl drain node01 --ignore-daemonsets --force  > takes maintenance mode. deletes every pod on it
```
```ruby
kubectl uncordon node01 > reactivates the node from maintenance mode. starts pod on it
```
```ruby
kubectl cordon node01  > run existing ones but not new pod
```
# Backup

```ruby
ETCDCTL_API=3 etcdctl snapshot save \
/tmp/snapshot-pre-boot.db \
--endpoints=https://[127.0.0.1]:2379 \
--cacert=/etc/kubernetes/pki/etcd/ca.crt \
--cert=/etc/kubernetes/pki/etcd/server.crt \
--key=/etc/kubernetes/pki/etcd/server.key
```
```ruby
ETCDCTL_API=3 etcdctl member list \
--endpoints=https://[127.0.0.1]:2379 \
--cacert=/etc/kubernetes/pki/etcd/ca.crt \
--cert=/etc/kubernetes/pki/etcd/server.crt \
--key=/etc/kubernetes/pki/etcd/server.key
```
# Restore

```ruby
ETCDCTL_API=3 etcdctl snapshot restore \
/tmp/snapshot-pre-boot.db \
--endpoints=https://[127.0.0.1]:2379 \
--cacert=/etc/kubernetes/pki/etcd/ca.crt \
--name=master --cert=/etc/kubernetes/pki/etcd/server.crt \
--key=/etc/kubernetes/pki/etcd/server.key \
--data-dir /var/lib/etcd-from-backup \
--initial-cluster=master=https://127.0.0.1:2380 \
--initial-cluster-token etcd-cluster-1 \
--initial-advertise-peer-urls=https://127.0.0.1:2380
```

# Certificate

```ruby
kubectl get csr 

kubectl certificate approve <cert-name>

kubectl certificate deny <cert-name>

kubectl delete csr <cert-name>
```

# Clusters info

```ruby
kubectl config view
```

# RBAC

```ruby
kubectl get roles --all-namespaces

kubectl get roles weave-net -n kube-system -o yaml

kubectl describe rolebindings weave-net -n kube-system
```

# Security Context

```yaml
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
```
