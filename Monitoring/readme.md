Repo : [URL](https://github.com/prometheus-operator/kube-prometheus)

### Step 1: Clone  **kube-prometheus**  project

Use  _git_  command to clone  _kube-prometheus_  project to your local system:

```
git clone https://github.com/prometheus-operator/kube-prometheus.git
```

Navigate to the  **_kube-prometheus_** directory:

```
cd kube-prometheus
```

### Step 2: Create monitoring namespace, CustomResourceDefinitions & operator pod

Create a namespace and required  _CustomResourceDefinitions_:

```
kubectl create -f manifests/setup
```

Command execution results as seen in the terminal screen.

```
namespace/monitoring created
customresourcedefinition.apiextensions.k8s.io/alertmanagerconfigs.monitoring.coreos.com created
customresourcedefinition.apiextensions.k8s.io/alertmanagers.monitoring.coreos.com created
customresourcedefinition.apiextensions.k8s.io/podmonitors.monitoring.coreos.com created
customresourcedefinition.apiextensions.k8s.io/probes.monitoring.coreos.com created
customresourcedefinition.apiextensions.k8s.io/prometheuses.monitoring.coreos.com created
customresourcedefinition.apiextensions.k8s.io/prometheusrules.monitoring.coreos.com created
customresourcedefinition.apiextensions.k8s.io/servicemonitors.monitoring.coreos.com created
customresourcedefinition.apiextensions.k8s.io/thanosrulers.monitoring.coreos.com created
clusterrole.rbac.authorization.k8s.io/prometheus-operator created
clusterrolebinding.rbac.authorization.k8s.io/prometheus-operator created
deployment.apps/prometheus-operator created
service/prometheus-operator created
serviceaccount/prometheus-operator created
```

```
$ kubectl get ns monitoring
NAME         STATUS   AGE
monitoring   Active   2m41s
```

Confirm that Prometheus operator pods are running:

```
$ kubectl get pods -n monitoring
NAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-84dc795dc8-jbgjm   2/2     Running   0          91s
```

### Step 3: Deploy Prometheus Monitoring Stack on Kubernetes

Once you confirm the Prometheus operator is running you can go ahead and deploy Prometheus monitoring stack.

```
kubectl create -f manifests/
```
Here is my deployment progress output:
```
poddisruptionbudget.policy/alertmanager-main created
prometheusrule.monitoring.coreos.com/alertmanager-main-rules created
secret/alertmanager-main created
service/alertmanager-main created
serviceaccount/alertmanager-main created
servicemonitor.monitoring.coreos.com/alertmanager created
clusterrole.rbac.authorization.k8s.io/blackbox-exporter created
clusterrolebinding.rbac.authorization.k8s.io/blackbox-exporter created
configmap/blackbox-exporter-configuration created
deployment.apps/blackbox-exporter created
service/blackbox-exporter created
serviceaccount/blackbox-exporter created
servicemonitor.monitoring.coreos.com/blackbox-exporter created
secret/grafana-datasources created
configmap/grafana-dashboard-alertmanager-overview created
configmap/grafana-dashboard-apiserver created
configmap/grafana-dashboard-cluster-total created
configmap/grafana-dashboard-controller-manager created
configmap/grafana-dashboard-k8s-resources-cluster created
configmap/grafana-dashboard-k8s-resources-namespace created
configmap/grafana-dashboard-k8s-resources-node created
configmap/grafana-dashboard-k8s-resources-pod created
configmap/grafana-dashboard-k8s-resources-workload created
configmap/grafana-dashboard-k8s-resources-workloads-namespace created
configmap/grafana-dashboard-kubelet created
configmap/grafana-dashboard-namespace-by-pod created
configmap/grafana-dashboard-namespace-by-workload created
configmap/grafana-dashboard-node-cluster-rsrc-use created
configmap/grafana-dashboard-node-rsrc-use created
configmap/grafana-dashboard-nodes created
configmap/grafana-dashboard-persistentvolumesusage created
configmap/grafana-dashboard-pod-total created
configmap/grafana-dashboard-prometheus-remote-write created
configmap/grafana-dashboard-prometheus created
configmap/grafana-dashboard-proxy created
configmap/grafana-dashboard-scheduler created
configmap/grafana-dashboard-workload-total created
configmap/grafana-dashboards created
deployment.apps/grafana created
service/grafana created
serviceaccount/grafana created
servicemonitor.monitoring.coreos.com/grafana created
prometheusrule.monitoring.coreos.com/kube-prometheus-rules created
clusterrole.rbac.authorization.k8s.io/kube-state-metrics created
clusterrolebinding.rbac.authorization.k8s.io/kube-state-metrics created
deployment.apps/kube-state-metrics created
prometheusrule.monitoring.coreos.com/kube-state-metrics-rules created
service/kube-state-metrics created
serviceaccount/kube-state-metrics created
servicemonitor.monitoring.coreos.com/kube-state-metrics created
prometheusrule.monitoring.coreos.com/kubernetes-monitoring-rules created
servicemonitor.monitoring.coreos.com/kube-apiserver created
servicemonitor.monitoring.coreos.com/coredns created
servicemonitor.monitoring.coreos.com/kube-controller-manager created
servicemonitor.monitoring.coreos.com/kube-scheduler created
servicemonitor.monitoring.coreos.com/kubelet created
clusterrole.rbac.authorization.k8s.io/node-exporter created
clusterrolebinding.rbac.authorization.k8s.io/node-exporter created
daemonset.apps/node-exporter created
prometheusrule.monitoring.coreos.com/node-exporter-rules created
service/node-exporter created
serviceaccount/node-exporter created
servicemonitor.monitoring.coreos.com/node-exporter created
clusterrole.rbac.authorization.k8s.io/prometheus-adapter created
clusterrole.rbac.authorization.k8s.io/system:aggregated-metrics-reader created
clusterrolebinding.rbac.authorization.k8s.io/prometheus-adapter created
clusterrolebinding.rbac.authorization.k8s.io/resource-metrics:system:auth-delegator created
clusterrole.rbac.authorization.k8s.io/resource-metrics-server-resources created
configmap/adapter-config created
deployment.apps/prometheus-adapter created
poddisruptionbudget.policy/prometheus-adapter created
rolebinding.rbac.authorization.k8s.io/resource-metrics-auth-reader created
service/prometheus-adapter created
serviceaccount/prometheus-adapter created
servicemonitor.monitoring.coreos.com/prometheus-adapter created
clusterrole.rbac.authorization.k8s.io/prometheus-k8s created
clusterrolebinding.rbac.authorization.k8s.io/prometheus-k8s created
prometheusrule.monitoring.coreos.com/prometheus-operator-rules created
servicemonitor.monitoring.coreos.com/prometheus-operator created
poddisruptionbudget.policy/prometheus-k8s created
prometheus.monitoring.coreos.com/k8s created
prometheusrule.monitoring.coreos.com/prometheus-k8s-prometheus-rules created
rolebinding.rbac.authorization.k8s.io/prometheus-k8s-config created
rolebinding.rbac.authorization.k8s.io/prometheus-k8s created
rolebinding.rbac.authorization.k8s.io/prometheus-k8s created
rolebinding.rbac.authorization.k8s.io/prometheus-k8s created
role.rbac.authorization.k8s.io/prometheus-k8s-config created
role.rbac.authorization.k8s.io/prometheus-k8s created
role.rbac.authorization.k8s.io/prometheus-k8s created
role.rbac.authorization.k8s.io/prometheus-k8s created
service/prometheus-k8s created
serviceaccount/prometheus-k8s created
servicemonitor.monitoring.coreos.com/prometheus-k8s created
```

Give it few seconds and the pods should start coming online. This can be checked with the commands below:

```
$ kubectl get pods -n monitoring
NAME                                   READY   STATUS    RESTARTS   AGE
alertmanager-main-0                    2/2     Running   0          113s
alertmanager-main-1                    2/2     Running   0          113s
alertmanager-main-2                    2/2     Running   0          113s
blackbox-exporter-6c95587d7-2vf28      3/3     Running   0          113s
grafana-9b54884bf-9s82l                1/1     Running   0          112s
kube-state-metrics-b545789dd-27xg4     3/3     Running   0          111s
node-exporter-cbjx5                    2/2     Running   0          111s
node-exporter-fs2vj                    2/2     Running   0          111s
node-exporter-gswkl                    2/2     Running   0          111s
node-exporter-hxv7l                    2/2     Running   0          111s
node-exporter-ktnd8                    2/2     Running   0          111s
prometheus-adapter-5c977869c-7mhz2     1/1     Running   0          111s
prometheus-adapter-5c977869c-8fndf     1/1     Running   0          111s
prometheus-k8s-0                       2/2     Running   1          109s
prometheus-k8s-1                       2/2     Running   1          109s
prometheus-operator-84dc795dc8-jbgjm   2/2     Running   0          7m37s
```
To list all the services created you’ll run the command:

```
$ kubectl get svc -n monitoring
NAME                    TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
alertmanager-main       ClusterIP   10.254.220.101   <none>        9093/TCP                     3m20s
alertmanager-operated   ClusterIP   None             <none>        9093/TCP,9094/TCP,9094/UDP   3m20s
blackbox-exporter       ClusterIP   10.254.41.39     <none>        9115/TCP,19115/TCP           3m20s
grafana                 ClusterIP   10.254.226.247   <none>        3000/TCP                     3m19s
kube-state-metrics      ClusterIP   None             <none>        8443/TCP,9443/TCP            3m19s
node-exporter           ClusterIP   None             <none>        9100/TCP                     3m18s
prometheus-adapter      ClusterIP   10.254.193.17    <none>        443/TCP                      3m18s
prometheus-k8s          ClusterIP   10.254.92.43     <none>        9090/TCP                     3m17s
prometheus-operated     ClusterIP   None             <none>        9090/TCP                     3m17s
prometheus-operator     ClusterIP   None             <none>        8443/TCP                     9m4s
```

### Step 4: Access Prometheus, Grafana, and Alertmanager dashboards

```
kubectl create ingress prometeus --class=nginx --rule="prometeus.mydomain.com/*=prometheus-k8s:9090"

kubectl create ingress grafana --class=nginx --rule="grafana.mydomain.com/*=grafana:3000"

kubectl create ingress alertmanager --class=nginx --rule="alertmanager.mydomain.com/*=alertmanager-main:9093"
```

Default Logins are:
```
Username: admin
Password: admin
```
You’re required to change the password on first login:

![image](https://user-images.githubusercontent.com/3519706/147210163-14780b89-d5c2-4876-a07d-c183057972c4.png)

![image](https://user-images.githubusercontent.com/3519706/147210234-824352bc-e19e-477b-92c9-26c0f6685cde.png)

### How to create kubernetes prometheus alert rules

We can modify the configuration file  `prometheus-rules.yaml`  present in prometheus-operator repo to re-create the configmap.

```
kubectl get cm -n monitoring | grep rulefile
prometheus-k8s-rulefiles-0                  1         40m
```
I have added the following section at end of the configuration file. Custom Rule - awesome-prometheus-alerts.grep.to/rules.html#kubernetes
```yaml
- name: KubernetesNodeReady
  rules:
  - alert: KubernetesNodeReady
    expr: kube_node_status_condition{condition="Ready",status="true"} == 0
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: Kubernetes Node ready (instance {{ $labels.instance }})
      description: "Node {{ $labels.node }} has been unready for a long time\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
```
Re-create the configmap
```
kubectl delete -f prometheus-rules.yaml
kubectl create -f prometheus-rules.yaml
prometheusrule "prometheus-k8s-rules" created
```

