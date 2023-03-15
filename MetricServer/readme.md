**To deploy the Metrics Server**

Deploy the Metrics Server with the following command:  
```ruby
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```
 Since the metric server will not open properly, the following parameters must be added.
```ruby
kubectl edit -n kube-system deployments.apps metrics-server
```
```ruby
- args:
- --cert-dir=/tmp
- --secure-port=4443
- --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
- --kubelet-use-node-status-port
- --authorization-always-allow-paths=/livez,/readyz
- --kubelet-insecure-tls
image: k8s.gcr.io/metrics-server/metrics-server:v0.4.1
```
 Make sure metric-server pod is running
```ruby
kubectl get po -n kube-system
```
Check if metric server is running
```ruby
kubectl top nodes
```
