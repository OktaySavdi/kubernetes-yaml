### # Install Prometheus AlertManager

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add prometheus-msteams https://prometheus-msteams.github.io/prometheus-msteams/
helm repo update
```
```
helm install prometheus-msteams --namespace kube-monitor --create-namespace -f Prometheus-MSteams.yaml prometheus-msteams/prometheus-msteams
helm install prometheus --namespace kube-monitor --create-namespace -f Prometheus.yaml prometheus-community/kube-prometheus-stack 
```
```
kubectl apply -f PrometheusRule.yaml
```
### # Update Prometheus AlertManager
```
helm repo update
```
```
helm upgrade prometheus-msteams -f Prometheus-MSteams.yaml prometheus-msteams/prometheus-msteams
helm upgrade prometheus -f Prometheus.yaml prometheus-community/kube-prometheus-stack 
```
### # Install Kwatch for Application Alerting

To deploy kwatch, execute following command:
```
kubectl apply -f kwatch.yaml
```
