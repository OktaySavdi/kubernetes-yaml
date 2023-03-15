### Kubernetes install ingress controller

Nginx ingress controller install :  [URL](https://docs.nginx.com/nginx-ingress-controller/installation/installation-with-manifests/)

**Taint worker node**
```
kubectl taint node <Infra Node Name> node-role.kubernetes.io/infra=:NoSchedule
```
## Prerequisites

1.  Make sure you have access to the Ingress controller image:
    -   For NGINX Ingress controller, use the image  `nginx/nginx-ingress`  from  [DockerHub](https://hub.docker.com/r/nginx/nginx-ingress).
    -   It is also possible to build your own image and push it to your private Docker registry by following the instructions from  [here](https://docs.nginx.com/nginx-ingress-controller/installation/building-ingress-controller-image).
2.  Clone the Ingress controller repo and change into the deployments folder:
    
```fallback
git clone https://github.com/nginxinc/kubernetes-ingress/
cd kubernetes-ingress/deployments
git checkout v2.0.3
```
    

## 1. Configure RBAC

1.  Create a namespace and a service account for the Ingress controller:
    
    ```fallback
    kubectl apply -f common/ns-and-sa.yaml
    ```
    
2.  Create a cluster role and cluster role binding for the service account:
    
    ```fallback
    kubectl apply -f rbac/rbac.yaml
    ```
    
3.  (App Protect only) Create the App Protect role and role binding:
    
    ```fallback
    kubectl apply -f rbac/ap-rbac.yaml    
    ```
    

**Note**: To perform this step you must be a cluster admin. Follow the documentation of your Kubernetes platform to configure the admin access. For GKE, see the  [Role-Based Access Control](https://cloud.google.com/kubernetes-engine/docs/how-to/role-based-access-control)  doc.

## 2. Create Common Resources

In this section, we create resources common for most of the Ingress Controller installations:

1.  Create a secret with a TLS certificate and a key for the default server in NGINX:
    
    ```fallback
    kubectl apply -f common/default-server-secret.yaml
    
    ```
    
    **Note**: The default server returns the Not Found page with the 404 status code for all requests for domains for which there are no Ingress rules defined. For testing purposes we include a self-signed certificate and key that we generated. However, we recommend that you use your own certificate and key.
    
2.  Create a config map for customizing NGINX configuration:
    
    ```fallback
    kubectl apply -f common/nginx-config.yaml    
    ```
    
3.  Create an IngressClass resource:

if you want to set automatic ingress class, change ingress-class.yaml file like below
````
vi common/ingress-class.yaml    
````
![image](https://user-images.githubusercontent.com/3519706/146514391-236cc11b-0910-465c-9372-373ded8b2f4e.png)
    
```fallback
kubectl apply -f common/ingress-class.yaml    
```
    
 If you would like to set the Ingress Controller as the default one, uncomment the annotation  `ingressclass.kubernetes.io/is-default-class`. With this annotation set to true all the new Ingresses without an ingressClassName field specified will be assigned this IngressClass.
    
 **Note**: The Ingress Controller will fail to start without an IngressClass resource.
    

### Create Custom Resources

> **Note**: By default, it is required to create custom resource definitions for VirtualServer, VirtualServerRoute, TransportServer and Policy. Otherwise, the Ingress Controller pods will not become  `Ready`. If you’d like to disable that requirement, configure  [`-enable-custom-resources`](https://docs.nginx.com/nginx-ingress-controller/configuration/global-configuration/command-line-arguments#cmdoption-global-configuration)  command-line argument to  `false`  and skip this section.

1.  Create custom resource definitions for  [VirtualServer and VirtualServerRoute](https://docs.nginx.com/nginx-ingress-controller/configuration/virtualserver-and-virtualserverroute-resources),  [TransportServer](https://docs.nginx.com/nginx-ingress-controller/configuration/transportserver-resource)  and  [Policy](https://docs.nginx.com/nginx-ingress-controller/configuration/policy-resource)  resources:
    
    ```fallback
    kubectl apply -f common/crds/k8s.nginx.org_virtualservers.yaml
    kubectl apply -f common/crds/k8s.nginx.org_virtualserverroutes.yaml
    kubectl apply -f common/crds/k8s.nginx.org_transportservers.yaml
    kubectl apply -f common/crds/k8s.nginx.org_policies.yaml    
    ```
    

If you would like to use the TCP and UDP load balancing features of the Ingress Controller, create the following additional resources:

1.  Create a custom resource definition for  [GlobalConfiguration](https://docs.nginx.com/nginx-ingress-controller/configuration/global-configuration/globalconfiguration-resource)  resource:
    
    ```fallback
    kubectl apply -f common/crds/k8s.nginx.org_globalconfigurations.yaml
    ```
    

> **Feature Status**: The TransportServer, GlobalConfiguration and Policy resources are available as a preview feature: it is suitable for experimenting and testing; however, it must be used with caution in production environments. Additionally, while the feature is in preview, we might introduce some backward-incompatible changes to the resources specification in the next releases.

### Resources for NGINX App Protect

If you would like to use the App Protect module, create the following additional resources:

1.  Create a custom resource definition for  `APPolicy`,  `APLogConf`  and  `APUserSig`:
    
    ```fallback
    kubectl apply -f common/crds/appprotect.f5.com_aplogconfs.yaml
    kubectl apply -f common/crds/appprotect.f5.com_appolicies.yaml
    kubectl apply -f common/crds/appprotect.f5.com_apusersigs.yaml    
    ```
    

## 3. Deploy the Ingress Controller

We include two options for deploying the Ingress controller:

-   _Deployment_. Use a Deployment if you plan to dynamically change the number of Ingress controller replicas.
-   _DaemonSet_. Use a DaemonSet for deploying the Ingress controller on every node or a subset of nodes.

> Before creating a Deployment or Daemonset resource, make sure to update the  [command-line arguments](https://docs.nginx.com/nginx-ingress-controller/configuration/global-configuration/command-line-arguments)  of the Ingress Controller container in the corresponding manifest file according to your requirements.

### 3.1 Run the Ingress Controller
    
-   _Use a DaemonSet_: When you run the Ingress Controller by using a DaemonSet, Kubernetes will create an Ingress controller pod on every node of the cluster.
    
    **See also:**  See the Kubernetes  [DaemonSet docs](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)  to learn how to run the Ingress controller on a subset of nodes instead of on every node of the cluster.
    
  Set toleration and node selector for infra nodes, edit:
 ```
vi daemon-set/nginx-ingress.yaml
```
```yaml
spec:
nodeSelector:
  node-role.kubernetes.io/infra: ''
tolerations:
- key: "node-role.kubernetes.io/infra"
  effect: "NoSchedule"
 ``` 
  
```fallback
kubectl apply -f daemon-set/nginx-ingress.yaml
``` 

### 3.2 Check that the Ingress Controller is Running

Run the following command to make sure that the Ingress controller pods are running:

```fallback
kubectl get pods --namespace=nginx-ingress
```
create a example ingress yaml file
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: istio-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: "istio-10-10-10-10.nip.io"
    http:
      paths:
      - path: /istio
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 8080
```
