
# Kubernetes Dashboard with UnSecure

### Installation: [URL](https://github.com/kubernetes/dashboard)

### Dashboard arguments : [URL](https://github.com/kubernetes/dashboard/blob/master/docs/common/dashboard-arguments.md)

### Access-Control:  [URL](https://github.com/kubernetes/dashboard/tree/master/docs/user/access-control)


# Kubernetes Dashboard

Kubernetes Dashboard is a general purpose, web-based UI for Kubernetes clusters. It allows users to manage applications running in the cluster and troubleshoot them, as well as manage the cluster itself.

![image](https://user-images.githubusercontent.com/3519706/119263610-6e2a3a00-bbe8-11eb-95d5-b3c8f28db32a.png)

## Getting Started

**IMPORTANT:**  Read the  [Access Control](https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/README.md)  guide before performing any further steps. The default Dashboard deployment contains a minimal set of RBAC privileges needed to run.

### [](https://github.com/OktaySavdi/kubernetes-yaml/blob/master/Dashboard/recommended.yaml)Install

To deploy Dashboard, execute following command:
```
kubectl create -f recommended.yaml
```
**Referance:** 

[1] - https://github.com/kubernetes/dashboard
