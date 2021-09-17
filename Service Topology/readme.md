#Enable Feature on kube-apiserver
```
--feature-gates=ServiceTopology=true,EndpointSlice=true
```
#Create application
```
kubectl create deployment web --image=nginx
```
#Expose service with topology

**Constraints**

 - Service topology is not compatible with `externalTrafficPolicy=Local`,   and therefore a Service cannot use both of these features. It is  possible to use both features in the same cluster on different Services, only not on the same Service.
   
 - Valid topology keys are currently limited to  `kubernetes.io/hostname`, `topology.kubernetes.io/zone`, and   `topology.kubernetes.io/region`, but will be generalized to other node labels in the future.

 - Topology keys must be valid label keys and at most 16 keys may be specified.
  
 - The catch-all value, `"*"`, must be the last value in the topology keys, if it is used.

```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: web
  name: web
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: web
  type: ClusterIP
  topologyKeys:
    - "kubernetes.io/hostname
 ```
```
kubectl get EndpointSlice -A
kubectl describe EndpointSlices web-gwdpt
``` 

![image](https://user-images.githubusercontent.com/3519706/133746112-c247fef2-5652-4ade-b3b7-5a0e5fecd437.png)
 
