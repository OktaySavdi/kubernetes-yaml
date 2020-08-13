

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
**Rollout-Rollback**
```ruby
kubectl rollout latest dc/example
kubectl rollout status deployment example
kubectl set image deployment/example MyContainerName=quay.io/oktaysavdi/istioproject:v2
kubectl rollout history deployment example
kubectl rollout undo deployment example
kubectl rollout history deployment example --revision=2
kubectl rollout undo deployment example  --to-revision=3
```
# Cheat Sheet

```ruby
oc get pods --field-selector=status.phase=Running

kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName,NAMESPACE:.metadata.namespace --all-namespaces

source <(kubectl completion bash) # setup autocomplete in bash into the current shell, bash-completion package should be installed first.
echo "source <(kubectl completion bash)" >> ~/.bashrc # add autocomplete permanently to your bash shell.

# use multiple kubeconfig files at the same time and view merged config
KUBECONFIG=~/.kube/config:~/.kube/kubconfig2 

kubectl config view

kubectl config get-contexts                          # display list of contexts 
kubectl config current-context                       # display the current-context
kubectl config use-context my-cluster-name           # set the default context to my-cluster-name

# Get commands with basic output
kubectl get services                          # List all services in the namespace
kubectl get pods --all-namespaces             # List all pods in all namespaces
kubectl get pods -o wide                      # List all pods in the current namespace, with more details
kubectl get deployment my-dep                 # List a particular deployment
kubectl get pods                              # List all pods in the namespace
kubectl get pod my-pod -o yaml                # Get a pod's YAML

# List Services Sorted by Name
kubectl get services --sort-by=.metadata.name

# List pods Sorted by Restart Count
kubectl get pods --sort-by='.status.containerStatuses[0].restartCount'

# List PersistentVolumes sorted by capacity
kubectl get pv --sort-by=.spec.capacity.storage

# Get the version label of all pods with label app=cassandra
kubectl get pods --selector=app=cassandra -o \
  jsonpath='{.items[*].metadata.labels.version}'

# Get all worker nodes (use a selector to exclude results that have a label
# named 'node-role.kubernetes.io/master')
kubectl get node --selector='!node-role.kubernetes.io/master'

# Get all running pods in the namespace
kubectl get pods --field-selector=status.phase=Running

# Partially update a node
kubectl patch node k8s-node-1 -p '{"spec":{"unschedulable":true}}'

# Update a container's image; spec.containers[*].name is required because it's a merge key
kubectl patch pod valid-pod -p '{"spec":{"containers":[{"name":"kubernetes-serve-hostname","image":"new image"}]}}'

# Update a container's image using a json patch with positional arrays
kubectl patch pod valid-pod --type='json' -p='[{"op": "replace", "path": "/spec/containers/0/image", "value":"new image"}]'

# Disable a deployment livenessProbe using a json patch with positional arrays
kubectl patch deployment valid-deployment  --type json   -p='[{"op": "remove", "path": "/spec/template/spec/containers/0/livenessProbe"}]'

# Add a new element to a positional array
kubectl patch sa default --type='json' -p='[{"op": "add", "path": "/secrets/1", "value": {"name": "whatever" } }]'

kubectl cluster-info                                                  # Display addresses of the master and services
kubectl cluster-info dump                                             # Dump current cluster state to stdout
kubectl cluster-info dump --output-directory=/path/to/cluster-state   # Dump current cluster state to /path/to/cluster-state
```

# jsonpath

```ruby
kubectl get nodes node01 -o jsonpath='{.metadata.name}'

kubectl get nodes -o jsonpath='{.items[*].metadata.name}'

kubectl config view -o=jsonpath='{.users[*].name}'

kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="InternalIP")].address}'

kubectl get secret elasticsearch-es-elastic-user -o=jsonpath='{.data.elastic}' | base64 --decode

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
