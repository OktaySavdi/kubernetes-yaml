![image](https://user-images.githubusercontent.com/3519706/147205106-a847721d-e250-4979-9755-731754734a8f.png)

# Kubernetes CLI Commands

**kubeadm**
```ruby
kubeadm token generate
kubeadm token create <generated-token> --print-join-command --ttl=0

kubeadm init phase upload-certs --upload-certs

kubeadm join 10.10.10.10:6443 --token < token > --discovery-token-ca-cert-hash sha256:< hash> --control-plane --certificate-key < upload_certs>
```
**Call DNS**
```ruby
<service-name>.<namespace>.svc.cluster.local:<service-port>
<pod-ip-address>.<namespace>.pod.cluster.local:<service-port>
```

**CLI Example**
```ruby
kubectl run nginx --image nginx --replicas=1 \
                  --port='8080' --requests 'memory=15Mi' \
                  --limits 'memory=20Mi' --restart Never \
                  --labels='app=nginx' --dry-run -o yaml \
                  --command -- sleep 1000
```
**CERT**
```
kubeadm alpha certs check-expiration
```
**ConfigMap**
```ruby
kubectl create configmap webapp-config-map
# file
kubectl create configmap propsfilecm --from-file=application.properties
kubectl create configmap myconfig --from-file=example-files/game.properties --from-file=example-files/ui.properties

# Value
kubectl create configmap myconfig --from-literal=special.how=very --from-literal=special.type=charm

# Volume
kubectl set volume dc/map --add --name=v1 --type=configmap --configmap-name='myconfig' --mount-path=/data
kubectl set volumes dc/myapp --add --overwrite=true --name=configmap-volume --mount-path=/data -t configmap --configmap-name=propsfilecm

kubectl set volume dc/<DC-NAME> -t configmap --name trusted-ca --add --read-only=true --mount-path /etc/pki/ca-trust/extracted/pem --configmap-name <CONFIGMAP-NAME>

# Env
kubectl set env --from=configmap/deneme dc/map
```
**secret**
```ruby
kubectl create secret generic db-secret \
        --from-literal=DB_HOST=sql01 \
        --from-literal=DB_User=root \
        --from-literal=DB_Password=password123 
```
```ruby
kubectl create secret generic mycert.certs \
        --from-file=mycert.crt=/tmp/mycert.crt \
        --from-file=mycert.key=/tmp/mycert.key
```
```ruby
kubectl create secret docker-registry private-reg-cred \
               --docker-username=dock_user \
               --docker-password=dock_password \
               --docker-server=myprivateregistry.com:5000 \
               --docker-email=dock_user@myprivateregistry.com
```
```ruby
# Generic
kubectl create secret generic oia-secret --from-literal=username=myuser --from-literal=password=mypassword
kubectl create secret generic test-secret --from-literal=username='my-app' --from-literal=password='39528$vdg7Jb'

# Env
kubectl set env --from=secret/test-secret dc/map

# Volume
kubectl set volume rc/r1 --add --name=v1 --type=secret --secret-name='secret1' --mount-path=/data
kubectl set volumes dc/myapp --add --name=secret-volume --mount-path=/opt/app-root/ --secret-name=oia-secret
```
**Process**
```ruby
kubectl process -f /yaml/myexample.yaml --parameters

kubectl process -f /yaml/myexample.yaml -p SERVICE_NAME=servismesh -p PROJECT=myproject -p SERVICE_PORT=8080 -p HOSTNAME=myap.com

for i in `kubectl get ns | awk '{print $1}'`; do kubectl process -f /yaml/myexample.yaml -p NAMESPACE=${i} | kubectl create -f - ; done
```
**Probe**
```ruby
kubectl set probe deployment/hello-node --readiness --get-url=http://:8766/actuator/health --timeout-seconds=1 --initial-delay-seconds=15 --liveness --get-url=http://:8766/actuator/health --timeout-seconds=1 --initial-delay-seconds=15
```
**Create and add a Persistent Volume**
```
kubectl set volume dc/name-of-your-app-here --add --name=storage --type='persistentVolumeClaim' --claim-class='standard' --claim-name='storage' --claim-size='10Gi' --mount-path=/var/www/html

kubectl set volume -f dc.json --add --name=v1 --type=persistentVolumeClaim --claim-name=pvc1 --mount-path=/data --containers=c1
```
**Token**
```ruby
kubectl create serviceaccount robot
kubectl policy add-role-to-user admin system:serviceaccount:test:robot
kubectl serviceaccounts get-token robot

SERVER=`cat .kube/config | grep server | sed 's/server: //g'`
TOKEN=$(kubectl get secret $(kubectl get sa deploy -o jsonpath='{.secrets[0].name}') -o jsonpath='{.data.token}' | base64 --decode )

URL="$SERVER/api/v1/nodes"

curl -H "Authorization: Bearer $TOKEN" $URL --insecure
```
**Rollout-Rollback**
```ruby
kubectl rollout latest dc/example
kubectl rollout status deployment example --timeout 90s
kubectl set image deployment/example MyContainerName=quay.io/oktaysavdi/istioproject:v2
kubectl rollout history deployment example
kubectl rollout undo deployment example
kubectl rollout history deployment example --revision=2
kubectl rollout undo deployment example  --to-revision=3
```
# Cheat Sheet
```ruby
# Use the --v flag to set a verbosity level.
kubectl get pods --v=8

# Delete Evicted pods
kubectl get pod  | grep Evicted | awk '{print $1}' | xargs oc delete pod

# Delete Failed pods
kubectl delete $(oc get pods --field-selector=status.phase=Failed -o name -n cluster-management) -n cluster-management

kubectl get pods --field-selector=status.phase=Running

kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName,NAMESPACE:.metadata.namespace --all-namespaces

source <(kubectl completion bash) # setup autocomplete in bash into the current shell, bash-completion package should be installed first.
echo "source <(kubectl completion bash)" >> ~/.bashrc # add autocomplete permanently to your bash shell.

# use multiple kubeconfig files at the same time and view merged config
KUBECONFIG=~/.kube/config:~/.kube/kubconfig2 

kubectl config view

kubectl config get-contexts                           # display list of contexts 
kubectl config current-context                        # display the current-context
kubectl config use-context my-cluster-name            # set the default context to my-cluster-name
kubectl config set-context --current --namespace=MyNS # permanently save the namespace for all subsequent kubectl commands in that context.
kubectl config use-context <cluster>                  # Set the default context to <cluster>
kubectl config set-credentials <username> [options]   # Sets a user entry in kubeconfig
kubectl config view -o jsonpath='{.users[?(@.name == "admin")].user.password}' # Get the password for the "admin" user
kubectl config set-credentials <user> --client-key=~/.kube/admin.key # Sets a user with a client key
kubectl config set-credentials --username=<username> --password=<password> # Sets a user with basic auth
kubectl config set-credentials <user> --client-certificate=<path/to/cert> --embed-certs=true # Sets a user with client certificate
kubectl config --kubeconfig=<config/path> use-context <cluster> # Set a context utilizing a specific config file
kubectl config set-context gce --user=cluster-admin --namespace=foo && kubectl config use-context gce # Set a context utilizing a specific username and namespace

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

# add env to nginx-app
kubectl set env deployment/nginx-app  DOMAIN=cluster

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

# change pod image version
kubectl patch dc nginx --patch='{"spec":{"template":{"spec":{"containers":[{"name": "nginx", "image":"nginx:1.19.1"}]}}}}'

# Add a new element to a positional array
kubectl patch sa default --type='json' -p='[{"op": "add", "path": "/secrets/1", "value": {"name": "whatever" } }]'

# expose a port through with a service
kubectl expose deployment nginx-app --port=80 --name=nginx-http

# login inside pod
kubectl exec -ti nginx-app-5jyvm -- /bin/sh

# Scale pods
kubectl scale replicaset myfirstreplicaset --replicas=3

# You do not have to wait until the entire log of the pod’s container is printed out — just use --tail
kubectl -n my-namespace logs -f my-pod --tail=50

# Here is how you can print all the logs from all containers of a pod
kubectl -n my-namespace logs -f my-pod --all-containers

# Getting logs of the “previous” container
kubectl -n my-namespace logs my-pod --previous

# Getting logs of multi pod
kubectl logs -f deployment/myapp -c myapp --tail 100
kubectl logs -f deployment/app

kubectl logs -l app=myapp -c myapp --tail 100
kubectl logs -l app=myapp
```
**Kubernetes API**
```ruby
# Use the `kubectl proxy` command to proxy local requests on port 8001 to the Kubernetes API:
kubectl proxy --port=8001

# Send a `GET` request to the Kubernetes API using `curl`:
curl -X GET http://localhost:8001

# Send a `GET` request to list all pods in the environment:
curl -X GET http://localhost:8001/api/v1/pods

# Use `jq` to parse the json response:
curl -X GET http://localhost:8001/api/v1/pods | jq .items[].metadata.name

# We can scope the response by only viewing all pods in a particular namespace:
curl -X GET http://localhost:8001/api/v1/namespaces/myproject/pods

# Get more details on a particular pod within the `myproject` namespace:
curl -X GET http://localhost:8001/api/v1/namespaces/myproject/pods/my-two-container-pod

# Patch the current pod with a newer container image (`1.15`):
curl -X PATCH http://localhost:8001/api/v1/namespaces/myproject/pods/my-two-container-pod -H "Content-type: application/strategic-merge-patch+json" -d '{"spec":{"containers":[{"name": "server","image":"nginx:1.15-alpine"}]}}'

# Delete the current pod by sending the `DELETE` request method:
curl -X DELETE http://localhost:8001/api/v1/namespaces/myproject/pods/my-two-container-pod

# Verify the pod no longer exists:
curl -X GET http://localhost:8001/api/v1/namespaces/myproject/pods/my-two-container-pod

# The `kubectl scale` command interacts with the `/scale` endpoint:
curl -X GET http://localhost:8001/apis/apps/v1/namespaces/myproject/replicasets/myfirstreplicaset/scale

# Use the `PUT` method against the `/scale` endpoint to change the number of replicas to 5
curl -X PUT localhost:8001/apis/apps/v1/namespaces/myproject/replicasets/myfirstreplicaset/scale -H "Content-type: application/json" -d '{"kind":"Scale","apiVersion":"autoscaling/v1","metadata":{"name":"myfirstreplicaset","namespace":"myproject"},"spec":{"replicas":5}}'

# You can also get information regarding the pod by using the `GET` method against the `/status` endpoint
curl -X GET http://localhost:8001/apis/apps/v1/namespaces/myproject/replicasets/myfirstreplicaset/status
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

# You can get internal IP addresses of cluster nodes
kubectl get nodes -o json | jq -r '.items[].status.addresses[]? | select (.type == "InternalIP") | .address' |   paste -sd "\n" -
 
# You can print all services and their respective nodePorts:
kubectl get --all-namespaces svc -o json | jq -r '.items[] | [.metadata.name,([.spec.ports[].nodePort | tostring ] | join("|"))]| @tsv'

# Pod subnets that are used in the cluster
kubectl get nodes -o jsonpath='{.items[*].spec.podCIDR}' | tr " " "\n

# get imagepullpolicy
kubectl get deploy --no-headers -A -o jsonpath='{range .items[*]}''NS:{.metadata.namespace}{"\t"}APP:{.metadata.name}{"\t"}UnavailableReplicas:{.status.unavailableReplicas}{"\t"}''image:{.spec.template.spec.containers[*].image}{"\t"}Policy:{.spec.template.spec.containers[*].imagePullPolicy}{"\n"}'
```
**Cluster**
```ruby
kubectl config view
kubectl cluster-info                                                  # Display addresses of the master and services
kubectl cluster-info dump                                             # Dump current cluster state to stdout
kubectl cluster-info dump --output-directory=/path/to/cluster-state   # Dump current cluster state to /path/to/cluster-state
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
kubectl taint nodes node1 key2=value2:PreferNoSchedule
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
![image](https://user-images.githubusercontent.com/3519706/110210363-5a512080-7ea2-11eb-94b3-e1656901d31e.png)

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
# ETCD
```ruby
ETCDCTL_API=3 etcdctl endpoint status --cluster --write-out=table \
--cacert /etc/kubernetes/pki/etcd/ca.crt \
--cert /etc/kubernetes/pki/etcd/server.crt \
--key /etc/kubernetes/pki/etcd/server.key 
```
```ruby
ETCDCTL_API=3 etcdctl member list --write-out table \
--cacert /etc/kubernetes/pki/etcd/ca.crt \
--cert /etc/kubernetes/pki/etcd/server.crt \
--key /etc/kubernetes/pki/etcd/server.key 
```
```ruby
ETCDCTL_API=3 etcdctl endpoint health --cluster \
--cacert /etc/kubernetes/pki/etcd/ca.crt \
--cert /etc/kubernetes/pki/etcd/server.crt \
--key /etc/kubernetes/pki/etcd/server.key
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

```ruby
KEY="/registry/deployments/kube-system/coredns"
kubectl exec -it etcd-controlplane -- sh -c "ETCDCTL_API=3 etcdctl \
--endpoints https://127.0.0.1:2379 \
--cacert /etc/kubernetes/pki/etcd/ca.crt \
--key /etc/kubernetes/pki/etcd/server.key \
--cert /etc/kubernetes/pki/etcd/server.crt \
get \"$KEY\" -w json" | jq '.kvs[0].value' | cut -d'"' -f2 | base64 --decode
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
