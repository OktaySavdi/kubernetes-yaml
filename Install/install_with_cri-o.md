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

### Step 1) Set Hostname and add entries in /etc/hosts file
```
hostnamectl set-hostname "k8s-master1"
exec bash
```
Similarly, run above command on remaining nodes and set their respective hostname. 
Once hostname is set on all master and worker nodes then add the following entries in **/etc/hosts** file on all the nodes.
```shell
echo "192.168.1.40   k8s-master1" | tee --append /etc/hosts    
echo "192.168.1.41   k8s-master2" | tee --append /etc/hosts
echo "192.168.1.42   k8s-master3" | tee --append /etc/hosts
echo "192.168.1.43   k8s-worker1" | tee --append /etc/hosts
echo "192.168.1.44   k8s-worker2" | tee --append /etc/hosts
echo "192.168.1.45   vip-k8s-master" | tee --append /etc/hosts
```
I have used one additional entry **192.168.1.45   vip-k8s-master** in host file because I will be using this IP and hostname while configuring the haproxy and keepalived on all master nodes. This IP will be used as **kube-apiserver load balancer ip**. All the kube-apiserver request will come to this IP and then the request will be distributed among backend actual kube-apiservers.

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
### Step 2) Install and Configure Keepalive and HAProxy on all master / control plane nodes

Install keepalived and haproxy on each master node using the following yum command,
```shell
yum install haproxy keepalived -y
```
Configure Keepalived on k8s-master1 first, create check_apiserver.sh script will the following content,
```shell
[kadmin@k8s-master1 ~]$ vi /etc/keepalived/check_apiserver.sh
```
```shell
#!/bin/sh
APISERVER_VIP=192.168.1.45
APISERVER_DEST_PORT=6443

errorExit() {
    echo "*** $*" 1>&2
    exit 1
}

curl --silent --max-time 2 --insecure https://localhost:${APISERVER_DEST_PORT}/ -o /dev/null || errorExit "Error GET https://localhost:${APISERVER_DEST_PORT}/"
if ip addr | grep -q ${APISERVER_VIP}; then
    curl --silent --max-time 2 --insecure https://${APISERVER_VIP}:${APISERVER_DEST_PORT}/ -o /dev/null || errorExit "Error GET https://${APISERVER_VIP}:${APISERVER_DEST_PORT}/"
fi
```
save and exit the file.

Set the executable permissions

Take the backup of keepalived.conf file and then truncate the file.
```shell
[kadmin@k8s-master1 ~]$ cp /etc/keepalived/keepalived.conf /etc/keepalived/keepalived.conf-org
[kadmin@k8s-master1 ~]$ sh -c '> /etc/keepalived/keepalived.conf'
```
Now paste the following contents to /etc/keepalived/keepalived.conf file
```shell
[kadmin@k8s-master1 ~]$ vi /etc/keepalived/keepalived.conf
```
```yaml
! /etc/keepalived/keepalived.conf
! Configuration File for keepalived
global_defs {
    router_id LVS_DEVEL
}
vrrp_script check_apiserver {
  script "/etc/keepalived/check_apiserver.sh"
  interval 3
  weight -2
  fall 10
  rise 2
}

vrrp_instance VI_1 {
    state MASTER
    interface enp0s3
    virtual_router_id 151
    priority 255
    authentication {
        auth_type PASS
        auth_pass P@##D321!
    }
    virtual_ipaddress {
        192.168.1.45/24
    }
    track_script {
        check_apiserver
    }
}
```
Save and close the file.

`Note:` Only two parameters of this file need to be changed for master-2 & 3 nodes. **State** will become **SLAVE** for master 2 and 3, priority will be 254 and 253 respectively.

Configure HAProxy on k8s-master1 node, edit its configuration file and add the following contents:
```shell
[kadmin@k8s-master1 ~]$ cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg-org
```
Remove all lines after default section and add following lines
```shell
[kadmin@k8s-master1 ~]$ vi /etc/haproxy/haproxy.cfg
```
```yaml
#---------------------------------------------------------------------
# apiserver frontend which proxys to the masters
#---------------------------------------------------------------------
frontend apiserver
    bind 192.168.1.45:6443
    mode tcp
    option tcplog
    default_backend apiserver
#---------------------------------------------------------------------
# round robin balancing for apiserver
#---------------------------------------------------------------------
backend apiserver
    option httpchk GET /healthz
    http-check expect status 200
    mode tcp
    option ssl-hello-chk
    balance     roundrobin
        server k8s-master1 192.168.1.40:6443 check
        server k8s-master2 192.168.1.41:6443 check
        server k8s-master3 192.168.1.42:6443 check
```
Save and exit the file

![image](https://user-images.githubusercontent.com/3519706/135464022-62ed3929-049c-40f7-bc00-51c1dc6cb2ed.png)

Now copy theses three files (**check_apiserver.sh , keepalived.conf** and **haproxy.cfg**) from k8s-master1 to k8s-master2 & 3

Run the following for loop to scp these files to master 2 and 3
```shell
[kadmin@k8s-master1 ~]$ for f in k8s-master2 k8s-master3 lb.example.com; do scp /etc/keepalived/check_apiserver.sh /etc/keepalived/keepalived.conf root@$f:/etc/keepalived; scp /etc/haproxy/haproxy.cfg root@$f:/etc/haproxy; done
```
**Note:** Don’t forget to change two parameters in keepalived.conf file that we discuss above for k8s-master2 & 3

In case firewall is running on master nodes then add the following firewall rules on all three master nodes
```shell
firewall-cmd --add-rich-rule='rule protocol value="vrrp" accept' --permanent
firewall-cmd --permanent --add-port=8443/tcp
firewall-cmd --reload
```
Now Finally start and enable keepalived and haproxy service on all three master nodes and lb.example.com using the following commands :
```shell
systemctl enable keepalived --now
systemctl enable haproxy --now
```
Once these services are started successfully, verify whether VIP (virtual IP) is enabled on k8s-master1 node because we have marked k8s-master1 as MASTER node in keepalived configuration file.

![image](https://user-images.githubusercontent.com/3519706/135464464-bd82f203-3e01-4f10-af62-7deecd1ff458.png)

Perfect, above output confirms that VIP has been enabled on k8s-master1.

### Step 3) Disable Swap, set SELinux as permissive and firewall rules for Master and worker nodes

Disable Swap Space on all the nodes including worker nodes, Run the following commands
```shell
swapoff -a 
sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
```
Set SELinux as Permissive on all master and worker nodes, run the following commands,
```shell
setenforce 0
sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
```
**Firewall Rules for Master Nodes:**

In case firewall is running on master nodes, then allow the following ports in the firewall,

![image](https://user-images.githubusercontent.com/3519706/135464784-694df33a-6a72-4113-9a4c-7763f62ddc07.png)

Run the following firewall-cmd command on all the master nodes,

```shell
firewall-cmd --permanent --add-port=6443/tcp
firewall-cmd --permanent --add-port=2379-2380/tcp
firewall-cmd --permanent --add-port=10250/tcp
firewall-cmd --permanent --add-port=10251/tcp
firewall-cmd --permanent --add-port=10252/tcp
firewall-cmd --permanent --add-port=179/tcp
firewall-cmd --permanent --add-port=4789/udp
firewall-cmd --reload


modprobe br_netfilter
sh -c "echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables"
sh -c "echo '1' > /proc/sys/net/ipv4/ip_forward"
```
**Firewall Rules for Worker nodes:**

In case firewall is running on worker nodes, then allow the following ports in the firewall on all the worker nodes

![image](https://user-images.githubusercontent.com/3519706/135464936-9c1a12ce-bf12-4cbe-8c04-c1e953f4957f.png)

Run the following commands on all the worker nodes,
```shell
firewall-cmd --permanent --add-port=10250/tcp
firewall-cmd --permanent --add-port=30000-32767/tcp                                                   
firewall-cmd --permanent --add-port=179/tcp
firewall-cmd --permanent --add-port=4789/udp
firewall-cmd --reload


modprobe br_netfilter
sh -c "echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables"
sh -c "echo '1' > /proc/sys/net/ipv4/ip_forward"
```
### Step 4) Install Container Run Time (CRI) CRI-O on Master & Worker Nodes

Install **CRI-O**(Container Run Time) on all the master nodes and worker nodes, run the following command,

Install and configure prerequisites:

Add centos repo
```shell
[extras]
name=CentOS-$releasever - Extras
mirrorlist=http://mirrorlist.centos.org/?release=7&arch=
$basearch&repo=extras
baseurl=http://mirror.centos.org/centos/7/extras/$basearch/
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
priority=1

[base]
name=CentOS-$releasever - Base
mirrorlist=http://mirrorlist.centos.org/?release=7&arch=
$basearch&repo=os
baseurl=http://mirror.centos.org/centos/7/os/$basearch/
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-5
priority=1

#released updates
[updates]
name=CentOS-$releasever - Updates
mirrorlist=http://mirrorlist.centos.org/?release=7&arch=
$basearch&repo=updates
baseurl=http://mirror.centos.org/centos/7/updates/$basearch/
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
priority=1
```
```shell
yum install yum-utils device-mapper-persistent-data lvm2 bash-completion -y
```
**letting ipTables see bridged networks**
```shell
cat <<EOF | tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF
```
**Create the .conf file to load the modules at bootup**
```shell
cat <<EOF | tee /etc/modules-load.d/crio.conf
overlay
br_netfilter
EOF
```
```shell
modprobe overlay
modprobe br_netfilter
```
***Set up required sysctl params, these persist across reboots.**
```shell
cat <<EOF | tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
```
```shell
sysctl --system
```
Now, let’s install kubeadm , kubelet and kubectl in the next step

### Step 5) Install Kubeadm, kubelet and kubectl

Install **kubeadm, kubelet** and **kubectl** on all master nodes as well as worker nodes. Before installing these packages first, we must configure Kubernetes repository, run the following command on each master and worker nodes,

```shell
cat <<EOF | tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-\$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kubelet kubeadm kubectl
EOF
```
**Install CRI-O binaries**

| Operating system | `$OS` |
|--|--|
| Centos 8 | `CentOS_8` |
| Centos 8 Stream| `CentOS_8_Stream` |
| Centos 7 | `CentOS_7` |

```shell
#set OS version
OS=CentOS_7

#set CRI-O
VERSION=1.22

curl -L -o /etc/yum.repos.d/devel:kubic:libcontainers:stable.repo https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/devel:kubic:libcontainers:stable.repo
curl -L -o /etc/yum.repos.d/devel:kubic:libcontainers:stable:cri-o:$VERSION.repo https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable:cri-o:$VERSION/$OS/devel:kubic:libcontainers:stable:cri-o:$VERSION.repo
yum install -y cri-o
```
**Install crictl**

crictl can be downloaded from cri-tools release page:
```shell
VERSION="v1.22.0"
wget https://github.com/kubernetes-sigs/cri-tools/releases/download/$VERSION/crictl-$VERSION-linux-amd64.tar.gz
sudo tar zxvf crictl-$VERSION-linux-amd64.tar.gz -C /usr/local/bin
rm -f crictl-$VERSION-linux-amd64.tar.gz
```
Now run below yum command to install these packages,
```shell
yum install -y kubelet-1.22.4-0 kubeadm-1.22.4-0 kubectl-1.22.4-0 --disableexcludes=kubernetes
```
Run following systemctl command to enable kubelet service on all nodes ( master and worker nodes)
```shell
systemctl enable kubelet --now
```
**Service enable**
```shell
systemctl daemon-reload
systemctl restart kubelet
systemctl status kubelet
systemctl enable crio
systemctl restart crio
systemctl status crio
```
**Add proxy configuration for container runtime**
```shell
vi /etc/systemd/system/multi-user.target.wants/crio.service
```
```shell
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:80"
Environment="HTTPS_PROXY=http://proxy.example.com:80"
Environment="NO_PROXY=localhost,127.0.0.0/8,docker-registry.somecorporation.com"
```

![image](https://user-images.githubusercontent.com/3519706/144755405-a1f9f946-9f5e-4fac-bd80-1561b0e21eb8.png)

**Service enable**
```shell
systemctl daemon-reload
systemctl restart kubelet
systemctl status kubelet
systemctl enable crio
systemctl restart crio
systemctl status crio
```
**Test cri-o**
```shell
crictl pull quay.io/oktaysavdi/istioproject
```
## Step 6) Initialize the Kubernetes Cluster from first master node

Now move to first master node / control plane and issue the following command,
```shell
[kadmin@k8s-master1 ~]$ kubeadm init --control-plane-endpoint="192.168.1.45:6443" --upload-certs --apiserver-advertise-address=192.168.1.40 --pod-network-cidr=192.168.0.0/16
```
In above command, apart from this ‘–upload-certs’ option will share the certificates among master nodes automatically

Output of kubeadm command would be something like below:

![image](https://user-images.githubusercontent.com/3519706/135467960-3545d78a-7992-4a53-a4b5-23dd18b6e852.png)

Great, above output confirms that Kubernetes cluster has been initialized successfully. In output we also got the commands for other master and worker nodes to join the cluster.

**Note:** It is recommended to copy this output to a text file for future reference.

Run following commands to allow local user to use kubectl command to interact with cluster,
```shell
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config
```
Now, Let’s deploy pod network (CNI – Container Network Interface), in my case I going to deploy calico addon as pod network, run following kubectl command
```shell
[kadmin@k8s-master1 ~]$ kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```
Once the pod network is deployed successfully, add remaining two master nodes to cluster. Just copy the command for master node to join the cluster from the output and paste it on k8s-master2 and k8s-master3, example is shown below
```shell
[kadmin@k8s-master2 ~]$ kubeadm join vip-k8s-master:6443 --token tun848.2hlz8uo37jgy5zqt  --discovery-token-ca-cert-hash sha256:d035f143d4bea38d54a3d827729954ab4b1d9620631ee330b8f3fbc70324abc5 --control-plane --certificate-key a0b31bb346e8d819558f8204d940782e497892ec9d3d74f08d1c0376dc3d3ef4
```
Output would be:

![image](https://user-images.githubusercontent.com/3519706/135479876-7acb7021-d731-4f44-b99e-4fa33693139e.png)

Also run the same command on k8s-master3,
```shell
[kadmin@k8s-master3 ~]$ kubeadm join vip-k8s-master:6443 --token tun848.2hlz8uo37jgy5zqt  --discovery-token-ca-cert-hash sha256:d035f143d4bea38d54a3d827729954ab4b1d9620631ee330b8f3fbc70324abc5 --control-plane --certificate-key a0b31bb346e8d819558f8204d940782e497892ec9d3d74f08d1c0376dc3d3ef4
```
Output would be:

![image](https://user-images.githubusercontent.com/3519706/135480002-becaaaac-cd3b-4de2-b6aa-aa9098f8b609.png)

Above output confirms that k8s-master3 has also joined the cluster successfully. Let’s verify the nodes status from kubectl command, go to master-1 node and execute below command,
```shell
[kadmin@k8s-master1 ~]$ kubectl get nodes
NAME           STATUS   ROLES    AGE     VERSION
k8s-master1   Ready    master   31m     v1.18.6
k8s-master2   Ready    master   10m     v1.18.6
k8s-master3   Ready    master   3m47s   v1.18.6
```
erfect, all our three master or control plane nodes are ready and join the cluster.

### Step 7) Join Worker nodes to Kubernetes cluster

To join worker nodes to cluster, copy the command for worker node from output and past it on both worker nodes, example is shown below:
```shell
[kadmin@k8s-worker1 ~]$ kubeadm join vip-k8s-master:6443 --token tun848.2hlz8uo37jgy5zqt --discovery-token-ca-cert-hash sha256:d035f143d4bea38d54a3d827729954ab4b1d9620631ee330b8f3fbc70324abc5

[kadmin@k8s-worker2 ~]$ kubeadm join vip-k8s-master:6443 --token tun848.2hlz8uo37jgy5zqt --discovery-token-ca-cert-hash sha256:d035f143d4bea38d54a3d827729954ab4b1d9620631ee330b8f3fbc70324abc5
```
Output would be something like below:

![image](https://user-images.githubusercontent.com/3519706/135480312-db4a0e0d-cc2c-4eb9-8112-a137f6086fe9.png)

Now head to k8s-master1 node and run below kubectl command to get status worker nodes,
```shell
[kadmin@k8s-master1 ~]$ kubectl get nodes
NAME           STATUS   ROLES    AGE     VERSION
k8s-master1   Ready    master   43m     v1.18.6
k8s-master2   Ready    master   21m     v1.18.6
k8s-master3   Ready    master   15m     v1.18.6
k8s-worker1   Ready    <none>   6m11s   v1.18.6
k8s-worker2   Ready    <none>   5m22s   v1.18.6
```
Above output confirms that both workers have also joined the cluster and are in ready state.

Run below command to verify the status infra pods which are deployed in kube-system namespace.
```shell
[kadmin@k8s-master1 ~]$ kubectl get pods -n kube-system
```
![image](https://user-images.githubusercontent.com/3519706/135480597-44696521-1a75-4448-b53f-bcc7cc1d8918.png)

## Step 8) Test Highly available Kubernetes cluster

Let’s try to connect to the cluster from remote machine (CentOS system) using load balancer dns name and port. On the remote machine first, we must install kubectl package. Run below command to set kubernetes repositories.

```shell
cat <<EOF | tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-\$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kubelet kubeadm kubectl
EOF
```
```shell
yum install -y  kubectl --disableexcludes=kubernetes
```
Now add following entry in /etc/host file,
```shell
192.168.1.45   vip-k8s-master
```
Create kube directory and copy /etc/kubernetes/admin.conf file from k8s-master1 node to $HOME/.kube/config ,
```shell
$ mkdir -p $HOME/.kube
$ scp root@192.168.1.40:/etc/kubernetes/admin.conf $HOME/.kube/config
$ chown $(id -u):$(id -g) $HOME/.kube/config
```
Now run “kubectl get nodes” command,
```shell
[kadmin@vip-k8s-master ~]$ kubectl get nodes
NAME           STATUS   ROLES    AGE    VERSION
k8s-master1   Ready    master   3h5m   v1.18.6
k8s-master2   Ready    master   163m   v1.18.6
k8s-master3   Ready    master   157m   v1.18.6
k8s-worker1   Ready    <none>   148m   v1.18.6
k8s-worker2   Ready    <none>   147m   v1.18.6
```
Let’s create a deployment with name nginx-lab with image ‘nginx’ and then expose this deployment as service of type “NodePort”
```shell
[kadmin@vip-k8s-master ~]$ kubectl create deployment nginx-lab --image=nginx
deployment.apps/nginx-lab created

[kadmin@vip-k8s-master ~]$ kubectl get deployments.apps nginx-lab
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
nginx-lab   1/1     1            1           59s

[kadmin@vip-k8s-master ~]$ kubectl get pods
NAME                         READY   STATUS    RESTARTS   AGE
nginx-lab-5df4577d49-rzv9q   1/1     Running   0          68s
test-844b65666c-pxpkh        1/1     Running   3          154m
```
Let’s try to scale replicas from 1 to 4, run the following command,
```shell
[kadmin@vip-k8s-master ~]$ kubectl scale deployment nginx-lab --replicas=4
deployment.apps/nginx-lab scaled

[kadmin@vip-k8s-master ~]$ kubectl get deployments.apps nginx-lab
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
nginx-lab   4/4     4            4           3m10s
```
Now expose the deployment as service, run
```
[kadmin@vip-k8s-master ~]$ kubectl expose deployment nginx-lab --name=nginx-lab --type=NodePort --port=80 --target-port=80
service/nginx-lab exposed
```
Get port details and try to access nginx web server using curl,
```shell
[kadmin@vip-k8s-master ~]$ kubectl get svc nginx-lab
NAME        TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
nginx-lab   NodePort   10.102.32.29   <none>        80:31766/TCP   60s
```
To access nginx web server we can use any master or worker node IP and port as “31766”
```shell
[kadmin@vip-k8s-master ~]$ curl http://192.168.1.44:31766
```
Output would be something like below:

![image](https://user-images.githubusercontent.com/3519706/135481304-989ed0da-621c-46cc-81a9-95c5c7d591c4.png)

Perfect, that’s confirm we have successfully deployed highly available Kubernetes cluster with kubeadm on CentOS 7 servers. Please don’t hesitate to share your valuable feedback and comments.

[+] reference : https://arabitnetwork.com/2021/02/20/install-kubernetes-with-cri-o-on-centos-7-step-by-step/
