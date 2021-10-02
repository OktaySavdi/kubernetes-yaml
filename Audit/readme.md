
### Implement Audit Policy Rules

1.  Edit the  `audit-policy`  rules file:
    
    ```bash
    sudo vi /etc/kubernetes/audit-policy.yaml
    ```
    
2.  Paste in the following YAML rule to log request and response bodies for namespace changes:
    
    ```yaml
    apiVersion: audit.k8s.io/v1
    kind: Policy
    rules:
    # Log request and response bodies for all changes to Namespaces.
    - level: RequestResponse
      resources:
      - group: ""
        resources: ["namespaces"]
    ```
    
3.  Skip a line and paste in the following rule to log only request bodies for Pod and Services changes in the  `web`  namespace:
    
    ```yaml
    # Log request bodies (but not response bodies) for changes to Pods and Services in the web Namespace.
    - level: Request
      resources:
      - group: ""
        resources: ["pods", "services"]
      namespaces: ["web"]
    ```
    
4.  Skip another line and paste in the following rule to log metadata for all changes to Secrets:
    
    ```yaml
    # Log metadata for all changes to Secrets.
    - level: Metadata
      resources:
      - group: ""
        resources: ["secrets"]
    ```
    
5.  Paste in the following catch-all rule to log metadata for all other requests:
    
    ```yaml
    # Create a catchall rule to log metadata for all other requests.
    - level: Metadata
    ```
    
6.  To save and exit the file, press  **Escape**, type  `:wq`, and hit  **Enter**.
    

### Configure Audit Logging

> **Note:**  kube-apiserver is already configured to mount both the audit policy file and the log output file.

1.  Edit the  `kube-apiserver`  manifest:
    
    ```bash
    sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
    ```
    ```bash
    /var/log/kubernetes
    ```
2.  Under the command-line arguments, add the  `audit-policy-file`  flag:
    
    ```yaml
    - command:
      - kube-apiserver
      - --audit-policy-file=/etc/kubernetes/audit-policy.yaml
    ```
    
3.  Add the output directory for the audit logs:
    
    ```yaml
      - --audit-log-path=/var/log/kubernetes/k8s-audit.log
    ```
    
4.  Configure the API server to keep old log files a maximum of 60 days with a maximum of only 1 old log file:
    
    ```yaml
    - --audit-log-maxage=60
    - --audit-log-maxbackup=1
    ```
    
5.  To save and exit the file, press  **Escape**, type  `:wq`, and hit  **Enter**.
    
6.  Once kube-apiserver has been re-created, check the nodes:
    
    ```
    kubectl get nodes
    ```
    
7.  View the audit logs:
    
    ```
    sudo tail -f /var/log/kubernetes/k8s-audit.log
    ```
