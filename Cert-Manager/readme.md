
## Procedure

To install cert-manager, complete the following steps:

1.  From the command-line interface, log in to your  Kubernetes  environment.
2.  Run the following command to install the cert-manager resources from a YAML manifest file on GitHub:
    
    ```plaintext
    kubectl apply -f https://github.com/jetstack/cert-manager/releases/latest/download/cert-manager.yaml
    ```
    
3.  To verify the installation, run the following command:
    
    ```plaintext
    kubectl get pods --namespace cert-manager
    ```
    
    The output should indicate that the cert-manager pods have a status of  `Running`.
    
4.  Run the following command to patch your deployment. Do not replace  `${POD_NAMESPACE}`  in this command; this value is referenced within the  cert-manager.yaml  file.
    
    ```plaintext
    kubectl patch deployment \
      cert-manager \
      --namespace cert-manager  \
      --type='json' \
      -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/args", "value": [
      "--v=2",
      "--cluster-resource-namespace=$(POD_NAMESPACE)",
      "--leader-election-namespace=kube-system",
      "--enable-certificate-owner-ref"
    ]}]'
    ```
    
    When the command completes, it adds a flag to ensure that any auto-generated secrets that store certificates are automatically removed when necessary.
