### How to Setup Kubernetes(k8s) Cluster in HA with Kubeadm

When we setup Kubernetes (k8s) cluster on-premises for production environment then it is recommended to deploy it in high availability. Here high availability means installing Kubernetes master or control plane in HA. In this article I will demonstrate how to setup setup Kubernetes(k8s) cluster in HA (High Availability) with kubeadm utility.

For the demonstration, I have used five CentOS 7 systems with following details:

```shell
k8s-master1 – Minimal CentOS 7 – 192.168.1.40 – 2GB RAM, 2vCPU, 40 GB Disk
k8s-master2 – Minimal CentOS 7 – 192.168.1.41 – 2GB RAM, 2vCPU, 40 GB Disk
k8s-master3 – Minimal CentOS 7 – 192.168.1.42 – 2GB RAM, 2vCPU, 40 GB Disk
k8s-worker1 – Minimal CentOS 7 – 192.168.1.43 – 2GB RAM, 2vCPU, 40 GB Disk
k8s-worker2 – Minimal CentOS 7 – 192.168.1.44 – 2GB RAM, 2vCPU, 40 GB Disk
vip-k8s-master - Minimal CentOS 7 – 192.168.1.45 – 2GB RAM, 2vCPU, 40 GB Disk
```

![image](https://user-images.githubusercontent.com/3519706/135461223-d7c619a1-f17e-4ccd-b199-70dca3f592fb.png)

Note: etcd cluster can also be formed outside of master nodes but for that we need additional hardware, so I am installing etcd inside my master nodes.

Minimum requirements for setting up Highly K8s cluster

 - Install **Kubeadm, kubelet** and **kubectl** on all master and worker Nodes
 - Network Connectivity among master and worker nodes 
 - Internet Connectivity on all the nodes 
 - Root credentials or sudo privileges user on all nodes 
 
Let’s jump into the installation and configuration

**Deploy ssh key from LB server to all nodes**
```shell
ssh-keygen
```
```shell
for host in 192.168.1.40 \
            192.168.1.41 \
            192.168.1.42 \
            192.168.1.43 \
            192.168.1.44 \
do ssh-copy-id -i ~/.ssh/id_rsa.pub $host; \
done
```
**install package on vip-k8s-master**
```shell
Ansible v2.9.x, Jinja 2.11+ and python-netaddr
yum install python-netaddr git -y
wget https://download-ib01.fedoraproject.org/pub/epel/7/x86_64/Packages/a/ansible-2.9.25-1.el7.noarch.rpm
rpm -ivh ansible-2.9.25-1.el7.noarch.rpm
install python3-pip -y
```
**Install requirements**
```shell
git clone https://github.com/kubernetes-sigs/kubespray.git
# Install dependencies from ``requirements.txt``
pip3 install -r requirements.txt
```
**Copy ``inventory/sample`` as ``inventory/mycluster``**
```shell
cp -rfp inventory/sample inventory/mycluster
```
**Update Ansible inventory file with inventory builder**
```shell
declare -a IPS=(192.168.1.40 192.168.1.41 192.168.1.42 192.168.1.43 192.168.1.44)
CONFIG_FILE=inventory/mycluster/hosts.yaml python3 contrib/inventory_builder/inventory.py ${IPS[@]}
```
**Review and change parameters under ``inventory/mycluster/group_vars``**
```shell
cat inventory/mycluster/group_vars/all/all.yml
cat inventory/mycluster/group_vars/k8s_cluster/k8s-cluster.yml
```
```shell
vi inventory/mycluster/hosts.yaml
vi roles/bootstrap-os/tasks/main.yml //change redhat yaml
```
```shell
vi inventory/mycluster/group_vars/all/all.yml
```
```shell
apiserver_loadbalancer_domain_name: "lb-kube.example.com"
loadbalancer_apiserver:
   address: 192.168.1.45
   port: 6443
loadbalancer_apiserver_localhost: false
```
```shell
#vi /etc/hosts
10.175.10.98  lb-kube.example.com
```
```shell
vi roles/container-engine/docker/templates/http-proxy.conf.j2
```
```shell
[Service]
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/bin/containerd
Environment="HTTP_PROXY=http://proxy.example.com:80"
Environment="HTTPS_PROXY=http://proxy.example.com:80"
Environment="NO_PROXY=localhost,127.0.0.0/8,docker-registry.somecorporation.com"
```
```shell
vi inventory/mycluster/group_vars/k8s_cluster/k8s-cluster.yml
```
```shell
kube_encrypt_secret_data: true
cluster_name: savdi-cluster.local
kubernetes_audit: true
podsecuritypolicy_enabled: true
```
```shell
vi inventory/mycluster/group_vars/k8s_cluster/addons.yml
```
```shell
dashboard_enabled: true
helm_enabled: true
metrics_server_enabled: true
```
Run Playbook
```
ansible-playbook -i inventory/mycluster/hosts.yaml  --become --become-user=root cluster.yml
```
**bastion**
```
mkdir .kube
scp root@192.168.1.40:/etc/kubernetes/admin.conf ~/.kube/config
```
