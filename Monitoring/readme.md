Repo : [URL](https://github.com/prometheus-operator/kube-prometheus)

### Create the namespace and CRDs, and then wait for them to be available before creating the remaining resources
```yaml
git clone https://github.com/prometheus-operator/kube-prometheus.git
cd kube-prometheus
```
```
kubectl apply --server-side -f manifests/setup
until kubectl get servicemonitors --all-namespaces ; do date; sleep 1; echo ""; done
kubectl apply -f manifests/
```

We create the namespace and CustomResourceDefinitions first to avoid race conditions when deploying the monitoring components. Alternatively, the resources in both folders can be applied with a single command  `kubectl apply --server-side -f manifests/setup -f manifests`, but it may be necessary to run the command multiple times for all components to be created successfullly.


### Access the dashboards

```
kubectl create ingress prometeus --class=nginx --rule="prometeus.mydomain.com/*=prometheus-k8s:9090"

kubectl create ingress grafana --class=nginx --rule="grafana.mydomain.com/*=grafana:3000"

kubectl create ingress alertmanager --class=nginx --rule="alertmanager.mydomain.com/*=alertmanager-main:9093"
```
