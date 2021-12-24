
### Kubernetes install ingress controller

Nginx ingress controller install :  [URL](https://docs.nginx.com/nginx-ingress-controller/installation/installation-with-helm/)

Nginx ingress parameters : [URL](https://github.com/nginxinc/kubernetes-ingress/tree/master/deployments/helm-chart#configuration)

Taint worker node
```
kubectl taint node <Infra Node Name> node-role.kubernetes.io/infra=:NoSchedule
```
## Prerequisites

-   A  [Kubernetes Version Supported by the Ingress Controller](https://docs.nginx.com/nginx-ingress-controller/technical-specifications/#supported-kubernetes-versions)
-   Helm 3.0+.
-   Git.

## Getting the Chart Sources

This step is required if you’re installing the chart using its sources. Additionally, the step is also required for managing the custom resource definitions (CRDs), which the Ingress Controller requires by default, or for upgrading/deleting the CRDs.

1.  Clone the Ingress controller repo:
    
    ```fallback
    git clone https://github.com/nginxinc/kubernetes-ingress/
    ```
    
2.  Change your working directory to /deployments/helm-chart:
    
    ```fallback
    cd kubernetes-ingress/deployments/helm-chart
    git checkout v2.0.3    
    ```    

## Adding the Helm Repository

This step is required if you’re installing the chart via the helm repository.

```fallback
helm repo add nginx-stable https://helm.nginx.com/stable
helm repo update
```

## Installing the Chart

### Installing the CRDs

By default, the Ingress Controller requires a number of custom resource definitions (CRDs) installed in the cluster. The Helm client will install those CRDs. If the CRDs are not installed, the Ingress Controller pods will not become  `Ready`.

If you do not use the custom resources that require those CRDs (which corresponds to  `controller.enableCustomResources`  set to  `false`  and  `controller.appprotect.enable`  set to  `false`), the installation of the CRDs can be skipped by specifying  `--skip-crds`  for the helm install command.

### Installing via Helm Repository

To install the chart with the release name my-release (my-release is the name that you choose):

For NGINX Result with dry-run:

```fallback
helm install ingress-controller nginx-stable/nginx-ingress \
     --namespace ingress-controller --create-namespace \
     --set controller.service.type=ClusterIP \
     --set controller.setAsDefaultIngress=true \
     --set controller.kind=daemonset \
     --set controller.nodeSelector."node-role\.kubernetes\.io/infra"= \
     --set controller.tolerations[0].key='node-role.kubernetes.io/infra',controller.tolerations[0].effect='NoSchedule' --dry-run
```

For NGINX Apply:

```fallback
helm install ingress-controller nginx-stable/nginx-ingress \
     --namespace ingress-controller --create-namespace \
     --set controller.service.type=ClusterIP \
     --set controller.setAsDefaultIngress=true \
     --set controller.kind=daemonset \
     --set controller.nodeSelector."node-role\.kubernetes\.io/infra"= \
     --set controller.tolerations[0].key='node-role.kubernetes.io/infra',controller.tolerations[0].effect='NoSchedule'
```

### Check that the Ingress Controller is Running

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

## Upgrading the Chart

### Upgrading the CRDs

Helm does not upgrade the CRDs during a release upgrade. Before you upgrade a release, run the following command to upgrade the CRDs:

```fallback
kubectl apply -f crds/
```

> **Note**: The following warning is expected and can be ignored:  `Warning: kubectl apply should be used on resource created by either kubectl create --save-config or kubectl apply`.

> **Note**: Make sure to check the  [release notes](https://www.github.com/nginxinc/kubernetes-ingress/releases) for a new release for any special upgrade procedures.

### Upgrading the Release

To upgrade the release  `ingress-controller`:

#### Upgrade Using Chart Sources:[](https://docs.nginx.com/nginx-ingress-controller/installation/installation-with-helm/#upgrade-using-chart-sources "Upgrade Using Chart Sources:")

```fallback
helm upgrade ingress-controller .
```

#### Upgrade via Helm Repository:
```fallback
$ helm upgrade ingress-controller nginx-stable/nginx-ingress
```

## Uninstalling the Chart

### Uninstalling the Release

To uninstall/delete the release  `ingress-controller`:

```fallback
helm uninstall ingress-controller
```

The command removes all the Kubernetes components associated with the release.

### Uninstalling the CRDs

Uninstalling the release does not remove the CRDs. To remove the CRDs, run:

```fallback
kubectl delete -f crds/
```

> **Note**: This command will delete all the corresponding custom resources in your cluster across all namespaces. Please ensure there are no custom resources that you want to keep and there are no other Ingress Controller releases running in the cluster.
