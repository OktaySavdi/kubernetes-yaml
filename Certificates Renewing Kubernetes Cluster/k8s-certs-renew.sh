#!/bin/bash

echo "## Expiration before renewal ##"
/usr/local/bin/kubeadm certs check-expiration

echo "## Renewing certificates managed by kubeadm ##"
/usr/local/bin/kubeadm certs renew all

echo "## Restarting control plane pods managed by kubeadm ##"
/usr/bin/docker ps -af 'name=k8s_POD_(kube-apiserver|kube-controller-manager|kube-scheduler|etcd)-*' -q | /usr/bin/xargs /usr/bin/docker rm -f

echo "## Updating /root/.kube/config ##"
cp /etc/kubernetes/admin.conf /root/.kube/config

echo "## Waiting for apiserver to be up again ##"
until printf "" 2>>/dev/null >>/dev/tcp/127.0.0.1/6443; do sleep 1; done

echo "## Expiration after renewal ##"
/usr/local/bin/kubeadm certs check-expiration
