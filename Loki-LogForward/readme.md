Add repos
```
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```
First let’s download the default chart values for every chart and make the necessary changes
```
helm install prometheus --namespace kube-monitoring --create-namespace prometheus-community/kube-prometheus-stack 
helm upgrade --install loki grafana/loki-distributed -n kube-monitoring --create-namespace
```
Loki values are now set, let’s install it and move to Promtail:
```
helm show values grafana/promtail > promtail-overrides.yaml
```
![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/4485cab2-e7ed-45ea-ba94-87048db4b9d8)
```
clients:
    - url: http://**loki-loki-distributed-gateway**.kube-monitoring.svc.cluster.local/loki/api/v1/push
```
```
helm upgrade --install --values promtail-overrides.yaml promtail grafana/promtail -n kube-monitoring
```
Configure Grafana Data Sources & Dashboard
```
kubectl get secret prometheus-grafana -o jsonpath='{.data.admin-password}' | base64 -d
```
We are now in. As next we need to add Grafana Loki as a data source:

![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/34c77a41-25b5-4588-bc27-258bf5ac0f18)

![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/ece1ea8a-10c5-42fd-9e97-ecc6970fb648)

![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/0662a250-9688-4147-ae1f-b906ade83654)
```
http://loki-loki-distributed-gateway.kube-monitoring.svc.cluster.local
```
Copy the dashboard template ID from the web page:
```
https://grafana.com/grafana/dashboards/15141-kubernetes-service-logs/

![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/9c8c089f-fee4-4a94-892c-25f7df23ddb7)
```
and in your Grafana environment, choose to Import a new Dashboard:

![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/93a2ba15-cd30-49ff-b3dd-d9ff1bf167ae)

Paste the template ID we just acquired and load the dashboard:

![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/f2be78e6-543a-4395-a5e8-60bd30f8ad7d)

Now all the puzzle pieces should come together and you should be able to see logs from your Kubernetes workloads directly into your Grafana interface as an almost real-time experience:

![image](https://github.com/OktaySavdi/kubernetes-yaml/assets/3519706/b1ac5115-7dda-4dae-8f39-0910f160122f)




