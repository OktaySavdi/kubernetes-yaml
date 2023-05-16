
## Problem

We would like to watch if some change happens in  `ConfigMap`  and/or  `Secret`; then perform a rolling upgrade on relevant  `DeploymentConfig`,  `Deployment`,  `Daemonset`,  `Statefulset`  and  `Rollout`

## [](https://github.com/stakater/Reloader#solution)Solution

Reloader can watch changes in  `ConfigMap`  and  `Secret`  and do rolling upgrades on Pods with their associated  `DeploymentConfigs`,  `Deployments`,  `Daemonsets`  `Statefulsets`  and  `Rollouts`.

### Install Reloader
```
kubectl apply -f https://raw.githubusercontent.com/stakater/Reloader/master/deployments/kubernetes/reloader.yaml
```

## How to use Reloader

For a  `Deployment`  called  `foo`  have a  `ConfigMap`  called  `foo-configmap`  or  `Secret`  called  `foo-secret`  or both. Then add your annotation (by default  `reloader.stakater.com/auto`) to main metadata of your  `Deployment`
```yaml
kind: Deployment
metadata:
  annotations:
    reloader.stakater.com/auto: "true"
spec:
  template:
    metadata:
```
This will discover deploymentconfigs/deployments/daemonsets/statefulset/rollouts automatically where  `foo-configmap`  or  `foo-secret`  is being used either via environment variable or from volume mount. And it will perform rolling upgrade on related pods when  `foo-configmap`  or  `foo-secret`are updated.

You can restrict this discovery to only  `ConfigMap`  or  `Secret`  objects that are tagged with a special annotation. To take advantage of that, annotate your deploymentconfigs/deployments/daemonsets/statefulset/rollouts like this:
```yaml
kind: Deployment
metadata:
  annotations:
    reloader.stakater.com/search: "true"
spec:
  template:
```
and Reloader will trigger the rolling upgrade upon modification of any  `ConfigMap`  or  `Secret`  annotated like this:
```yaml
kind: ConfigMap
metadata:
  annotations:
    reloader.stakater.com/match: "true"
data:
  key: value
```

### Configmap

To perform rolling upgrade when change happens only on specific configmaps use below annotation.

For a  `Deployment`  called  `foo`  have a  `ConfigMap`  called  `foo-configmap`. Then add this annotation to main metadata of your  `Deployment`
```yaml
kind: Deployment
metadata:
  annotations:
    configmap.reloader.stakater.com/reload: "foo-configmap"
spec:
  template:
    metadata:
```
Use comma separated list to define multiple configmaps.
```yaml
kind: Deployment
metadata:
  annotations:
    configmap.reloader.stakater.com/reload: "foo-configmap,bar-configmap,baz-configmap"
spec:
  template: 
    metadata:
```
### [](https://github.com/stakater/Reloader#secret)Secret

To perform rolling upgrade when change happens only on specific secrets use below annotation.

For a  `Deployment`  called  `foo`  have a  `Secret`  called  `foo-secret`. Then add this annotation to main metadata of your  `Deployment`
```yaml
kind: Deployment
metadata:
  annotations:
    secret.reloader.stakater.com/reload: "foo-secret"
spec:
  template: 
    metadata:
```
Use comma separated list to define multiple secrets.
```yaml
kind: Deployment
metadata:
  annotations:
    secret.reloader.stakater.com/reload: "foo-secret,bar-secret,baz-secret"
spec:
  template: 
    metadata:
```


### NOTES

-   Reloader also supports  [sealed-secrets](https://github.com/bitnami-labs/sealed-secrets).  [Here](https://github.com/stakater/Reloader/blob/master/docs/Reloader-with-Sealed-Secrets.md)  are the steps to use sealed-secrets with reloader.
-   For  [rollouts](https://github.com/argoproj/argo-rollouts/)  reloader simply triggers a change is up to you how you configure the rollout strategy.
-   `reloader.stakater.com/auto: "true"`  will only reload the pod, if the configmap or secret is used (as a volume mount or as an env) in  `DeploymentConfigs/Deployment/Daemonsets/Statefulsets`
-   `secret.reloader.stakater.com/reload`  or  `configmap.reloader.stakater.com/reload`  annotation will reload the pod upon changes in specified configmap or secret, irrespective of the usage of configmap or secret.
-   you may override the auto annotation with the  `--auto-annotation`  flag
-   you may override the search annotation with the  `--auto-search-annotation`  flag and the match annotation with the  `--search-match-annotation`  flag
-   you may override the configmap annotation with the  `--configmap-annotation`  flag
-   you may override the secret annotation with the  `--secret-annotation`  flag
-   you may want to prevent watching certain namespaces with the  `--namespaces-to-ignore`  flag
-   you may want to watch only a set of namespaces with certain labels by using the  `--namespace-selector`  flag
-   you may want to watch only a set of secrets/configmaps with certain labels by using the  `--resource-label-selector`  flag
-   you may want to prevent watching certain resources with the  `--resources-to-ignore`  flag
-   you can configure logging in JSON format with the  `--log-format=json`  option
-   you can configure the "reload strategy" with the  `--reload-strategy=<strategy-name>`  option (details below)
