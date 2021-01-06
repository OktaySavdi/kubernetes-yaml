## Kubernetes Upgrade

check kubernetes version

```shell
kubectl get nodes
```
![image](https://user-images.githubusercontent.com/3519706/103744377-bd434a00-500e-11eb-93ba-8097543de772.png)

**Master Node**

Find the latest stable 1.19 version:
```ruby
centos : yum update -y
ubuntu : apt update && apt-cache madison kubeadm
centos : yum list --showduplicates kubeadm --disableexcludes=kubernetes
```
 On your first control plane node, upgrade kubeadm:
 ```ruby
ubuntu : apt-get update && apt-get install -y --allow-change-held-packages kubeadm=1.19.x-00
centos : yum install -y kubeadm-1.19.x-0 --disableexcludes=kubernetes
```
Verify that the download works and has the expected version:
 ```ruby
kubeadm version
```
On the control plane node, run:
 ```ruby
kubeadm upgrade plan
```
Drain master node for upgrade
 ```ruby
kubectl drain controlplane --ignore-daemonsets
```
Choose a version to upgrade to, and run the appropriate command. For example:
 ```ruby
kubeadm upgrade apply v1.19.6
```
Upgrade the kubelet and kubectl on all master nodes:
 ```ruby
ubuntu : apt-mark unhold kubelet kubectl && apt-get update && apt-get install -y kubelet=1.19.6-00 kubectl=1.19.6-00 && apt-mark hold kubelet kubectl
centos : yum install -y kubelet-1.19.x-0 kubectl-1.19.x-0 --disableexcludes=kubernetes
```
Restart the kubelet
 ```ruby
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```
Bring the node back online by marking it schedulable:
 ```ruby
kubectl uncordon master01
```

**Worker Node** 

Find the latest stable 1.19 version:
 ```ruby
ubuntu : apt update && apt-cache madison kubeadm
centos : yum update -y
```
 On your first worker node, upgrade kubeadm:
 ```ruby
ubuntu : apt-get update && apt-get install -y --allow-change-held-packages kubeadm=1.19.6-00
centos : yum install -y kubeadm-1.19.x-0 --disableexcludes=kubernetes
```
Verify that the download works and has the expected version:
 ```ruby
kubeadm version
```
Drain worker node for upgrade
 ```ruby
kubectl drain worker
```
Same as the first control plane node but use:
 ```ruby
kubeadm upgrade node
```
Upgrade the kubelet and kubectl on all worker nodes:
 ```ruby
ubuntu : apt-get update && apt-get install -y --allow-change-held-packages kubelet=1.19.6-00 kubectl=1.19.6-00
centos : yum install -y kubelet-1.19.x-0 kubectl-1.19.x-0 --disableexcludes=kubernetes
```
Restart the kubelet
 ```ruby
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```
Bring the node back online by marking it schedulable:
 ```ruby
kubectl uncordon worker01
```

# Verify the status of the cluster

After the kubelet is upgraded on all nodes verify that all nodes are available again by running the following command from anywhere kubectl can access the cluster:

```shell
kubectl get nodes
```
![image](https://user-images.githubusercontent.com/3519706/103744243-82d9ad00-500e-11eb-9d7c-6ebb0639ccd8.png)

The `STATUS` column should show `Ready` for all your nodes, and the version number should be updated.

## Recovering from a failure state[](https://v1-19.docs.kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/#recovering-from-a-failure-state)

If  `kubeadm upgrade`  fails and does not roll back, for example because of an unexpected shutdown during execution, you can run  `kubeadm upgrade`  again. This command is idempotent and eventually makes sure that the actual state is the desired state you declare.

To recover from a bad state, you can also run  `kubeadm upgrade apply --force`  without changing the version that your cluster is running.

During upgrade kubeadm writes the following backup folders under  `/etc/kubernetes/tmp`:

-   `kubeadm-backup-etcd-<date>-<time>`
-   `kubeadm-backup-manifests-<date>-<time>`

![image](https://user-images.githubusercontent.com/3519706/103744214-735a6400-500e-11eb-8fe3-2734362726f6.png)

`kubeadm-backup-etcd`  contains a backup of the local etcd member data for this control-plane Node. In case of an etcd upgrade failure and if the automatic rollback does not work, the contents of this folder can be manually restored in  `/var/lib/etcd`. In case external etcd is used this backup folder will be empty.

`kubeadm-backup-manifests`  contains a backup of the static Pod manifest files for this control-plane Node. In case of a upgrade failure and if the automatic rollback does not work, the contents of this folder can be manually restored in  `/etc/kubernetes/manifests`. If for some reason there is no difference between a pre-upgrade and post-upgrade manifest file for a certain component, a backup file for it will not be written.
