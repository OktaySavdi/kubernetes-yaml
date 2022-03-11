In case of conjur token expires, no new token is created even if the container restarts.(due to using init container)

Since an init container is used, the pod must be restarted to get a new conjur token.

so you can use below method

```yaml
oc create sa mysa -n default
oc create clusterrole conjur-sa --resource=pods --verb=*
oc create clusterrolebinding conjur-sa --clusterrole=conjur-sa --serviceaccount=default:conjur-sa
```
```yaml
containers:
  - name: test-garanti
    env:
      - name: MY_POD_NAME
        valueFrom:
          fieldRef:
            apiVersion: v1
            fieldPath: metadata.name
    lifecycle:
      preStop:
        exec:
          command:
            - /bin/sh
            - '-c'
            - >
              export SCRIPT_NAMESPACE="my-namespace";
              export SCRIPT_SA_TOKEN="W91ZXZsczQifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ";
              export SCRIPT_POD_NAME=${MY_POD_NAME};
              export SCRIPT_API_URL="api.ocp.mycluster.local:6443";
              curl -k --header "Authorization: Bearer ${SCRIPT_SA_TOKEN}" --insecure --data '{"spec":{"activeDeadlineSeconds":1}}' -XPATCH   -H "Accept: application/json, */*" -H "Content-Type: application/strategic-merge-patch+json" https://${SCRIPT_API_URL}/api/v1/namespaces/${SCRIPT_NAMESPACE}/pods/${SCRIPT_POD_NAME}
```
